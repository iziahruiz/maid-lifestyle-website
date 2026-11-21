/*
 * Maid Lifestyle — private photo upload service
 * ------------------------------------------------------------
 * A small password-protected page where the owner uploads job photos.
 * Photos are resized in her browser (location/EXIF data stripped), then this
 * server commits them to the website's GitHub repo and asks Render to redeploy
 * the public site. No dependencies — Node 18+ only.
 *
 * Environment variables (set in the Render dashboard — never commit them):
 *   ADMIN_PASSWORD      required  the owner's upload password (12+ characters)
 *   GITHUB_TOKEN        required  fine-grained token: ONLY this repo, Contents = Read and write
 *   GITHUB_REPO         optional  default "iziahruiz/maid-lifestyle-website"
 *   GITHUB_BRANCH       optional  default "main"
 *   RENDER_DEPLOY_HOOK  optional  the public site's Deploy Hook URL (redeploys after each change)
 *   SESSION_SECRET      optional  random string; if unset one is generated at startup
 */
"use strict";
const http = require("http");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 10000;
const PASSWORD = process.env.ADMIN_PASSWORD || "";
const TOKEN = process.env.GITHUB_TOKEN || "";
const REPO = process.env.GITHUB_REPO || "iziahruiz/maid-lifestyle-website";
const BRANCH = process.env.GITHUB_BRANCH || "main";
const DEPLOY_HOOK = process.env.RENDER_DEPLOY_HOOK || "";
const SECRET = process.env.SESSION_SECRET || crypto.randomBytes(32).toString("hex");
const GH = process.env.GITHUB_API || "https://api.github.com";
const DATA_PATH = "assets/data/gallery-uploads.json";
const IMG_DIR = "assets/img/uploads";
const CATS = ["kitchen", "bathroom", "living", "bedroom", "deep", "beforeafter"];
const SESSION_HOURS = 12;
const MAX_BODY = 8 * 1024 * 1024; // 8 MB JSON (two resized JPEGs)
const PAGE = fs.readFileSync(path.join(__dirname, "page.html"), "utf8");

if (PASSWORD.length < 12) console.warn("WARNING: ADMIN_PASSWORD missing or shorter than 12 characters — logins are disabled.");
if (!TOKEN) console.warn("WARNING: GITHUB_TOKEN missing — uploads are disabled.");

/* ---------------- sessions & login protection ---------------- */
const sign = (v) => crypto.createHmac("sha256", SECRET).update(v).digest("hex");
function makeSession() {
  const exp = Date.now() + SESSION_HOURS * 3600e3;
  const v = exp + "." + crypto.randomBytes(16).toString("hex");
  return v + "." + sign(v);
}
function validSession(req) {
  const m = /(?:^|;\s*)ml_session=([^;]+)/.exec(req.headers.cookie || "");
  if (!m) return false;
  const parts = m[1].split(".");
  if (parts.length !== 3) return false;
  const v = parts[0] + "." + parts[1];
  const a = Buffer.from(sign(v)), b = Buffer.from(parts[2]);
  return a.length === b.length && crypto.timingSafeEqual(a, b) && Number(parts[0]) > Date.now();
}
function passwordOk(given) {
  if (PASSWORD.length < 12 || typeof given !== "string") return false;
  const a = crypto.createHash("sha256").update(given).digest();
  const b = crypto.createHash("sha256").update(PASSWORD).digest();
  return crypto.timingSafeEqual(a, b);
}
const fails = new Map(); // ip -> {n, until}
function clientIp(req) { return (req.headers["x-forwarded-for"] || "").split(",")[0].trim() || req.socket.remoteAddress; }
function lockedOut(ip) { const f = fails.get(ip); return f && f.n >= 5 && f.until > Date.now(); }
function noteFail(ip) {
  const f = fails.get(ip) || { n: 0, until: 0 };
  if (f.until < Date.now()) f.n = 0;
  f.n++; f.until = Date.now() + 15 * 60e3; fails.set(ip, f);
}

