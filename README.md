# Graze & Rose — Static Site

Full rebuild of grazeandrose.com without Wix. 21 pages of plain HTML + CSS
(Wix's server-rendered presentation markup, pruned of all runtime machinery),
plus one small vanilla-JS file for forms, galleries, and date pickers.

## Deploy (GitHub Pages)

Push to `main`; Pages serves the repo root. `.nojekyll` must stay so the
`_assets/` directory is served. No build step.

## Structure

- `index.html`, `<page>/index.html` — one folder per page, mirrors the live
  site's URL structure (including `catering-packages/cateringpackagesinquiry`
  style nested pages)
- `css/` — deduplicated Wix style blocks (one file per unique block, hashed)
- `site.css` — small static-site additions: dropdown menu open/close, gallery
  slide visibility, date-picker support
- `site.js` — vanilla JS: inquiry forms compose a `mailto:` to
  grazecatercda@gmail.com, galleries auto-advance with Wix's own arrows and
  counter, date pickers use the native control
- `_assets/` — images, fonts, and CSS captured from the live site (only what
  the pages reference)
- `_files/` — linked documents (catering service terms PDF)

## Notes

- Forms submit via the visitor's email client (Wix's backend doesn't exist
  off-platform). Fields are compiled into a formatted email body.
- Desktop rendering is pixel-identical to the live site (same DOM, same CSS).
  Small screens get a simple stacked layout via `site.css`.
- The 10 live pages that no menu or footer links to (dessertgraze, kidsgraze,
  gifts, etc.) were intentionally dropped; the 21 linked pages are all here.

## Rebuild tooling

`.build/` holds the pipeline that produced this site from the original Wix
mirror: `graph.py` (link-graph page set), `prune_site.py` (the builder),
`fetch_renditions.py` (live wixstatic image renditions), `shoot_pairs.py` +
`diff.py` (pixel-parity verification vs the original mirror).
