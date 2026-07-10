# Next Steps — Reciprocal Museum Maps

Working notes for upcoming sessions. Status as of **2026-07-10**.

## Current state

- Live on GitHub Pages: https://jimmyvluong.github.io/astc-passport-map/ (ASTC),
  `/narm.html` (NARM), `/states/` (54 state pages), `/privacy.html`
- Repo **public** (temporarily — see migration below). License: source-visible/no-reuse; `tools/` MIT.
- Weekly GitHub Action watches ASTC/NARM PDFs for new releases → opens an issue.
- Decision made: **monetization path** → Cloudflare Pages + private repo + custom domain + (eventually) ads.

## Blocked on Jimmy

1. **Create Cloudflare account** (free plan) at dash.cloudflare.com
2. **Register custom domain** — recommend Cloudflare Registrar (at-cost ~$10/yr).
   Naming decision: this site (e.g. `reciprocalmuseums.com`) vs. future
   kids-activities umbrella brand with maps as first section.

## Migration runbook (once account + domain exist)

1. Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git →
   authorize GitHub → select `astc-passport-map`. Build settings: no framework,
   build command empty, output dir `/` (site is prebuilt static files).
2. Verify the `*.pages.dev` deployment works.
3. Attach custom domain in Pages → Custom domains (auto-DNS if domain is on Cloudflare).
4. Update `BASE_URL` in `tools/build.py` to the new domain; `python tools/build.py`; commit.
5. Flip repo private: `gh repo edit jimmyvluong/astc-passport-map --visibility private --accept-visibility-change-consequences`
   (Cloudflare keeps deploying from private repos; GitHub Pages will stop — that's expected.)
6. Optional: disable GitHub Pages on the repo; add a redirect note if anything linked the old URL.
7. Google Search Console: add property for the new domain (DNS verification via
   Cloudflare), submit `sitemap.xml`. Bing Webmaster Tools too (imports from GSC).

## SEO / growth backlog (after migration)

- Backlink outreach drafts: r/Museums, r/TravelHacks, parenting + homeschool
  communities, science-center member newsletters/forums. Write posts, Jimmy submits.
- "Show HN"-style or blog write-up of the build (earns dev backlinks).
- Watch GSC queries; consider FAQ expansions for terms like "ASTC 90 mile rule",
  "NARM 15 mile rule", "museums with reciprocal membership".

## Feature backlog (roughly prioritized)

1. Parse ASTC per-venue **eligible membership levels** from the PDF → show on cards
   ("is MY membership level covered?" — nobody else answers this).
2. More networks as new map pages: ROAM, Time Travelers, AHS gardens, AZA zoos
   (template + pipeline already generalize).
3. Trip planner: enter a destination city → everything in range, grouped by distance.
4. Ads groundwork when traffic justifies: AdSense application, consent banner,
   update privacy.html, retire "no tracking" claims.
5. Kids-activities umbrella: playgrounds, libraries, story times, free museum days —
   fold reciprocal maps in as the first vertical.

## Maintenance

- When the freshness Action opens an issue: run
  `python tools/update_data.py <astc-pdf-url>` / `python tools/update_narm.py <narm-pdf-url>`,
  then `python tools/build.py`, update `data/source-hashes.json` (URL + sha256), commit.
- ASTC list expires **Oct 31, 2026** — expect a new PDF around then even if the
  Action hasn't fired.
