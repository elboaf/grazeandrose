---
name: Graze and Rosé Catering
description: Luxury charcuterie-style grazing platters, tables, and workshops — Post Falls, Idaho
colors:
  page-blush: "#F6CFB7"
  band-blush: "#F5DDD0"
  footer-gray: "#E8E6E6"
  hairline-gray: "#C7C7C7"
  furniture-white: "#FFFFFF"
  text-warm-black: "#3E362E"
  body-gray: "#757575"
  dropdown-ink: "#2F2E2E"
  rose-berry: "#9F2747"
  rose-berry-hover: "rgba(159,39,71,.7)"
  rose-light: "#DFA7B6"
  rose-mid: "#BF778A"
  peach-link: "#F8D1C2"
  peach-frame: "#FFE0D4"
  sage-active: "#5F7355"
  taupe-card: "#605E5E"
  taupe-card-border: "#E6DECA"
  cc-link: "#5F574E"
typography:
  display:
    fontFamily: "baskervillemtw01-smbdit, baskervillemtw05-smbdit, serif"
    fontSize: "50px"
    fontWeight: 400
    lineHeight: 1.9
    letterSpacing: "0em"
  title:
    fontFamily: "spinnaker, sans-serif"
    fontSize: "39px"
    fontWeight: 400
    lineHeight: 1.2
  subhead:
    fontFamily: "spinnaker, sans-serif"
    fontSize: "33px"
    fontWeight: 400
    lineHeight: 1.4
  button-label:
    fontFamily: "baskervillemtw01-smbdit, baskervillemtw05-smbdit, serif"
    fontSize: "33px"
    fontWeight: 400
    letterSpacing: "0.05em"
  intro:
    fontFamily: "spinnaker, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0.06em"
  body:
    fontFamily: "spinnaker, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.4
  label:
    fontFamily: "spinnaker, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.4
rounded:
  pill: "60px"
  pill-full: "300px"
  card: "5px"
  plaque: "3px"
  square: "0px"
components:
  nav-active:
    backgroundColor: "{colors.sage-active}"
    textColor: "{colors.furniture-white}"
  pill-cta:
    backgroundColor: "{colors.taupe-card}"
    textColor: "{colors.furniture-white}"
    rounded: "{rounded.pill-full}"
  button-stylable:
    backgroundColor: "{colors.furniture-white}"
    textColor: "{colors.body-gray}"
    rounded: "{rounded.pill}"
  button-stylable-hover:
    backgroundColor: "{colors.body-gray}"
    textColor: "{colors.furniture-white}"
  button-classic:
    backgroundColor: "{colors.rose-berry}"
    textColor: "{colors.furniture-white}"
    rounded: "{rounded.square}"
---

# Design System: Graze and Rosé Catering

## Overview

**Creative North Star: "The Styled Board Atelier"** *(current incumbent; owner is still exploring — "The Provisions Larder" and "Garden-Party Editorial" remain live candidates for a future redesign, and a redesign must route through new-work, not edit this file ad hoc.)*

A hand-styled provisions atelier rendered as a website: warm blush and rosé page surfaces, white furniture, and full-bleed photography of grazing boards styled like floral arrangements. The header is a gallery plaque — the framed logo hung between thin rules on a white wall — and every page closes with a delicate double-line flourish above the footer. Type is quiet and even: Spinnaker's humanist sans for everything textual, Baskerville reserved for display moments and the pill buttons' serif labels. Saturated color appears only twice — the berry-rose classic button and the sage active-nav block — so the food carries the chroma.

**Key Characteristics:**
- Photography-first pages; pre-rendered full-bleed bands lock to their true aspect ratios
- 980px centered site column with full-width color bands (blush, peach-blush, gray)
- White header with framed logo plaque + flanking thin rules; flourish ornament above footer
- Peach-on-photo type over dimmed photography; sage block marks where you are
- Rounded-soft forms (60px pills) against square 0px classic buttons and 1px-framed cards

## Colors

A warm rosé hospitality palette: blush-peach surfaces, gray furniture bands, and two saturated accents (berry rose, sage) used sparingly.