/* ---------------- http helpers ---------------- */
const SEC_HEADERS = {
  "X-Robots-Tag": "noindex, nofollow",
  "X-Frame-Options": "DENY",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "no-referrer",
  "Cache-Control": "no-store",
  "Content-Security-Policy": "default-src 'self'; img-src 'self' blob: data: https://maid-lifestyle.onrender.com; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; form-action 'self'",
};
function send(res, code, body, type = "application/json") {
  res.writeHead(code, { "Content-Type": type, ...SEC_HEADERS });
  res.end(typeof body === "string" ? body : JSON.stringify(body));
}
function readJson(req) {
  return new Promise((resolve, reject) => {
    const tooBig = () => Object.assign(new Error("Upload too large"), { code: 413 });
    if (Number(req.headers["content-length"]) > 4 * MAX_BODY) { req.resume(); return reject(tooBig()); } // absurd sizes: refuse at once
    let size = 0, over = false; const chunks = [];
    req.on("data", (c) => { size += c.length; if (size > MAX_BODY) over = true; else chunks.push(c); }); // keep draining so we can reply cleanly
    req.on("end", () => { if (over) return reject(tooBig()); try { resolve(JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}")); } catch { reject(Object.assign(new Error("Bad request"), { code: 400 })); } });
    req.on("error", reject);
  });
}
function sameOrigin(req) {
  const o = req.headers.origin;
  if (!o) return true; // non-browser or same-origin navigation; cookie is SameSite=Strict anyway
  try { return new URL(o).host === req.headers.host; } catch { return false; }
}

/* ---------------- GitHub (git data API) ---------------- */
async function gh(method, url, body) {
  const r = await fetch(GH + url, {
    method,
    headers: { Authorization: "Bearer " + TOKEN, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "maid-lifestyle-uploader", ...(body ? { "Content-Type": "application/json" } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await r.text();
  const j = text ? JSON.parse(text) : {};
  if (!r.ok) throw Object.assign(new Error("GitHub " + r.status + ": " + (j.message || text).slice(0, 200)), { status: r.status });
  return j;
}
async function readGallery(commitSha) {
  try {
    const f = await gh("GET", `/repos/${REPO}/contents/${DATA_PATH}?ref=${commitSha}`);
    return JSON.parse(Buffer.from(f.content, "base64").toString("utf8"));
  } catch (e) { if (e.status === 404) return []; throw e; }
}
/* Apply a change to gallery JSON + image files as one commit; retries if main moved. */
async function commitChange(message, mutate) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const ref = await gh("GET", `/repos/${REPO}/git/ref/heads/${BRANCH}`);
    const head = ref.object.sha;
    const commit = await gh("GET", `/repos/${REPO}/git/commits/${head}`);
    const gallery = await readGallery(head);
    const { files, result, skip } = mutate(gallery); // files: [{path, base64}|{path, delete:true}]
    if (skip) return result; // nothing to change — don't create an empty commit
    const tree = [];
    for (const f of files) {
      if (f.delete) { tree.push({ path: f.path, mode: "100644", type: "blob", sha: null }); continue; }
      const blob = await gh("POST", `/repos/${REPO}/git/blobs`, { content: f.base64, encoding: "base64" });
      tree.push({ path: f.path, mode: "100644", type: "blob", sha: blob.sha });
    }
    const data = Buffer.from(JSON.stringify(gallery, null, 2) + "\n").toString("base64");
    const dblob = await gh("POST", `/repos/${REPO}/git/blobs`, { content: data, encoding: "base64" });
    tree.push({ path: DATA_PATH, mode: "100644", type: "blob", sha: dblob.sha });
    const newTree = await gh("POST", `/repos/${REPO}/git/trees`, { base_tree: commit.tree.sha, tree });
    const newCommit = await gh("POST", `/repos/${REPO}/git/commits`, { message: message + "\n\nVia the Maid Lifestyle photo uploader.", tree: newTree.sha, parents: [head] });
    try {
      await gh("PATCH", `/repos/${REPO}/git/refs/heads/${BRANCH}`, { sha: newCommit.sha, force: false });
      await redeploy();
      return result;
    } catch (e) { if (e.status !== 422 || attempt === 2) throw e; } // branch moved: retry on top
  }
}
async function redeploy() {
  if (!DEPLOY_HOOK) return;
  try { await fetch(DEPLOY_HOOK, { method: "POST" }); } catch (e) { console.error("Deploy hook failed:", e.message); }
}

/* ---------------- validation ---------------- */
function jpegBase64(s) {
  if (typeof s !== "string") return null;
  const m = /^data:image\/jpeg;base64,([A-Za-z0-9+/=]+)$/.exec(s);
  if (!m) return null;
  const buf = Buffer.from(m[1], "base64");
  if (buf.length < 1000 || buf[0] !== 0xff || buf[1] !== 0xd8 || buf[2] !== 0xff) return null;
  return m[1];
}
const clean = (s, max) => String(s || "").replace(/[\u0000-\u001f<>]/g, " ").replace(/\s+/g, " ").trim().slice(0, max);

/* ---------------- routes ---------------- */
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://x");
  try {
    if (req.method === "GET" && url.pathname === "/") return send(res, 200, PAGE, "text/html; charset=utf-8");
    if (req.method === "GET" && url.pathname === "/robots.txt") return send(res, 200, "User-agent: *\nDisallow: /\n", "text/plain");
    if (req.method === "GET" && url.pathname === "/healthz") return send(res, 200, { ok: true });
    if (req.method !== "GET" && !sameOrigin(req)) return send(res, 403, { error: "Forbidden" });

    if (req.method === "POST" && url.pathname === "/api/login") {
      const ip = clientIp(req);
      if (lockedOut(ip)) return send(res, 429, { error: "Too many attempts. Try again in 15 minutes." });
      const { password } = await readJson(req);
      if (!passwordOk(password)) { noteFail(ip); await new Promise((r) => setTimeout(r, 600)); return send(res, 401, { error: "Wrong password." }); }
      fails.delete(ip);
      res.setHeader("Set-Cookie", `ml_session=${makeSession()}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=${SESSION_HOURS * 3600}`);
      return send(res, 200, { ok: true });
    }
    if (req.method === "POST" && url.pathname === "/api/logout") {
      res.setHeader("Set-Cookie", "ml_session=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0");
      return send(res, 200, { ok: true });
    }

    // Everything below requires a valid session
    if (!url.pathname.startsWith("/api/")) return send(res, 404, { error: "Not found" });
    if (!validSession(req)) return send(res, 401, { error: "Please log in." });
    if (!TOKEN) return send(res, 503, { error: "Uploads aren't set up yet (missing GitHub token)." });

    if (req.method === "GET" && url.pathname === "/api/photos") {
      const ref = await gh("GET", `/repos/${REPO}/git/ref/heads/${BRANCH}`);
      return send(res, 200, { photos: await readGallery(ref.object.sha) });
    }
    if (req.method === "POST" && url.pathname === "/api/photos") {
      const b = await readJson(req);
      const lg = jpegBase64(b.large), sm = jpegBase64(b.small);
      if (!lg || !sm) return send(res, 400, { error: "That file couldn't be read as a photo." });
      const caption = clean(b.caption, 140);
      if (caption.length < 3) return send(res, 400, { error: "Please add a short description." });
      const cats = Array.isArray(b.categories) ? [...new Set(b.categories.filter((c) => CATS.includes(c)))] : [];
      if (!cats.length) return send(res, 400, { error: "Pick at least one category." });
      const id = new Date().toISOString().slice(0, 10) + "-" + crypto.randomBytes(4).toString("hex");
      const entry = { id, alt: caption, cat: cats.join(" "), added: new Date().toISOString() };
      await commitChange(`Add photo: ${caption}`, (gallery) => {
        gallery.unshift(entry);
        return { files: [{ path: `${IMG_DIR}/${id}-lg.jpg`, base64: lg }, { path: `${IMG_DIR}/${id}-sm.jpg`, base64: sm }], result: entry };
      });
      return send(res, 200, { ok: true, photo: entry, redeploy: !!DEPLOY_HOOK });
    }
    const del = /^\/api\/photos\/([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9a-f]{8})$/.exec(url.pathname);
    if (req.method === "DELETE" && del) {
      const id = del[1];
      let found = false;
      await commitChange(`Remove photo ${id}`, (gallery) => {
        const i = gallery.findIndex((p) => p.id === id);
        if (i > -1) { found = true; gallery.splice(i, 1); }
        return found ? { files: [{ path: `${IMG_DIR}/${id}-lg.jpg`, delete: true }, { path: `${IMG_DIR}/${id}-sm.jpg`, delete: true }], result: null } : { skip: true, result: null };
      });
      return found ? send(res, 200, { ok: true }) : send(res, 404, { error: "Photo not found." });
    }
    return send(res, 404, { error: "Not found" });
  } catch (e) {
    console.error(e);
    return send(res, e.code === 413 ? 413 : e.code === 400 ? 400 : 502, { error: e.code === 413 ? "That photo is too large." : e.code === 400 ? "Bad request." : "Something went wrong saving to the website. Please try again." });
  }
});
server.listen(PORT, () => console.log("Maid Lifestyle uploader listening on", PORT));
