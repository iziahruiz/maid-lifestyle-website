#!/usr/bin/env python3
"""Builds the Maid Lifestyle website pages (shared header/footer + page content).

Edit the SETTINGS below, then run:  python3 build.py
Output: the .html files in this folder (upload the whole folder to your host).
"""
import json, html, os, datetime

# ============================ SETTINGS ============================
SITE_URL = ""          # e.g. "https://www.maidlifestylecleaning.com"  (no trailing slash) — needed for canonical/QR/sitemap
SERVICE_AREA = "Goose Creek, SC (29445)"      # e.g. "Goose Creek, Summerville & the Greater Charleston, SC area"
PHONE = "854-274-4871"
EMAIL = "themaidlifestylecompany@gmail.com"
FACEBOOK_URL = "https://www.facebook.com/search/top?q=Maid%20Lifestyle%20Cleaning%20Services"  # replace with the page's real URL
BUSINESS = "Maid Lifestyle Cleaning Services"
OWNER = "Shana"
TAGLINE = "A Clean Home Is a Happy Home."
# ==================================================================

HERE = os.path.dirname(os.path.abspath(__file__))
TEL = "tel:+1" + "".join(c for c in PHONE if c.isdigit())
SMS = "sms:+1" + "".join(c for c in PHONE if c.isdigit())
AREA_TXT = f"Serving {SERVICE_AREA}" if SERVICE_AREA else "Call or text to confirm your service area"
e = html.escape

I = {  # inline icons
 "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10" opacity=".25"/><path d="m7.5 12.5 3 3 6-6.5"/></svg>',
 "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
 "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></svg>',
 "fb": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 8h3V4h-3c-2.8 0-5 2.2-5 5v2H7v4h2v7h4v-7h3l1-4h-4V9c0-.6.4-1 1-1z"/></svg>',
 "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15l.7 2.3L22 18l-2.3.7L19 21l-.7-2.3L16 18l2.3-.7z"/></svg>',
 "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
 "eye": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
 "cal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18M8 15h2m4 0h2"/></svg>',
 "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 10.5 12 3l9 7.5V21h-6v-6H9v6H3z"/></svg>',
 "building": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="2" width="16" height="20" rx="1"/><path d="M9 22v-4h6v4M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/></svg>',
 "heart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/></svg>',
 "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
 "x": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>',
 "left": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m15 6-6 6 6 6"/></svg>',
 "right": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>',
 "key": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="7.5" cy="15.5" r="4.5"/><path d="m10.7 12.3 9.3-9.3M17 6l3 3M14 9l2 2"/></svg>',
 "trash": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18M8 6V4h8v2M6 6l1 15h10l1-15M10 11v6M14 11v6"/></svg>',
 "sign": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 22V3M4 4h14l-2 4 2 4H4"/></svg>',
}
def ck(items): return '<ul class="checklist">' + "".join(f"<li>{I['check']}<span>{e(x)}</span></li>" for x in items) + "</ul>"
def img(name, alt, cls="", size="sm", lazy=True, extra=""):
    return f'<img src="assets/img/{name}-{size}.jpg" alt="{e(alt)}"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}{" loading=\"lazy\"" if lazy else ""} decoding="async"{extra}>'

NAV = [("index.html","Home"),("services.html","Our Services"),("about.html","About Us"),("work.html","Our Work"),("property-managers.html","Property Managers"),("contact.html","Contact")]

def page(fname, title, desc, body, og_img="living-room"):
    nav = "".join(f'<li><a href="{h}"{" aria-current=\"page\"" if h==fname else ""}>{t}</a></li>' for h,t in NAV)
    canon = f'<link rel="canonical" href="{SITE_URL}/{"" if fname=="index.html" else fname}">\n<meta property="og:url" content="{SITE_URL}/{"" if fname=="index.html" else fname}">' if SITE_URL else ""
    ogi = f"{SITE_URL}/assets/img/{og_img}-lg.jpg" if SITE_URL else f"assets/img/{og_img}-lg.jpg"
    ld = {"@context":"https://schema.org","@type":"LocalBusiness","@id":(SITE_URL or "")+"/#business","name":BUSINESS,
          "slogan":TAGLINE,"telephone":"+1-"+PHONE,"email":EMAIL,"founder":{"@type":"Person","name":OWNER},
          "image":ogi,"logo":(SITE_URL+"/" if SITE_URL else "")+"assets/img/logo-tagline.png","priceRange":"$$",
          "paymentAccepted":"Cash App, Venmo, Zelle","sameAs":[FACEBOOK_URL] if "search" not in FACEBOOK_URL else [],
          "description":"Residential cleaning, deep cleaning, move-in/move-out cleaning, apartment turnover cleaning and real estate listing preparation.",
          "makesOffer":[{"@type":"Offer","itemOffered":{"@type":"Service","name":n}} for n in ["Residential Cleaning","Deep Cleaning","Move-In / Move-Out Cleaning","Apartment Turnover Cleaning","Real Estate Listing Preparation","Trash-Out Services"]]}
    if SITE_URL: ld["url"] = SITE_URL
    if SERVICE_AREA: ld["areaServed"] = SERVICE_AREA
    full_title = f"{title} | {BUSINESS}" if fname!="index.html" else title
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0f3d1e">
{canon}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BUSINESS}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{ogi}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="assets/img/favicon.png">
<link rel="apple-touch-icon" href="assets/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Great+Vibes&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
<script type="application/ld+json">{json.dumps(ld)}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="container"><span class="hide-sm">{e(TAGLINE)}</span><span><a href="{TEL}">Call / Text {PHONE}</a> &nbsp;·&nbsp; <a href="mailto:{EMAIL}" class="hide-sm">{EMAIL}</a></span></div></div>
<header class="header">
 <div class="container">
  <a class="brand" href="index.html" aria-label="{BUSINESS} home"><img src="assets/img/logo.png" alt="Maid Lifestyle Cleaning Services logo" width="602" height="220"></a>
  <button class="menu-toggle" aria-controls="site-nav" aria-expanded="false" aria-label="Open menu">{I['menu']}</button>
  <nav class="nav" id="site-nav" aria-label="Main"><ul>{nav}<li><a class="btn btn--primary" href="quote.html">Get a Free Quote</a></li></ul></nav>
 </div>
