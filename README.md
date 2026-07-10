# Reciprocal Museum Maps — ASTC Travel Passport + NARM

Fast, personalized, mobile-friendly maps of the two big museum reciprocal-admission networks:

- **ASTC Travel Passport** (`index.html`) — 351 science centers & museums with free
  reciprocal general admission — https://jimmyvluong.github.io/astc-passport-map/
- **NARM** (`narm.html`) — 1,526 art/history museums, gardens, and children's museums —
  https://jimmyvluong.github.io/astc-passport-map/narm.html

## Why better than the existing maps?

Existing options ([astcpassportmap.blogspot.com](https://astcpassportmap.blogspot.com/),
[astcfanmap.com](https://astcfanmap.com/)) show pins. This project models the **rules**:

- **Set your home museum → see *your* map.** ASTC's 90-mile exclusion circles are drawn
  around your home museum and your location; excluded venues are crossed out with the
  reason spelled out. NARM's per-institution 15/50-mile restriction symbols are parsed
  from the official list and applied the same way.
- **Set your location** (geolocate or drop a pin) → distance-sorted list, day-trip
  highlighting (≤120 mi), "My area" view.
- **Per-venue cards**: address, phone, website, Google Maps directions, proof-of-ID flags,
  NARM restriction badges, straight-line distances.
- **Shareable setups** — home museum + location live in the URL hash.
- **No dependencies, no tile servers, no accounts, no tracking** — each map is one
  self-contained HTML file (canvas-rendered basemap), works offline once loaded,
  light & dark theme.
- **Reproducible data pipeline** — regenerate everything from the official PDFs in one
  command when new lists publish.

## Repo layout

```
index.html                  ASTC map (built; GitHub Pages serves it)
narm.html                   NARM map (built)
sitemap.xml, robots.txt     SEO (built)
site/template.html          shared page source; config/data injected at build time
data/participants.json      ASTC dataset (parsed from official PDF, street-level geocodes)
data/narm.json              NARM dataset (parsed from official PDF, city-level geocodes)
data/manual_locations.json  hand-maintained ASTC non-US entries
data/basemap.json           quantized world + US-state polygons (public-domain sources)
tools/update_data.py        ASTC PDF -> participants.json (parse + Census/GeoNames geocode)
tools/update_narm.py        NARM PDF -> narm.json (parse + GeoNames city centroids)
tools/build.py              data + template -> index.html, narm.html, sitemap, robots
```

## Updating when new lists publish

ASTC refreshes ~twice a year (current list: May 1 – Oct 31, 2026). NARM refreshes quarterly.

```sh
pip install pypdf requests
python tools/update_data.py <astc-pdf-url>
python tools/update_narm.py <narm-pdf-url> [path-to-geonames-US.txt]
python tools/build.py
```

Check the update scripts' console output for parse counts and geocoding misses; add manual
coordinates for any misses to the tables at the top of the scripts.

## Roadmap

- [ ] Per-state landing pages ("ASTC museums in California") for long-tail SEO
- [ ] Per-venue eligible membership levels (in the ASTC PDF, not yet parsed)
- [ ] More reciprocal networks: ROAM, Time Travelers, AHS gardens, AZA zoos
- [ ] Trip planner: pick a city → what's in range, grouped by drive time
- [ ] Automated new-PDF detection (GitHub Action)
- [ ] Broader "things to do with kids near you" umbrella project

## Data & attribution

Participant data © [ASTC](https://www.astc.org/) and the
[NARM Association](https://narmassociation.org/) — this is an unofficial fan project; always
call the venue to confirm benefits. Basemap geometry from public-domain Natural Earth
derivatives. Geocoding by the US Census Bureau and GeoNames (CC-BY).
