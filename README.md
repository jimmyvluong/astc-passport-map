# ASTC Travel Passport Map

An interactive, fast, mobile-friendly map of every science center and museum in the
[ASTC Travel Passport Program](https://www.astc.org/passport/) — the reciprocal-admission
program that gets members of one participating science center free general admission at
~350 others worldwide.

**Live site:** https://jimmyvluong.github.io/astc-passport-map/

## Why another ASTC map?

Existing maps ([astcpassportmap.blogspot.com](https://astcpassportmap.blogspot.com/),
[astcfanmap.com](https://astcfanmap.com/)) show pins. This project aims further:

- **Distance-sorted list + search** — plan a trip, don't just browse pins
- **90-mile exclusion zone drawn on the map** — the Passport rule everyone forgets;
  venues inside it render as excluded so you don't drive to a museum that won't take your card
- **Proof-of-residence flags** on every venue that requires photo ID
- **Per-venue detail card** — address, phone, website, straight-line distances
- **No dependencies, no tile servers, no tracking** — a single self-contained HTML file
  (canvas-rendered basemap), works offline once loaded, light & dark theme
- **Reproducible data pipeline** — regenerate everything from the official ASTC PDF in one command

## Repo layout

```
index.html                  built site (committed so GitHub Pages serves it)
site/template.html          page source; data placeholders injected at build time
data/participants.json      canonical dataset parsed from the official ASTC list
data/manual_locations.json  hand-maintained non-US entries (Canada + international)
data/basemap.json           quantized world + US-state polygons (public-domain sources)
tools/update_data.py        official PDF -> participants.json (parse + geocode)
tools/build.py              data + template -> index.html
```

## Updating when ASTC publishes a new list

ASTC refreshes the participant PDF roughly twice a year (the current list covers
May 1 – Oct 31, 2026). To rebuild:

```sh
pip install pypdf requests
python tools/update_data.py <url-or-path-of-new-pdf>
python tools/build.py
```

US addresses are geocoded with the free US Census Bureau batch geocoder; misses fall
back to GeoNames ZIP centroids (marked `zip-centroid` in the data and "Location
approximate" in the UI). Canada/international entries live in
`data/manual_locations.json` — check them by hand against the new PDF.

Home base (day-trip highlight) and exclusion center are constants at the top of
`tools/build.py`.

## Roadmap

- [ ] User-settable home base & home museum (URL params / localStorage) instead of build-time constants
- [ ] Exclusion zone computed from the user's home museum *and* residence (the actual Passport rule)
- [ ] Per-venue eligible membership levels (in the PDF, not yet parsed)
- [ ] Driving-time isochrones or at least driving distance
- [ ] Trip planner: pick a city, list what's in range
- [ ] Automated check for a new ASTC PDF (GitHub Action)

## Data & attribution

Participant data © [ASTC](https://www.astc.org/) — this is an unofficial fan project;
always call the venue to confirm benefits. Passport benefits cover **general admission
only** and exclude venues within 90 straight-line miles of your home museum or residence.
Basemap geometry from public-domain Natural Earth derivatives. Geocoding by the
US Census Bureau and GeoNames (CC-BY).