</header>
<main id="main">
{body}
</main>
<footer class="footer">
 <div class="container">
  <div class="footer__grid">
   <div>
    <a class="footer__logo" href="index.html"><img src="assets/img/logo.png" alt="Maid Lifestyle logo" loading="lazy"></a>
    <p class="tagline">A Clean Home Is a Happy Home</p>
    <p>Residential, deep, move-in/move-out, apartment turnover and real estate cleaning. Owned and operated by {OWNER}.</p>
   </div>
   <div><h4>Explore</h4><ul>{"".join(f'<li><a href="{h}">{t}</a></li>' for h,t in NAV)}<li><a href="quote.html">Request a Free Quote</a></li></ul></div>
   <div><h4>Services</h4><ul>
    <li><a href="services.html#residential">Residential Cleaning</a></li><li><a href="services.html#deep">Deep Cleaning</a></li>
    <li><a href="services.html#move">Move-In / Move-Out</a></li><li><a href="services.html#turnover">Apartment Turnovers</a></li>
    <li><a href="services.html#realestate">Real Estate Prep</a></li><li><a href="services.html#trashout">Trash-Out Services</a></li></ul></div>
   <div><h4>Contact</h4><ul>
    <li><a href="{TEL}">{PHONE}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
    <li><a href="{FACEBOOK_URL}" target="_blank" rel="noopener">Facebook: Maid Lifestyle Cleaning Services</a></li>
    <li>{e(AREA_TXT)}</li><li>Payment: Cash App · Venmo · Zelle</li></ul></div>
  </div>
  <div class="footer__bottom"><span>© <span data-year></span> {BUSINESS}. All rights reserved.</span><span>Free estimates · Certified funds only · No checks</span></div>
 </div>
