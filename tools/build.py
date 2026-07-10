"""Build the site: index.html (ASTC), narm.html (NARM), sitemap.xml, robots.txt.

Usage:  python tools/build.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://jimmyvluong.github.io/astc-passport-map"  # update when custom domain lands


def astc_rows():
    data = json.loads((ROOT / "data" / "participants.json").read_text(encoding="utf-8"))
    return [[p["name"], p["street"], p["city"], p["state"], p["region"], p["phone"],
             p["url"], 1 if p["proofOfResidence"] else 0, p["lat"], p["lng"],
             0 if p["geoPrecision"] == "exact" else 1, ""]
            for p in data["participants"]], data


def narm_rows():
    data = json.loads((ROOT / "data" / "narm.json").read_text(encoding="utf-8"))
    return [[p["name"], "", p["city"], p["state"], p["country"], p["phone"],
             "", 0, p["lat"], p["lng"], 1, p["symbols"]]
            for p in data["participants"]], data


ASTC_ABOUT = """
<h2>ASTC Travel Passport Map</h2>
<p>The <a href="https://www.astc.org/passport/" target="_blank" rel="noopener">ASTC Travel
Passport Program</a> is a reciprocal-admission network run by the Association of Science and
Technology Centers: members of one participating science center or museum get <b>free general
admission</b> at the other participating institutions when they travel.</p>
<h3>How the 90-mile rule works</h3>
<p>Passport benefits are excluded at venues within <b>90 miles straight-line ("as the crow
flies")</b> of either (1) the science center where you hold your membership, or (2) your
residence. Set your home museum and your location above and this map draws both exclusion
circles and crosses out the venues they remove — so you never drive to a museum that won't
honor your card.</p>
<h3>What's included — and what isn't</h3>
<ul>
<li>Free <b>general admission only</b>: special exhibits, planetarium shows, and giant-screen
theaters are typically not included.</li>
<li>Venues marked "Photo ID required" check proof of residence — bring ID along with your
membership card.</li>
<li>Membership levels matter: check that your level is Passport-eligible at your home museum,
and call the destination before you visit.</li>
</ul>
<h3>About this map</h3>
<p>Built from the official ASTC participant list and rebuilt each season. Locations are
geocoded from the published street addresses. Your home museum and location are stored only
in your browser — no accounts, no tracking, and the whole map works offline once loaded.
This is an unofficial fan project; data belongs to ASTC and the listed institutions.
Source code on <a href="https://github.com/jimmyvluong/astc-passport-map" target="_blank"
rel="noopener">GitHub</a>.</p>
"""

NARM_ABOUT = """
<h2>NARM Reciprocal Museum Map</h2>
<p>The <a href="https://narmassociation.org/" target="_blank" rel="noopener">North American
Reciprocal Museum (NARM) Association</a> connects 1,500+ art museums, history museums,
botanical gardens, and children's museums: a NARM-level membership at one institution gets
you free member admission (and often shop discounts) at all the others.</p>
<h3>How NARM restrictions work</h3>
<p>Unlike ASTC's blanket 90-mile rule, NARM restrictions are per-institution, marked with
symbols in the official list:</p>
<ul>
<li><b>**</b> / <b>***</b> — the institution does not honor NARM for members of museums
within <b>15 miles</b> of it.</li>
<li><b>#</b> — same, but a <b>50-mile</b> radius.</li>
<li><b>*</b> — benefits may be restricted for concerts, lectures, special exhibitions, and
ticketed events.</li>
<li><b>^</b> — reciprocity may be restricted for members of institutions that restrict this
one.</li>
</ul>
<p>Set your home museum above and the map crosses out the institutions whose radius rule
excludes you. Locations are city-level (the NARM list publishes no street addresses), so
tap through to directions for the exact spot.</p>
<h3>About this map</h3>
<p>Built from the official NARM member list, rebuilt each quarter. Your settings stay in
your browser — no accounts, no tracking. This is an unofficial fan project; data belongs to
the NARM Association and the listed institutions. Source code on
<a href="https://github.com/jimmyvluong/astc-passport-map" target="_blank" rel="noopener">GitHub</a>.</p>
"""


def faq_jsonld(qas):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qas
        ],
    }


PROGRAMS = {
    "index.html": {
        "program": "astc",
        "title": "ASTC Travel Passport Map — Interactive Map of All Participating Science Centers",
        "desc": ("Interactive map of all ASTC Travel Passport science centers and museums with free "
                 "reciprocal admission. Set your home museum to see your personal 90-mile exclusion "
                 "zone, search, sort by distance, and plan day trips."),
        "h1": "ASTC Travel Passport Map",
        "other_href": "narm.html",
        "other_label": "NARM map",
        "footer": ("<b>Passport rules:</b> free <b>general admission only</b> — special exhibits, planetariums, "
                   "and giant-screen theaters are not included. Venues within 90 straight-line miles of your home "
                   "museum <b>or</b> residence are excluded. Bring your membership card and photo ID, and call "
                   "ahead to confirm. Unofficial fan project — data © ASTC. "
                   '<a href="states/" style="color:inherit">Browse by state</a> · '
                   '<a href="privacy.html" style="color:inherit">Privacy</a>'),
        "about": ASTC_ABOUT,
        "faq": [
            ("What is the ASTC Travel Passport Program?",
             "A reciprocal admission program from the Association of Science and Technology Centers: members of one participating science center get free general admission at 350+ other participating science centers and museums worldwide."),
            ("How does the ASTC 90-mile rule work?",
             "Passport benefits are excluded at science centers within 90 straight-line miles of your home museum or of your residence. The distance is measured as the crow flies, not driving distance."),
            ("Does the ASTC Passport include special exhibits or planetarium shows?",
             "No. The benefit covers free general admission only. Special exhibits, planetarium and giant-screen theater shows, and museum store discounts are not included unless the venue states otherwise."),
            ("What should I bring to use my ASTC Passport benefit?",
             "Your membership card and a photo ID — many venues require proof of residence. Calling ahead to confirm your membership level is Passport-eligible is recommended."),
        ],
    },
    "narm.html": {
        "program": "narm",
        "title": "NARM Reciprocal Museum Map — 1,500+ Museums with Free Member Admission",
        "desc": ("Interactive map of all North American Reciprocal Museum (NARM) Association members. "
                 "Set your home museum to see which 15- and 50-mile restrictions apply to you, search "
                 "1,500+ art museums, gardens, and history museums, and plan visits."),
        "h1": "NARM Reciprocal Museum Map",
        "other_href": "index.html",
        "other_label": "ASTC map",
        "footer": ("<b>NARM basics:</b> free member admission at 1,500+ institutions. Symbols in the official list "
                   "mark restrictions — 15/50-mile home-museum radius rules and special-event exclusions — shown on "
                   "each venue's card here. Locations are city-level. Call ahead to confirm. Unofficial fan project — "
                   "data © NARM Association. "
                   '<a href="states/" style="color:inherit">Browse by state</a> · '
                   '<a href="privacy.html" style="color:inherit">Privacy</a>'),
        "about": NARM_ABOUT,
        "faq": [
            ("What is NARM reciprocal membership?",
             "The North American Reciprocal Museum (NARM) Association is a network of 1,500+ museums, galleries, and gardens. A NARM-qualifying membership at one institution grants free member admission at all the others."),
            ("Does NARM have a distance exclusion rule like ASTC?",
             "Not a blanket one. Individual institutions opt into restrictions: ** means no benefits for members of museums within 15 miles, # means 50 miles, and * means special exhibitions and ticketed events may be excluded."),
            ("How do I know if a NARM museum will honor my membership?",
             "Check the venue's restriction symbols on its card in this map, make sure your membership card carries the NARM sticker or logo, and call ahead — institutions can change their policies."),
        ],
    },
}


STATE_NAMES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'DC': 'Washington, D.C.',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois',
    'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
    'ME': 'Maine', 'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan',
    'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana',
    'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota',
    'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
    'PR': 'Puerto Rico', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
    'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia',
    'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
}

CONTENT_CSS = """
:root{--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--hair:#e1e0d9;--blue:#2a78d6;--chipbg:#f1f0ec}
@media (prefers-color-scheme: dark){:root{--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;
--ink2:#c3c2b7;--muted:#898781;--hair:#2c2c2a;--blue:#3987e5;--chipbg:#242423}}
:root[data-theme="light"]{--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;
--muted:#898781;--hair:#e1e0d9;--blue:#2a78d6;--chipbg:#f1f0ec}
:root[data-theme="dark"]{--page:#0d0d0d;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;
--muted:#898781;--hair:#2c2c2a;--blue:#3987e5;--chipbg:#242423}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);
font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:760px;margin:0 auto;padding:28px 20px 60px}
h1{font-size:24px;letter-spacing:-.01em;line-height:1.25;text-wrap:balance;margin:10px 0 6px}
h2{font-size:17px;margin:30px 0 8px}
p,li{color:var(--ink2);max-width:68ch}
a{color:var(--blue);text-decoration:none} a:hover{text-decoration:underline}
.crumb{font-size:12.5px;color:var(--muted)}
.mapbtns{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0 4px}
.mapbtns a{font-size:13px;padding:7px 14px;border-radius:999px;background:var(--chipbg);
border:1px solid var(--hair)}
ul.venues{list-style:none;padding:0;margin:8px 0}
ul.venues li{padding:9px 0;border-bottom:1px solid var(--hair);color:var(--ink2);font-size:13.5px}
ul.venues b{color:var(--ink);font-weight:600;font-size:14.5px;display:block}
.tag{font-size:11px;padding:2px 8px;border-radius:999px;background:var(--chipbg);
color:var(--ink2);white-space:nowrap;margin-left:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:8px;
list-style:none;padding:0}
.grid a{display:flex;justify-content:space-between;gap:8px;padding:9px 12px;
border:1px solid var(--hair);border-radius:8px;background:var(--surface);color:var(--ink)}
.grid .n{color:var(--muted);font-variant-numeric:tabular-nums}
footer{border-top:1px solid var(--hair);margin-top:44px;padding-top:14px;
font-size:12px;color:var(--muted)}
"""


def page_shell(title, desc, canonical, body):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#128301;</text></svg>">
<style>{CONTENT_CSS}</style>
</head>
<body>
<main>
{body}
<footer>Unofficial fan project — participant data © ASTC and NARM Association.
Always call the venue to confirm reciprocal benefits.
· <a href="../index.html">ASTC map</a> · <a href="../narm.html">NARM map</a>
· <a href="../privacy.html">Privacy</a></footer>
</main>
</body>
</html>
"""


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_state_pages(astc, narm):
    out_dir = ROOT / "states"
    out_dir.mkdir(exist_ok=True)
    year = "2026"

    def astc_li(p):
        bits = []
        if p["url"]:
            u = p["url"] if p["url"].startswith("http") else "https://" + p["url"]
            bits.append(f'<a href="{esc(u)}" target="_blank" rel="noopener">Website</a>')
        if p["phone"]:
            bits.append(esc(p["phone"]))
        tail = " · ".join(bits)
        tag = '<span class="tag">Photo ID required</span>' if p["proofOfResidence"] else ""
        return (f'<li><b>{esc(p["name"])}{tag}</b>'
                f'{esc(p["street"])}, {esc(p["city"])} · {tail}</li>')

    def narm_li(p):
        syms = f' <span class="tag">{esc(p["symbols"])} — see restriction key</span>' if p["symbols"] else ""
        phone = f' · {esc(p["phone"])}' if p["phone"] else ""
        return f'<li><b>{esc(p["name"])}{syms}</b>{esc(p["city"])}{phone}</li>'

    narm_key = """<p><small>Restriction key: <b>**</b>/<b>***</b> = no benefit if your home
museum is within 15 miles · <b>#</b> = 50 miles · <b>*</b> = special exhibits/ticketed
events may be excluded · <b>^</b> = may restrict reciprocity.</small></p>"""

    # group by US state code; Canada and everything else get their own pages
    groups = {}
    for p in astc["participants"]:
        code = p["state"] if p["state"] in STATE_NAMES and p["region"] not in ("Canada",) else (
            "canada" if p["region"] == "Canada" else "international")
        groups.setdefault(code, {"astc": [], "narm": []})["astc"].append(p)
    for p in narm["participants"]:
        code = p["state"] if p["state"] in STATE_NAMES and p["country"] == "United States" else (
            p["state"] if p["state"] in STATE_NAMES and p["country"] == "Puerto Rico" else
            "canada" if p["country"] == "Canada" else "international")
        groups.setdefault(code, {"astc": [], "narm": []})["narm"].append(p)

    def title_for(code):
        if code == "canada":
            return "Canada"
        if code == "international":
            return "International"
        return STATE_NAMES[code]

    def slug_for(code):
        if code in ("canada", "international"):
            return code
        return STATE_NAMES[code].lower().replace(",", "").replace(".", "").replace(" ", "-")

    index_items = []
    pages = []
    for code, g in sorted(groups.items(), key=lambda kv: title_for(kv[0])):
        name = title_for(code)
        slug = slug_for(code)
        na, nn = len(g["astc"]), len(g["narm"])
        total = na + nn
        title = f"Reciprocal Museums in {name} ({year}): ASTC & NARM List and Map"
        desc = (f"{name} has {na} ASTC Travel Passport science center{'s' if na != 1 else ''} with free "
                f"reciprocal admission and {nn} NARM member museum{'s' if nn != 1 else ''}. "
                f"Full {year} list with an interactive map, exclusion-rule checks, and directions.")
        qa = f"../index.html#q={name.replace(' ', '%20')}" if code in ("canada", "international") \
            else f"../index.html#q={code}"
        qn = f"../narm.html#q={name.replace(' ', '%20')}" if code in ("canada", "international") \
            else f"../narm.html#q={code}"
        body = [f'<p class="crumb"><a href="./">All states</a> › {esc(name)}</p>',
                f"<h1>Reciprocal Museums in {esc(name)}</h1>",
                f"<p>{esc(name)} has <b>{total}</b> museums in the two big reciprocal-admission "
                f"networks: <b>{na}</b> in the ASTC Travel Passport program (free general admission "
                f"for science-center members) and <b>{nn}</b> in NARM (free member admission at "
                f"art, history, and children's museums). Open the interactive maps to set your own "
                f"home museum — they compute which venues the 90-mile and 15/50-mile exclusion "
                f"rules remove for you.</p>",
                '<div class="mapbtns">']
        if na:
            body.append(f'<a href="{qa}">Open {esc(name)} on the ASTC map →</a>')
        if nn:
            body.append(f'<a href="{qn}">Open {esc(name)} on the NARM map →</a>')
        body.append('</div>')
        if na:
            body.append(f"<h2>ASTC Travel Passport science centers ({na})</h2><ul class='venues'>")
            body += [astc_li(p) for p in sorted(g["astc"], key=lambda p: p["name"])]
            body.append("</ul>")
        if nn:
            body.append(f"<h2>NARM member museums ({nn})</h2>")
            body.append(narm_key)
            body.append("<ul class='venues'>")
            body += [narm_li(p) for p in sorted(g["narm"], key=lambda p: (p["city"], p["name"]))]
            body.append("</ul>")
        (out_dir / f"{slug}.html").write_text(
            page_shell(title, desc, f"{BASE_URL}/states/{slug}.html", "\n".join(body)),
            encoding="utf-8")
        pages.append(f"states/{slug}.html")
        index_items.append(f'<a href="{slug}.html">{esc(name)}<span class="n">{total}</span></a>')

    idx_body = (
        '<p class="crumb"><a href="../index.html">ASTC map</a> · <a href="../narm.html">NARM map</a></p>'
        "<h1>Reciprocal Museums by State</h1>"
        "<p>Every ASTC Travel Passport science center and NARM member museum, grouped by state. "
        "Numbers show total reciprocal venues. Each page links into the interactive maps, which "
        "can compute your personal exclusion zones.</p>"
        '<ul class="grid">' + "".join(f"<li>{it}</li>" for it in index_items) + "</ul>")
    (out_dir / "index.html").write_text(
        page_shell(f"Reciprocal Museums by State ({year}) — ASTC & NARM Lists",
                   "State-by-state lists of ASTC Travel Passport science centers and NARM "
                   "reciprocal museums, with interactive maps and exclusion-rule checks.",
                   f"{BASE_URL}/states/", idx_body),
        encoding="utf-8")
    pages.append("states/")
    print(f"wrote {len(pages) - 1} state pages + states/index.html")
    return pages


def build_privacy():
    body = """<p class="crumb"><a href="index.html">ASTC map</a> · <a href="narm.html">NARM map</a></p>
<h1>Privacy</h1>
<p>This site is a static set of pages with no accounts, no analytics scripts, no ads, and no
cookies.</p>
<h2>What is stored</h2>
<p>Your home museum and location settings are saved in your browser's <b>localStorage</b> so
the maps remember them between visits. They never leave your device — there is no server to
send them to. Clearing your browser data removes them. If you use "share" links, your chosen
home museum and coordinates are encoded in the URL you share.</p>
<h2>Device location</h2>
<p>The "Use device location" button asks your browser for your position once, to center the
map and compute distances. The coordinates stay in your browser subject to the above.</p>
<h2>Hosting, map tiles &amp; external links</h2>
<p>Pages are served by our hosting provider, which may log standard request metadata (IP
address, user agent) to operate the service. When the <b>Streets</b> or <b>Satellite</b>
base-map layer is selected (Streets is the default), map images are fetched from
OpenStreetMap and Esri tile servers respectively — those services receive your IP address
and the map areas you view, under their own privacy policies. The <b>Simple</b> layer makes
no external requests at all. Directions links open Google Maps, and venue website links
open the venue's own site.</p>
<h2>Changes</h2>
<p>If advertising is ever added, this policy and an in-page consent notice will be updated
first.</p>
<h2>Contact</h2>
<p>Questions or corrections: open an issue on
<a href="https://github.com/jimmyvluong/astc-passport-map/issues" target="_blank"
rel="noopener">GitHub</a>.</p>"""
    html = page_shell("Privacy — Reciprocal Museum Maps",
                      "Privacy policy for the ASTC Travel Passport and NARM reciprocal museum "
                      "maps: settings stay in your browser; no accounts, analytics, or cookies.",
                      f"{BASE_URL}/privacy.html", body).replace('href="../', 'href="')
    (ROOT / "privacy.html").write_text(html, encoding="utf-8")
    print("wrote privacy.html")


def main():
    template = (ROOT / "site" / "template.html").read_text(encoding="utf-8")
    basemap = (ROOT / "data" / "basemap.json").read_text(encoding="utf-8")

    datasets = {"astc": astc_rows(), "narm": narm_rows()}
    for fname, cfg in PROGRAMS.items():
        rows, data = datasets[cfg["program"]]
        season = data.get("source", "")
        sub = f"{len(rows):,} participating institutions · {season.split(',')[-1].strip() if cfg['program']=='astc' else 'official member list'} · free, no sign-up"
        jsonld = json.dumps([
            {"@context": "https://schema.org", "@type": "WebApplication",
             "name": cfg["h1"], "url": f"{BASE_URL}/{fname}",
             "applicationCategory": "TravelApplication",
             "operatingSystem": "Any",
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
             "description": cfg["desc"]},
            faq_jsonld(cfg["faq"]),
        ], ensure_ascii=False)

        html = (template
                .replace("__TITLE__", cfg["title"])
                .replace("__DESC__", cfg["desc"])
                .replace("__CANONICAL__", f"{BASE_URL}/{fname}")
                .replace("__JSONLD__", jsonld)
                .replace("__H1__", cfg["h1"])
                .replace("__SUB__", sub)
                .replace("__OTHER_HREF__", cfg["other_href"])
                .replace("__OTHER_LABEL__", cfg["other_label"])
                .replace("__ABOUT__", cfg["about"])
                .replace("__FOOTER__", cfg["footer"])
                .replace("/*__CONFIG__*/{}", json.dumps({"program": cfg["program"]}))
                .replace("/*__BASEMAP__*/[]", basemap)
                .replace("/*__ROWS__*/[]", json.dumps(rows, separators=(",", ":"), ensure_ascii=False)))
        out = ROOT / fname
        out.write_text(html, encoding="utf-8")
        print(f"wrote {fname} ({out.stat().st_size // 1024} KB, {len(rows)} rows)")

    state_pages = build_state_pages(datasets["astc"][1], datasets["narm"][1])
    build_privacy()

    all_pages = list(PROGRAMS) + state_pages + ["privacy.html"]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f" <url><loc>{BASE_URL}/{f}</loc></url>\n" for f in all_pages)
        + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    print("wrote sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
