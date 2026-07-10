"""Build index.html from site/template.html + data/*.json.

Usage:  python tools/build.py
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Reference points for distance columns. HOME drives the "day trip" highlight;
# EXCLUSION drives the 90-mile Passport exclusion zone (home museum / residence).
HOME = (33.8169, -118.0373)       # Cypress, CA
EXCLUSION = (38.5816, -121.4944)  # Sacramento, CA


def dist_mi(lat1, lng1, lat2, lng2):
    R = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def main():
    data = json.loads((ROOT / "data" / "participants.json").read_text(encoding="utf-8"))
    basemap = (ROOT / "data" / "basemap.json").read_text(encoding="utf-8")

    rows = []
    for p in data["participants"]:
        rows.append([
            p["name"], p["street"], p["city"], p["state"], p["region"],
            p["phone"], p["url"], 1 if p["proofOfResidence"] else 0,
            p["lat"], p["lng"],
            round(dist_mi(*HOME, p["lat"], p["lng"])),
            round(dist_mi(*EXCLUSION, p["lat"], p["lng"])),
            0 if p["geoPrecision"] == "exact" else 1,
        ])

    template = (ROOT / "site" / "template.html").read_text(encoding="utf-8")
    html = template.replace("/*__BASEMAP__*/[]", basemap)
    html = html.replace("/*__ROWS__*/[]", json.dumps(rows, separators=(",", ":"), ensure_ascii=False))
    out = ROOT / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size // 1024} KB, {len(rows)} participants)")


if __name__ == "__main__":
    main()
