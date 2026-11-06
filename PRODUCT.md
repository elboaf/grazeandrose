# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Plain static HTML/CSS (no build step, no framework) — a semantic reimplementation of the original Wix render. Deployed as a static site on GitHub Pages at `elboaf.github.io/grazeandrose/` (the custom domain is not wired; root-absolute paths 404 — all refs must be relative with correct depth: root pages none, nested pages `../`).

## Users

Primary: couples, party hosts, and corporate/social event organizers in North Idaho and Eastern Washington (Coeur d'Alene, Post Falls, Hayden, Rathdrum, Sandpoint; Spokane, Spokane Valley, Cheney) looking for luxury charcuterie-style catering. Job: browse offerings and packages, then inquire by email. Secondary audience: hobbyists interested in the owner's charcuterie styling workshops.

## Product Purpose

Marketing site for Graze and Rosé Catering, a boutique charcuterie-style grazing platter/table/brunch catering business based in Post Falls, Idaho. Success = a visitor understands the offerings, trusts the quality (photography-led proof), and sends an email inquiry.

## Positioning

Luxury charcuterie-style grazing boards, platters, and tables where every provision is styled by hand with flowers and herbs — display-as-centerpiece, not just food. Owner-led, personal service (one stylist, not a production kitchen), plus hands-on styling workshops.

## Operating Context

- 21-page static set: home, offerings (5 sub-pages), workshops, about, contact/FAQs, 4 inquiry pages, catering packages, and supporting legal/terms pages.
- Contact is **email-only by design**: `Grazecatercda@gmail.com` mailto links (no form backend, ever). Inquiry pages use simple forms; the owner answers within 24 hours.
- Free delivery within 10 miles of Post Falls, ID; $0.70/mile beyond. Socials: Instagram/Facebook `graze.and.rose`.
- Owner iterates visually by dropping AI studio re-renders into `ai-images/` (gitignored); shipping copies go to `_assets/` byte-for-byte.

## Capabilities and Constraints

- Exactly the current 21-page set — do not add or remove pages.
- No form backend; no client JS framework (`site.js` is minimal).
- The hashed `css/b*.css` cascade comes from the Wix rebuild; **its load order is load-bearing** — never reorder, merge, or rename. `site.css` loads last as the owner's override layer and its gallery-visibility override is load-bearing.
- Nested pages are one directory deep; relative `../` depth must match in both `src` and `srcset`.
- Owner-supplied renders ship byte-for-byte: never crop, resize, recompress, or "optimize" them. Containers fit the page to the image via `aspect-ratio` (hero 4096/768, strip 4096/512, offerings column 4096/6144); never reintroduce fixed pixel heights on those slots.
- Live-mode variant latitude (owner-confirmed): variants may push layout and color structure noticeably, but must keep the brand markers — blush/rosé surfaces, the framed logo plaque header, provisions-led photography.

## Brand Commitments

- Name: **Graze and Rosé Catering**; tagline: **"Bring Something New to the Table!"**
- Voice: warm, enthusiastic hospitality — "luxury", "beautiful provisions", "stunning presentation"; run-on ingredient lists; exclamation used sparingly.
- Signature visuals: framed logo plaque in the white header (flanked by thin rules); double thin-line flourish ornament above the footer on every page; sage-green active-nav block.
- Binding imagery: owner-approved AI studio renders (`_assets/studio/`) are sanctioned replacements — not parity violations, never to be flagged or "fixed".

## Evidence on Hand

- Real menu copy on every page (e.g., Brunch Graze: "Cold smoked salmon, candied bacon, Canadian bacon roses, prosciutto rolls, fancy eggs…").
- Owner-supplied studio renders in `_assets/studio/` (hero 4096×768, strip 4096×512, offerings column 4096×6144).
- The live Wix original as historical evidence. No testimonials, press, or awards exist — do not fabricate any.

## Product Principles

1. **Photography is the product.** Provisions styled like florals lead every page; furniture and chrome recede.
2. **Email is the conversion path.** Every page routes interest to the mailto inquiry.
3. **Personal, local, 24-hour service.** One stylist's voice, not an agency's; delivery radius and service areas are stated plainly.
4. **Owner imagery is sacrosanct.** Renders ship byte-for-byte; fit the page to the image, never the reverse.