### Primary
- **Rose Berry** (#9F2747): classic buttons and inquiry-form controls (hover rgba(159,39,71,.7)). The only saturated red-violet moment; treated as a command color, not decoration.

### Secondary
- **Sage Active** (#5F7355): the active nav item's block, white text. The site's single "you are here" signal — never used decoratively.
- **Peach Link** (#F8D1C2): underlined card titles on offerings; links living on photo/dim surfaces.
- **Peach Frame** (#FFE0D4): the 4px border of the homepage tagline panel.

### Tertiary
- **Rose Light** (#DFA7B6) / **Rose Mid** (#BF778A): registered ramp accents, rarely surfaced.

### Neutral
- **Page Blush** (#F6CFB7): homepage page background.
- **Band Blush** (#F5DDD0): title bands and section strips on offerings/home.
- **Footer Gray** (#E8E6E6): footer band and the homepage about-strip.
- **Hairline Gray** (#C7C7C7): header's 2px bottom rule; disabled fills.
- **Furniture White** (#FFFFFF): header, dropdown, cards, text on photos.
- **Text Warm Black** (#3E362E): nav labels.
- **Body Gray** (#757575): body text and stylable-button labels.
- **Dropdown Ink** (#2F2E2E): dropdown items.
- **Taupe Card** (#605E5E, border #E6DECA): pill CTA boxes ("Offerings", "Email").
- **CC Link** (#5F574E): privacy/legal links in the footer.

### Named Rules
**The Two Accents Rule.** Berry rose and sage are the only saturated colors, and neither is ambient: berry appears on interactive controls, sage only marks the current page. Everywhere else the palette is blush, gray, and white so photography owns the chroma.

## Typography

**Display Font:** Baskerville MT Semi Bold Italic (`baskervillemtw01-smbdit`, serif fallback) — page titles and pill-button labels
**Body Font:** Spinnaker (`spinnaker, sans-serif`) — everything else: titles, subheads, body, nav, forms
**Script Accent:** Niconne (`niconne, fantasy`) — registered, not currently surfaced; do not introduce without the owner

**Character:** A quiet, evenly-set hospitality voice. Spinnaker's open humanist forms carry all reading text at small sizes with generous line-height (1.4–1.5em) and slight tracking on intros (0.06em); Baskerville italic is the single serif exclamation, reserved for the 50px page title and the 33px button label.

### Hierarchy
- **Display** (400, 50px, 1.9): page titles on blush title bands, centered, white
- **Title** (400, 39px, 1.2): offerings card titles — underlined, Peach Link on photo
- **Subhead** (400, 33px, 1.4): taglines ("Bring Something New to the Table!"), white, centered
- **Intro** (400, 18px, 1.5, +0.06em): homepage intro paragraph, centered
- **Body** (400, 13–14px, 1.4): paragraphs and menu lists; bold spans mark ingredients
- **Label** (400, 12px, 1.4): nav items (typed uppercase), dropdown items, footer links (13px underlined)
- **Form/Mono** (400, 13–14px, Courier New stack): inquiry-form field text and classic-button labels

### Named Rules
**The Quiet Page Rule.** One Baskerville display moment per page, at most. All other text is Spinnaker; scale shifts are size changes only, never new faces.

## Layout

A fixed **980px centered site column** inside full-width color bands. Header is 300px tall: framed logo plaque (227×226) flanked by thin rules, with a full-width 4-item nav bar (956×40) along its bottom edge above a 2px hairline. Footer is a 234px gray band with the B&W logo (80×80), two 39px social icons, and underlined legal links. Pages stack full-width sections: title band → content column → flourish ornament → footer. The offerings page is the signature composition: a full-page photo column (2:3, dark overlay rgba(0,0,0,.57)) with one giant white card (941px) floating over it, carrying a repeating two-column rhythm of text blocks and small right-rail photos. Contact/brunch pages set text over full-page 1:1 photo backgrounds. Owner-supplied pre-rendered bands lock to true aspect ratio in `site.css` (4096/768 hero, 4096/512 strip, 4096/6144 column) — `object-fit: cover` with nothing to crop; never reintroduce fixed pixel heights there.

## Elevation & Depth

Flat-first with hairline lifts. Depth comes from thin borders and photo overlay, not ambient shadow: cards and page frames carry `0 1px 4px rgba(0,0,0,.6)`; the dropdown `0 1px 4px rgba(0,0,0,.2)`; the footer logo `0 1px 3px rgba(0,0,0,.5)`. The offerings photo column dims behind white type instead of using scrims-as-gradients.

### Shadow Vocabulary
- **Card/page frame** (`0 1px 4px rgba(0,0,0,.6)`): white cards and page containers over photo.
- **Dropdown** (`0 1px 4px rgba(0,0,0,.2)`): hover/focus nav menus.
- **Footer logo** (`0 1px 3px rgba(0,0,0,.5)`): small framed logo tile.

## Shapes

A two-register form language. Soft register: 60px stylable pill buttons, 300px fully-rounded CTA pills, 5px cards/frames, 3px logo plaque. Square register: 0px classic form buttons and nav items, 1px black card borders, 4px pastel frames for feature panels. Borders are thin (1–4px) and flat; decorative rules (header hairline, logo flanks, footer flourish) do the ornament work.

## Components

### Navigation
- 4 stretched items, 40px tall, 12px Spinnaker #3E362E (typed uppercase); active = sage #5F7355 block, white text
- Dropdowns open on hover/focus-within: white panel, 0 1px 4px rgba(0,0,0,.2), items 9px/14px #2F2E2E, hover black underline

### Buttons
- **Pill (signature):** white bg, 60px radius, 33px Baskerville label #757575, letter-spacing 0.05em; hover flips bg #757575 / label white; disabled #E2E2E2/#8F8F8F
- **Pill CTA box:** taupe #605E5E, fully rounded, white underlined 30px link — used for "Offerings" and "Email"
- **Classic (forms):** 0px radius, 6–10px × 16px padding, berry #9F2747 bg, white Courier label; secondary outlined; hover rgba(159,39,71,.7)

### Cards / Containers
- 5px radius, white bg, 1px black or #C7C7C7 border, card shadow; internal padding 54–71px on the offerings mega-card

### Inputs / Fields
- Wix-style fields on inquiry pages; date fields get the invisible calendar overlay (site.css). Contact page itself is mailto-only — no form.

### Footer
- #E8E6E6 band, 234px; B&W logo tile, Instagram + Facebook icons (39px), underlined 13px legal links

### Signature
- **Framed logo plaque:** 2px black frame + 2px inner padding, 3px radius, flanked by thin horizontal rules, centered in the white 300px header
- **Double-line flourish:** 363×14 ornament pair above the footer on every page
- **Peach-on-photo type:** white/blush underlined titles over rgba(0,0,0,.57)-dimmed photography

## Do's and Don'ts

### Do:
- **Do** keep photography as the dominant surface on every page; text lives on bands, cards, or dimmed photo.
- **Do** fit containers to owner images with `aspect-ratio` (hero 4096/768, strip 4096/512, offerings 4096/6144); `object-fit: cover` then has nothing to crop.
- **Do** keep the two-accent discipline: berry for controls, sage for location, peach for links-on-photo.
- **Do** keep the header plaque, footer flourish, and 980px column as fixed furniture across all 21 pages.
- **Do** ship owner renders (`_assets/studio/`) byte-for-byte.

### Don't:
- **Don't** reorder, merge, or rename the hashed `css/b*.css` files; don't delete `site.css`'s gallery-visibility override.
- **Don't** crop, resize, or recompress owner-supplied images; don't put fixed pixel heights on aspect-locked slots.
- **Don't** introduce new saturated hues or new typefaces; new accents must route through a redesign conversation.
- **Don't** break relative-path depth (`../` in both `src` and `srcset`) on nested pages.
- **Don't** add a form backend or replace mailto contact links.
- **Don't** fabricate testimonials, press, or awards.
