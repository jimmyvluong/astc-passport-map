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
                   "ahead to confirm. Unofficial fan project — data © ASTC."),
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
                   "data © NARM Association."),
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

    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f" <url><loc>{BASE_URL}/{f}</loc></url>\n" for f in PROGRAMS)
        + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    print("wrote sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