</footer>
<div class="mobile-bar"><a class="btn btn--ghost" href="{TEL}">{I['phone']} Call Now</a><a class="btn btn--primary" href="quote.html">Free Quote</a></div>
<script src="assets/js/config.js"></script>
<script src="assets/js/main.js" defer></script>
</body>
</html>"""

def page_hero(eyebrow, h1, sub, bg):
    return f'''<section class="page-hero"><div class="hero__bg" style="background-image:url('assets/img/{bg}-lg.jpg')"></div>
<div class="container"><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p>{sub}</p></div></section>'''

def cta_band(h, p, btn="Request a Free Quote", href="quote.html"):
    return f'''<section class="section"><div class="container"><div class="cta reveal"><div><h2>{h}</h2><p>{p}</p></div>
<div class="btn-row"><a class="btn btn--gold" href="{href}">{btn}</a><a class="btn btn--ghost-light" href="{TEL}">{I['phone']} {PHONE}</a></div></div></div></section>'''

# ---------------- SERVICES DATA ----------------
SERVICES = [
 dict(key="residential", icon="home", title="Residential Cleaning", img="kitchen-gray", accent="double-vanity",
      blurb="For homeowners, individuals, and families who want a clean, comfortable living space.",
      items=["Routine cleaning","Weekly and biweekly cleaning","Monthly cleaning","General household cleaning","Kitchen and bathroom cleaning","Dusting and surface cleaning","Floors and common areas"]),
 dict(key="deep", icon="spark", title="Deep Cleaning", img="tile-shower", accent="fridge-interior",
      blurb="Detailed cleaning for homes that need extra attention — top to bottom, corner to corner.",
      items=["Detailed kitchen cleaning","Appliances","Cabinets (inside & outside)","Bathroom scrubbing","Bathroom grout & buildup removal","Baseboards & trim","Dust removal","Hard-to-reach areas","Detailed floor cleaning","Extra attention to neglected & high-touch areas"]),
 dict(key="move", icon="key", title="Move-In / Move-Out Cleaning", img="dining", accent="freezer",
      blurb="Professional cleaning for people moving into or out of a home or apartment.",
      items=["Empty-unit cleaning","Kitchen and appliance exterior cleaning","Bathroom sanitizing","Cabinet and countertop cleaning","Floors and baseboards","Interior window cleaning (on request)","Final property preparation"]),
 dict(key="turnover", icon="building", title="Apartment Turnover Cleaning", img="bedroom-3", accent="hall-bath", corp=True,
      blurb="Dependable, fast-turnaround cleaning for apartment communities and property management companies — so every unit is ready for its next resident.",
      items=["Vacant apartment cleaning","Move-out cleaning","Move-in preparation","Unit turnover cleaning","Rental property cleaning","Property presentation","Flexible scheduling for management teams"]),
 dict(key="realestate", icon="sign", title="Real Estate & Listing Preparation", img="living-room", accent="primary-bath",
      blurb="For real estate agents, home sellers, landlords, and property investors who need a property looking its best.",
      items=["Pre-listing cleaning","Showing preparation","Open-house preparation","Empty-home cleaning","General property refresh","Move-in-ready cleaning"],
      cta="Getting a Property Ready to Sell? Let Maid Lifestyle Help Make It Shine."),
 dict(key="trashout", icon="trash", title="Trash-Out Services", img="mudroom", accent=None,
      blurb="Clearing out what was left behind so a property can be cleaned and turned over. Starting at $350+.",
      items=["Removal of left-behind items","Pricing based on amount of items","Size of property","Condition of property","Labor hours required"]),
]

# ---------------- GALLERY DATA (all photos are Shana's completed work) ----------------
GALLERY = [
 ("kitchen-gray","kitchen","Kitchen with gray cabinets, white quartz counters and stainless refrigerator, cleaned by Maid Lifestyle"),
 ("living-room","living","Open living room with freshly mopped plank floors and sunlit windows"),
 ("tile-shower","bathroom deep","Tiled walk-in shower with clean glass door and shower pan"),
 ("bedroom-1","bedroom","Bedroom carpet freshly vacuumed with even vacuum lines"),
 ("kitchen-wood","kitchen","Kitchen with wood cabinets, black granite counters and freshly mopped floor"),
 ("fridge-interior","kitchen deep","French-door refrigerator interior wiped down and emptied"),
 ("double-vanity","bathroom","Double-sink bathroom vanity with polished faucets and mirror"),
 ("dining","living","Dining area with gleaming plank floors and sliding glass door"),
 ("primary-bath","bathroom deep","Primary bathroom with freshly mopped tile floor and garden tub"),
 ("bedroom-2","bedroom","Empty bedroom with freshly vacuumed carpet"),
 ("glass-shower","bathroom deep","Glass-enclosed shower stall cleaned to a shine"),
 ("freezer","kitchen deep","Freezer drawer cleaned inside, with ice maker bin"),
 ("hall-bath","bathroom","Hall bathroom with tub, toilet and freshly mopped tile floor"),
 ("mudroom","living","Mudroom hallway with built-in bench and freshly cleaned floor"),
 ("fridge-hisense","kitchen deep","Refrigerator interior with clean glass shelves and drawers"),
 ("bath-wood-vanity","bathroom","Bathroom with one-piece tub shower, wood vanity and clean plank floor"),
 ("bedroom-3","bedroom","Bedroom with freshly vacuumed carpet and bright windows"),
 ("tub-detail","bathroom deep","Close-up of a scrubbed bathtub and shower surround"),
 ("fridge-door","kitchen deep","Refrigerator door bins cleaned and cleared"),
 ("half-bath","bathroom","Half bath with pedestal sink, oval mirror and clean floor"),
 ("kitchen-island-shine","kitchen","Open kitchen with granite island and freshly mopped, gleaming plank floors"),
 ("living-floor-shine","living","Open living area with plank floors mopped to a high shine"),
 ("kitchen-cherry","kitchen","Kitchen with cherry cabinets, granite counters and stainless dishwasher, cleaned and ready"),
 ("hall-tub-shower","bathroom deep","One-piece tub and shower surround scrubbed clean, with handheld shower head"),
 ("vanity-mirror","bathroom","Bathroom vanity with wiped-down sink, faucet and mirror"),
 ("half-bath-door","bathroom","Bathroom with clean vanity, toilet and freshly mopped tile floor"),
 ("toilet-curtain","bathroom","Toilet and tile floor cleaned, with fresh white shower curtain"),
 ("bedroom-3-windows","bedroom","Bedroom with three windows and freshly vacuumed carpet"),
 ("loft-carpet","living","Upstairs loft carpet with fresh vacuum lines"),
 ("laundry-floor","living","Laundry room vinyl floor mopped clean"),
]

# ================= PAGES =================
def home():
    why = [("shield","Dependable & Professional","Show up on time, communicate clearly, and do the job right — every visit."),
           ("eye","Attention to Detail","Baseboards, fixtures, corners and the spots most people miss."),
           ("spark","Quality You Can See","Fresh vacuum lines, gleaming floors, spotless fixtures — see the photos."),
           ("cal","Flexible Options","One-time, weekly, biweekly or monthly — scheduled around you."),
           ("building","Residential & Commercial","Homes, apartments, rentals, turnovers and listings."),
           ("heart","Customer-Focused","Your satisfaction matters. We listen and tailor every clean.")]
    whyh = "".join(f'<article class="feature reveal"><div class="icon">{I[i]}</div><h3>{t}</h3><p>{d}</p></article>' for i,t,d in why)
    cards = "".join(f'''<a class="svc-card reveal" href="services.html#{s['key']}"><div class="svc-card__img">{img(s['img'], s['title']+' — completed Maid Lifestyle cleaning')}</div>
<div class="svc-card__body"><h3>{s['title']}</h3><p>{s['blurb']}</p><span class="svc-card__more">Learn more {I['arrow']}</span></div></a>''' for s in SERVICES)
    feat = ["kitchen-gray","tile-shower","bedroom-1","double-vanity","dining","fridge-interior","primary-bath","kitchen-wood"]
    alt = dict((g[0],g[2]) for g in GALLERY)
    mosaic = "".join(img(n, alt[n]) for n in feat)
    trust = "".join(f"<li>{I['check']}{t}</li>" for t in ["Professional","Reliable","Affordable","Detail-Oriented","Free Estimates"])
    body = f'''
<section class="hero"><div class="hero__bg" style="background-image:url('assets/img/living-room-lg.jpg')" role="img" aria-label="Bright living room with freshly cleaned floors"></div>
 <div class="container"><div class="hero__inner">
  <div class="hero__logo"><img src="assets/img/logo-tagline.png" alt="Maid Lifestyle Cleaning Services — A Clean Home Is a Happy Home" width="766" height="420"></div>
  <h1>A Clean Home Is a Happy Home.</h1>
  <span class="tag">A Cleaner Home. A Better Lifestyle.</span>
  <p>Professional cleaning services designed to make your home, apartment, or property feel fresh, spotless, and welcoming.</p>
  <div class="btn-row"><a class="btn btn--gold" href="quote.html">Request a Free Quote</a><a class="btn btn--ghost-light" href="services.html">Explore Our Services</a></div>
 </div></div>
</section>
<div class="trust"><ul class="container">{trust}</ul></div>

<section class="section"><div class="container">
 <div class="head center reveal"><span class="eyebrow">Why Choose Us</span><h2>Why Choose <span class="script">Maid Lifestyle?</span></h2>
 <p class="lead">Cleaning you can count on, from people who care about the details.</p></div>
 <div class="grid grid-3">{whyh}</div>
</div></section>

<section class="section section--cream"><div class="container">
 <div class="head center reveal"><span class="eyebrow">Our Cleaning Services</span><h2>Every Space, Every Need</h2>
 <p class="lead">From weekly upkeep to full move-out and apartment turnovers — every photo below is a space Shana cleaned.</p></div>
 <div class="grid grid-3">{cards}</div>
</div></section>

<section class="section"><div class="container">
 <div class="head center reveal"><span class="eyebrow">Our Work</span><h2>Real Homes. Real Results.</h2>
 <p class="lead">No stock photos — these are spaces Maid Lifestyle has cleaned.</p></div>
 <div class="mosaic reveal">{mosaic}</div>
 <p class="center" style="margin-top:34px"><a class="btn btn--ghost" href="work.html">View the Full Gallery {I['arrow']}</a></p>
</div></section>

<section class="section section--green"><div class="container split">
 <div class="reveal"><span class="eyebrow">For Property Professionals</span><h2>Professional Cleaning Solutions for Property Managers</h2>
 <p class="lead">Keep your properties clean, presentable, and ready for their next residents. Maid Lifestyle provides cleaning solutions for apartment turnovers, vacant units, rental properties, and real estate preparation.</p>
 <div class="btn-row" style="margin-top:26px"><a class="btn btn--gold" href="property-managers.html#inquiry">Request a Commercial Cleaning Quote</a><a class="btn btn--ghost-light" href="property-managers.html">Learn More</a></div></div>
 <div class="split__media reveal">{img("bedroom-3","Vacant apartment bedroom with freshly vacuumed carpet, ready for move-in")}
  <div class="card-float"><strong>Turnover-ready</strong><span>Vacant units, move-outs & rental refreshes</span></div></div>
</div></section>

<section class="section section--cream"><div class="container">
 <div class="head center reveal"><span class="eyebrow">Customer Reviews</span><h2>What Our Clients Say</h2></div>
 <div class="reviews" id="reviews"><div class="empty reveal" style="grid-column:1/-1"><h3>Reviews Coming Soon</h3>
 <p>We're collecting feedback from our clients. Worked with Maid Lifestyle? We'd love to hear from you on <a href="{FACEBOOK_URL}" target="_blank" rel="noopener">Facebook</a>.</p></div></div>
</div></section>
{cta_band("Ready for a Cleaner Home?","Free estimates. Tell us about your space and Shana will get back to you with a quote.")}'''
    return page("index.html","Maid Lifestyle Cleaning Services | House, Deep, Move-Out & Apartment Turnover Cleaning",
        "Maid Lifestyle Cleaning Services offers professional house cleaning, deep cleaning, move-in/move-out cleaning, apartment turnover and real estate cleaning. Free estimates — call 854-274-4871.", body)

def services():
    rows = ""
    for s in SERVICES:
        acc = img(s['accent'], s['title']+" detail", "accent") if s.get('accent') else ""
        extra = f'<p class="script" style="font-size:1.7rem;margin-bottom:18px">{s["cta"]}</p>' if s.get("cta") else ""
        badge = '<span class="badge">For Property Management</span>' if s.get("corp") else ""
        btns = f'<div class="btn-row"><a class="btn {"btn--gold" if s.get("corp") else "btn--primary"}" href="quote.html?service={s["key"]}">Request a Quote</a>'
        if s.get("corp"): btns += f'<a class="btn btn--ghost-light" href="property-managers.html">Property Manager Solutions</a>'
        btns += "</div>"
        rows += f'''<article class="svc reveal{" svc--corp" if s.get("corp") else ""}" id="{s['key']}">
<div class="svc__media">{img(s['img'], s['title']+' — space cleaned by Maid Lifestyle', size="lg")}{acc}</div>
<div>{badge}<span class="eyebrow">{e(s['title'])}</span><h2>{e(s['title'])}</h2><p class="lead">{s['blurb']}</p>{ck(s['items'])}{extra}{btns}</div></article>'''
    def table(title, icon, rows_std, rows_deep):
        dl = lambda r: "<dl>" + "".join(f"<dt>{a}</dt><dd>{b}</dd>" for a,b in r) + "</dl>"
        return f'''<div class="price-card reveal"><header><span class="icon" style="background:rgba(255,255,255,.12);color:#fff">{I[icon]}</span><h3>{title}</h3></header>
<div class="price-cols"><div class="price-col"><h4>Standard Cleaning</h4>{dl(rows_std)}</div><div class="price-col"><h4>Deep Cleaning</h4>{dl(rows_deep)}</div></div></div>'''
    apt = table("Apartment Cleaning","building",[("Studio / 1 Bedroom","$95"),("2 Bedroom","$125"),("3 Bedroom","$155")],[("Studio / 1 Bedroom","$175"),("2 Bedroom","$220"),("3 Bedroom","$275")])
    house = table("House Cleaning","home",[(f"{n} Bedroom",p) for n,p in zip(range(1,7),["$120","$145","$175","$210","$250","$300"])],[(f"{n} Bedroom",p) for n,p in zip(range(1,7),["$175","$220","$275","$340","$420","$500"])])
    jump = "".join(f'<a class="btn btn--ghost" style="min-height:44px;padding:10px 18px" href="#{s["key"]}">{e(s["title"])}</a>' for s in SERVICES)
    body = page_hero("Our Cleaning Services","Cleaning Services for Every Space","Residential, deep, move-in/move-out, apartment turnover, real estate and trash-out services — all with the same attention to detail.","kitchen-gray") + f'''
<section class="section" style="padding-bottom:0"><div class="container"><div class="btn-row" style="justify-content:center">{jump}<a class="btn btn--ghost" style="min-height:44px;padding:10px 18px" href="#pricing">Starting Prices</a></div></div></section>
<section class="section" style="padding-top:20px"><div class="container">{rows}</div></section>
<section class="section section--cream" id="pricing" style="scroll-margin-top:90px"><div class="container">
 <div class="head center reveal"><span class="eyebrow">Starting Prices</span><h2>Simple, Upfront Pricing</h2><p class="lead">Free estimates available. Final pricing is confirmed after we learn about your space.</p></div>
 <div class="grid grid-2">{apt}{house}</div>
 <div class="grid grid-2" style="margin-top:26px">
  <div class="note reveal"><strong>Trash-Out Services — starting at $350+.</strong> Pricing is based on the amount of items to be removed, size and condition of the property, and labor hours required.</div>
  <div class="note reveal"><strong>Prices may vary depending on:</strong> size of apartment or home, square footage, overall condition, frequency of service, number of pets, first-time cleanings, and special requests.</div>
 </div>
 <p class="center reveal" style="margin-top:28px;color:var(--muted)">Payment methods: <strong>Cash App · Venmo · Zelle</strong> &nbsp;|&nbsp; Certified funds only · No checks</p>
</div></section>
{cta_band("Not Sure Which Service You Need?","Tell us about your space and we'll recommend the right clean — free, no obligation.")}'''
    return page("services.html","House Cleaning, Deep Cleaning & Move-Out Cleaning Services",
        "Residential cleaning, deep cleaning, move-in/move-out cleaning, apartment turnover cleaning, real estate listing prep and trash-out services from Maid Lifestyle. See starting prices.", body, "kitchen-gray")

def about():
    vals = [("eye","Attention to Every Detail","We clean the way we'd want our own homes cleaned."),("shield","Reliable & Trustworthy","Dependable service you can schedule around."),("heart","Your Satisfaction Matters","We listen, and we make it right.")]
    body = page_hero("About Us","Meet Maid Lifestyle","A Clean Home Is a Happy Home.","living-room") + f'''
<section class="section"><div class="container split">
 <div class="split__media reveal">{img("double-vanity","Double vanity bathroom cleaned by Maid Lifestyle", size="lg")}
  <div class="card-float"><strong>Owned by {OWNER}</strong><span>Every photo on this site is her work</span></div></div>
 <div class="reveal"><span class="eyebrow">Our Story</span><h2>Meet <span class="script">Maid Lifestyle</span></h2>
  <p>{BUSINESS} is dedicated to helping homeowners, families, and property professionals maintain clean, comfortable, and welcoming spaces.</p>
  <p>We believe a clean environment makes a difference in everyday life. From routine residential cleaning to detailed move-out services and apartment turnovers, our goal is to deliver dependable service and quality results with attention to every detail.</p>
  <p>Whether you're looking for help maintaining your home or preparing a property for its next resident, Maid Lifestyle is here to help.</p>
  <p class="script" style="font-size:2rem;margin:10px 0 24px">Let us handle the mess so you can enjoy the rest!</p>
  <div class="btn-row"><a class="btn btn--primary" href="quote.html">Request a Free Quote</a><a class="btn btn--ghost" href="work.html">See Our Work</a></div></div>
</div></section>
<section class="section section--cream"><div class="container"><div class="head center reveal"><span class="eyebrow">What We Stand For</span><h2>Our Promise</h2></div>
<div class="grid grid-3">{"".join(f'<article class="feature reveal"><div class="icon">{I[i]}</div><h3>{t}</h3><p>{d}</p></article>' for i,t,d in vals)}</div></div></section>
{cta_band("Let's Make Your Space Shine","Homes, apartments, rentals and listings — get a free estimate today.")}'''
    return page("about.html","About Us — Meet Maid Lifestyle", "Meet Maid Lifestyle Cleaning Services, owned by Shana — dependable residential and property cleaning with attention to every detail.", body, "double-vanity")

def work():
    cats = [("all","All"),("kitchen","Kitchens"),("bathroom","Bathrooms"),("living","Living Areas"),("bedroom","Bedrooms"),("deep","Deep Cleaning"),("beforeafter","Before & After")]
    btns = "".join(f'<button type="button" data-filter="{k}" aria-pressed="{"true" if k=="all" else "false"}">{t}</button>' for k,t in cats)
    items = "".join(f'<a href="assets/img/{n}-lg.jpg" data-cat="{c}"><figure style="margin:0">{img(n,a)}<figcaption>{e(a)}</figcaption></figure></a>' for n,c,a in GALLERY)
    body = page_hero("Our Work","Cleaning Portfolio","Every photo here is a real space cleaned by Shana and the Maid Lifestyle team — no stock photography.","kitchen-wood") + f'''
<section class="section"><div class="container">
 <div class="filters" role="group" aria-label="Filter photos">{btns}</div>
 <div class="gallery">{items}</div>
 <div class="empty" id="gallery-empty" hidden><h3>Before &amp; After Photos Coming Soon</h3>
  <p>We only show real, matching before-and-after pairs from actual jobs. New comparisons will be added here as they're photographed.</p>
  <a class="btn btn--primary" href="quote.html" style="margin-top:8px">Book Your Clean</a></div>
</div></section>
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Photo viewer">
 <button class="lb-btn lb-close" aria-label="Close">{I['x']}</button><button class="lb-btn lb-prev" aria-label="Previous photo">{I['left']}</button>
 <img alt=""><button class="lb-btn lb-next" aria-label="Next photo">{I['right']}</button><p></p></div>
{cta_band("Want Results Like These?","Request a free quote and let Maid Lifestyle make your space shine.")}'''
    return page("work.html","Our Work — Cleaning Photo Gallery","Photo gallery of kitchens, bathrooms, living areas and bedrooms cleaned by Maid Lifestyle Cleaning Services.", body, "kitchen-wood")

def form_success(msg):
    return f'<div class="form-success" role="status" aria-live="polite"><div class="icon">{I["check"]}</div><h3>Thank you — your request was sent!</h3><p>{msg}</p><p>Need us sooner? Call or text <a href="{TEL}">{PHONE}</a>.</p></div>'

def field(label, name, typ="text", req=False, full=False, attrs=""):
    r = ' <span class="req">*</span>' if req else ""
    fid = "f-" + "".join(c for c in name.lower() if c.isalnum())
    return f'<div class="field{" full" if full else ""}"><label for="{fid}">{label}{r}</label><input id="{fid}" name="{name}" type="{typ}"{" required" if req else ""} {attrs}></div>'

def select(label, name, opts, req=False, full=False, keys=None):
    fid = "f-" + "".join(c for c in name.lower() if c.isalnum())
    o = '<option value="">Select…</option>' + "".join(f'<option{f" data-key={chr(34)}{keys[i]}{chr(34)}" if keys else ""}>{e(x)}</option>' for i,x in enumerate(opts))
    return f'<div class="field{" full" if full else ""}"><label for="{fid}">{label}{" <span class=req>*</span>" if req else ""}</label><select id="{fid}" name="{name}"{" required" if req else ""}>{o}</select></div>'

def radios(label, name, opts, req=False):
    return f'<fieldset class="field full"><span class="label">{label}{" <span class=req>*</span>" if req else ""}</span><div class="choices">' + "".join(f'<label><input type="radio" name="{name}" value="{e(x)}"{" required" if req and i==0 else ""}><span>{e(x)}</span></label>' for i,x in enumerate(opts)) + "</div></fieldset>"

HP = '<div class="hp" aria-hidden="true"><label>Leave blank<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>'

def quote_form():
    return f'''<div class="form-wrap reveal"><form data-lead data-subject="New Quote Request" novalidate>
<fieldset><legend>Your Contact Info</legend><div class="form-grid">
{field("Full name","Name",req=True,attrs='autocomplete="name"')}{field("Phone number","Phone","tel",req=True,attrs='autocomplete="tel" inputmode="tel"')}
{field("Email address","Email","email",req=True,attrs='autocomplete="email"')}{field("Service address","Service address",req=True,attrs='autocomplete="street-address"')}
</div></fieldset>
<fieldset style="margin-top:22px"><legend>About the Cleaning</legend><div class="form-grid">
{select("Type of cleaning needed","Cleaning type",[s["title"] for s in SERVICES]+["Not sure — please advise"],req=True,keys=[s["key"] for s in SERVICES]+["unsure"])}
{select("Approximate property size","Property size",["Under 1,000 sq ft","1,000–1,500 sq ft","1,500–2,000 sq ft","2,000–2,500 sq ft","2,500–3,500 sq ft","3,500+ sq ft","Not sure"])}
{radios("Residential or commercial?","Property type",["Residential","Commercial / Property management"],req=True)}
{select("Bedrooms","Bedrooms",["Studio","1","2","3","4","5","6+"],req=True)}
{select("Bathrooms","Bathrooms",["1","1.5","2","2.5","3","3.5","4+"],req=True)}
{field("Preferred cleaning date","Preferred date","date")}
{radios("How often?","Frequency",["One-time","Weekly","Biweekly","Monthly"],req=True)}
<div class="field full"><label for="f-details">Additional details</label><textarea id="f-details" name="Additional details" placeholder="Pets, condition of the home, areas needing extra attention, gate codes, special requests…"></textarea></div>
</div></fieldset>{HP}
<div class="form-foot"><small>Free estimate · No obligation. Your information is only used to respond to your request.</small><button class="btn btn--primary" type="submit">Request My Free Quote {I['arrow']}</button></div>
<div class="form-status" role="alert"></div></form>{form_success("Shana will review your details and reach out with your quote shortly.")}</div>'''

def quote():
    body = page_hero("Free Estimates","Request a Free Quote","Tell us about your space — it only takes a minute.","double-vanity") + f'''
<section class="section"><div class="container split" style="align-items:start">
 <div>{quote_form()}</div>
 <aside class="reveal"><h2>Prefer to Talk?</h2><p class="lead">Call or text for a quick estimate.</p>
 <div class="contact-cards" style="margin-top:20px">
  <a class="contact-card" href="{TEL}"><span class="icon">{I['phone']}</span><span><small>Call</small><strong>{PHONE}</strong></span></a>
  <a class="contact-card" href="{SMS}"><span class="icon">{I['mail']}</span><span><small>Text</small><strong>{PHONE}</strong></span></a>
  <a class="contact-card" href="mailto:{EMAIL}"><span class="icon">{I['mail']}</span><span><small>Email</small><strong>{EMAIL}</strong></span></a>
 </div>
 <div class="note" style="margin-top:24px"><strong>Property manager or realtor?</strong> Use our <a href="property-managers.html#inquiry">commercial inquiry form</a> for turnovers and multiple units.</div>
 </aside></div></section>'''
    return page("quote.html","Request a Free Cleaning Quote","Request a free estimate for house cleaning, deep cleaning, move-out cleaning or apartment turnover cleaning from Maid Lifestyle.", body, "double-vanity")

def pm():
    who = [("building","Apartment Complexes"),("key","Property Management Companies"),("home","Landlords"),("sign","Real Estate Professionals"),("home","Rental Property Owners"),("spark","Investors")]
    steps = [("Send Your Request","Share the property, number of units and timeline."),("Get a Clear Quote","Upfront pricing for one unit or ongoing turnovers."),("We Clean & Prep","Units cleaned top to bottom and presentation-ready."),("Ready for Residents","Move-in-ready spaces on your schedule.")]
    form = f'''<div class="form-wrap reveal"><form data-lead data-subject="New Commercial / Property Inquiry" novalidate>
<fieldset><legend>Commercial Cleaning Inquiry</legend><div class="form-grid">
{field("Contact name","Contact name",req=True,attrs='autocomplete="name"')}{field("Company / property name","Company")}
{field("Phone number","Phone","tel",req=True,attrs='autocomplete="tel" inputmode="tel"')}{field("Email address","Email","email",req=True,attrs='autocomplete="email"')}
{field("Property address(es)","Property address",full=True)}
{select("I am a…","Client type",["Apartment community","Property management company","Landlord","Real estate agent","Rental property owner","Investor","Other"],req=True)}
{select("Service needed","Service needed",["Apartment turnover cleaning","Vacant unit cleaning","Move-out / move-in prep","Real estate listing prep","Trash-out","Ongoing contract","Other"],req=True)}
{field("Number of units","Number of units","number",attrs='min="1" inputmode="numeric"')}
{select("How often?","Frequency",["One-time","As units turn over","Weekly","Monthly","Not sure yet"])}
<div class="field full"><label for="f-pmdetails">Details</label><textarea id="f-pmdetails" name="Details" placeholder="Unit sizes, timelines, access instructions, recurring needs…"></textarea></div>
</div></fieldset>{HP}
<div class="form-foot"><small>We'll respond with availability and pricing.</small><button class="btn btn--primary" type="submit">Send Commercial Inquiry {I['arrow']}</button></div>
<div class="form-status" role="alert"></div></form>{form_success("Shana will follow up about your properties shortly.")}</div>'''
    body = page_hero("Property Managers & Real Estate","Professional Cleaning Solutions for Property Managers","Keep your properties clean, presentable, and ready for their next residents.","bedroom-2") + f'''
<section class="section"><div class="container split">
 <div class="reveal"><span class="eyebrow">Turnover Cleaning Partner</span><h2>Units Ready When You Are</h2>
 <p class="lead">Keep your properties clean, presentable, and ready for their next residents. Maid Lifestyle provides cleaning solutions for apartment turnovers, vacant units, rental properties, and real estate preparation.</p>
 {ck(["Vacant apartment cleaning","Move-out cleaning & move-in preparation","Unit turnover cleaning","Rental property cleaning","Real estate listing & showing prep","Trash-out services","Flexible scheduling for management teams"])}
 <a class="btn btn--primary" href="#inquiry">Request a Commercial Cleaning Quote</a></div>
 <div class="split__media reveal">{img("hall-bath","Apartment bathroom cleaned and ready for the next resident", size="lg")}<div class="card-float"><strong>Studio – 3 BR</strong><span>Apartment cleaning starts at $95 · deep cleans from $175</span></div></div>
</div></section>
<section class="section section--cream"><div class="container"><div class="head center reveal"><span class="eyebrow">Who We Serve</span><h2>Built for Property Professionals</h2></div>
<div class="grid grid-3">{"".join(f'<article class="feature reveal" style="display:flex;gap:16px;align-items:center"><div class="icon">{I[i]}</div><h3 style="margin:0;font-size:1.35rem">{t}</h3></article>' for i,t in who)}</div></div></section>
<section class="section section--green"><div class="container"><div class="head center reveal"><span class="eyebrow">How It Works</span><h2>A Simple Turnover Process</h2></div>
<div class="steps">{"".join(f'<div class="step reveal"><h3>{t}</h3><p>{d}</p></div>' for t,d in steps)}</div></div></section>
<section class="section" id="inquiry" style="scroll-margin-top:90px"><div class="container" style="max-width:900px">
 <div class="head center reveal"><span class="eyebrow">Commercial Inquiry</span><h2>Request a Commercial Cleaning Quote</h2><p class="lead">Getting a property ready to sell or rent? Let Maid Lifestyle help make it shine.</p></div>{form}</div></section>'''
    return page("property-managers.html","Apartment Turnover & Property Management Cleaning","Apartment turnover cleaning, vacant unit cleaning, rental property and real estate listing cleaning for property managers, landlords and realtors. Request a commercial quote.", body, "bedroom-2")

def contact():
    form = f'''<div class="form-wrap reveal"><form data-lead data-subject="New Website Inquiry" novalidate>
<fieldset><legend>Send an Inquiry</legend><div class="form-grid">
{field("Name","Name",req=True,attrs='autocomplete="name"')}{field("Phone","Phone","tel",attrs='autocomplete="tel" inputmode="tel"')}
{field("Email","Email","email",req=True,full=True,attrs='autocomplete="email"')}
<div class="field full"><label for="f-msg">Message <span class="req">*</span></label><textarea id="f-msg" name="Message" required></textarea></div>
</div></fieldset>{HP}
<div class="form-foot"><small>We typically reply by phone or email.</small><button class="btn btn--primary" type="submit">Send Inquiry {I['arrow']}</button></div>
<div class="form-status" role="alert"></div></form>{form_success("We'll get back to you soon.")}</div>'''
    body = page_hero("Contact","Get in Touch","Questions, scheduling, or a free estimate — we'd love to hear from you.","dining") + f'''
<section class="section"><div class="container split" style="align-items:start">
 <div class="reveal"><h2>{BUSINESS}</h2><p class="lead">Owner: {OWNER} · {e(AREA_TXT)}</p>
 <div class="btn-row" style="margin:22px 0 28px"><a class="btn btn--primary" href="{TEL}">{I['phone']} Call Now</a><a class="btn btn--gold" href="quote.html">Request a Quote</a><a class="btn btn--ghost" href="#inquiry-form">Send an Inquiry</a></div>
 <div class="contact-cards">
  <a class="contact-card" href="{TEL}"><span class="icon">{I['phone']}</span><span><small>Call or text</small><strong>{PHONE}</strong></span></a>
  <a class="contact-card" href="mailto:{EMAIL}"><span class="icon">{I['mail']}</span><span><small>Email</small><strong>{EMAIL}</strong></span></a>
  <a class="contact-card" href="{FACEBOOK_URL}" target="_blank" rel="noopener"><span class="icon">{I['fb']}</span><span><small>Facebook</small><strong>Maid Lifestyle Cleaning Services</strong></span></a>
 </div>
 <div class="note" style="margin-top:24px"><strong>Payment methods</strong><div class="pay"><span>Cash App</span><span>Venmo</span><span>Zelle</span></div><p style="margin:10px 0 0;font-size:.92rem">Certified funds only · No checks</p></div>
 </div>
 <div id="inquiry-form" style="scroll-margin-top:100px">{form}</div>
</div></section>'''
    return page("contact.html","Contact Us","Contact Maid Lifestyle Cleaning Services — call or text 854-274-4871, email themaidlifestylecompany@gmail.com, or send an inquiry online.", body, "dining")

PAGES = {"index.html":home,"services.html":services,"about.html":about,"work.html":work,"quote.html":quote,"property-managers.html":pm,"contact.html":contact}
for f,fn in PAGES.items():
    open(os.path.join(HERE,f),"w").write(fn())
base = SITE_URL or "https://YOUR-DOMAIN.com"
open(os.path.join(HERE,"robots.txt"),"w").write(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
today = datetime.date.today().isoformat()
open(os.path.join(HERE,"sitemap.xml"),"w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{base}/{'' if f=='index.html' else f}</loc><lastmod>{today}</lastmod></url>\n" for f in PAGES) + "</urlset>\n")
print("Built", len(PAGES), "pages", "(SITE_URL not set — sitemap uses placeholder)" if not SITE_URL else "")
