(function () {
  "use strict";
  var C = window.ML_CONFIG || {};

  /* ---- Header shadow + mobile menu ---- */
  var header = document.querySelector(".header");
  var onScroll = function () { header && header.classList.toggle("scrolled", window.scrollY > 10); };
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();

  var toggle = document.querySelector(".menu-toggle"), nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open);
    });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) { nav.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); } });
  }

  /* ---- Reveal on scroll ---- */
  var els = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    els.forEach(function (el) { io.observe(el); });
  } else els.forEach(function (el) { el.classList.add("in"); });

  /* ---- Footer year ---- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---- Reviews (real reviews only, from config.js) ---- */
  var rv = document.getElementById("reviews");
  if (rv) {
    var list = window.ML_REVIEWS || [];
    if (list.length) {
      rv.innerHTML = "";
      list.forEach(function (r) {
        var a = document.createElement("article"); a.className = "review reveal in";
        var q = document.createElement("blockquote"); q.textContent = r.text;
        var c = document.createElement("cite"); c.textContent = r.name;
        var s = document.createElement("small"); s.textContent = r.detail || "";
        a.append(q, c, s); rv.appendChild(a);
      });
    }
  }

  /* ---- Preselect service on quote form via ?service= ---- */
  var params = new URLSearchParams(location.search);
  var svc = params.get("service");
  if (svc) {
    var sel = document.querySelector('select[name="Cleaning type"]');
    if (sel) for (var i = 0; i < sel.options.length; i++) if (sel.options[i].dataset.key === svc) sel.selectedIndex = i;
    if (svc === "turnover" || svc === "realestate") {
      var com = document.querySelector('input[name="Property type"][value="Commercial / Property management"]');
      if (com) com.checked = true;
    }
  }
  // Earliest selectable date = today
  document.querySelectorAll('input[type="date"]').forEach(function (d) { d.min = new Date().toISOString().slice(0, 10); });

  /* ---- Form submission (FormSubmit.co AJAX → Shana's inbox) ---- */
  document.querySelectorAll("form[data-lead]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector(".form-status");
      status.className = "form-status"; status.textContent = "";
      if (!form.checkValidity()) { form.reportValidity(); return; }
      if (form.querySelector(".hp input") && form.querySelector(".hp input").value) return; // bot

      var data = {};
      new FormData(form).forEach(function (v, k) {
        if (k === "_honey") return;
        data[k] = data[k] ? data[k] + ", " + v : v;
      });
      data._subject = form.dataset.subject + " — " + (data["Name"] || data["Contact name"] || "Website");
      data._template = "table";
      data._captcha = "false";
      if (data["Email"]) data._replyto = data["Email"];
      data["Submitted from"] = location.href;

      var target = C.formAlias || C.leadEmail;
      var btn = form.querySelector('button[type="submit"]'), label = btn.innerHTML;
      btn.disabled = true; btn.textContent = "Sending…";

      fetch("https://formsubmit.co/ajax/" + encodeURIComponent(target), {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(data)
      })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok || String(res.j.success) !== "true") throw new Error(res.j.message || "Submission failed");
          form.classList.add("sent");
          var ok = form.nextElementSibling; if (ok) { ok.setAttribute("tabindex", "-1"); ok.focus(); }
          form.reset();
        })
        .catch(function () {
          status.className = "form-status error";
          status.innerHTML = "Sorry — your request didn't go through. Please call or text <a href=\"tel:" + C.phone.replace(/\D/g, "") + "\">" + C.phone + "</a> or email <a href=\"mailto:" + C.leadEmail + "\">" + C.leadEmail + "</a>.";
        })
        .finally(function () { btn.disabled = false; btn.innerHTML = label; });
    });
  });

  /* ---- Gallery filters + lightbox ---- */
  var gal = document.querySelector(".gallery");
  if (gal) {
    var items = Array.prototype.slice.call(gal.querySelectorAll("a"));
    var empty = document.getElementById("gallery-empty");
    document.querySelectorAll(".filters button").forEach(function (b) {
      b.addEventListener("click", function () {
        document.querySelectorAll(".filters button").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true");
        var f = b.dataset.filter, shown = 0;
        items.forEach(function (a) {
          var on = f === "all" || a.dataset.cat.split(" ").indexOf(f) > -1;
          a.classList.toggle("hidden", !on); if (on) shown++;
        });
        if (empty) empty.hidden = shown > 0;
        gal.hidden = shown === 0;
      });
    });

    var lb = document.getElementById("lightbox"), lbImg = lb.querySelector("img"), lbCap = lb.querySelector("p"), idx = 0, lastFocus;
    var visible = function () { return items.filter(function (a) { return !a.classList.contains("hidden"); }); };
    var show = function (i) {
      var v = visible(); idx = (i + v.length) % v.length;
      var a = v[idx], img = a.querySelector("img");
      lbImg.src = a.getAttribute("href"); lbImg.alt = img.alt; lbCap.textContent = img.alt;
    };
    var open = function (a) { lastFocus = a; lb.classList.add("open"); document.body.style.overflow = "hidden"; show(visible().indexOf(a)); lb.querySelector(".lb-close").focus(); };
    var close = function () { lb.classList.remove("open"); document.body.style.overflow = ""; lbImg.src = ""; lastFocus && lastFocus.focus(); };
    items.forEach(function (a) { a.addEventListener("click", function (e) { e.preventDefault(); open(a); }); });
    lb.querySelector(".lb-close").onclick = close;
    lb.querySelector(".lb-prev").onclick = function () { show(idx - 1); };
    lb.querySelector(".lb-next").onclick = function () { show(idx + 1); };
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") close(); if (e.key === "ArrowLeft") show(idx - 1); if (e.key === "ArrowRight") show(idx + 1);
    });
    var sx = null;
    lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) { if (sx === null) return; var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1)); sx = null; });
  }
})();
