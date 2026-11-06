"""Rebuild the site as a static, framework-free copy with pixel parity.

Approach: keep Wix's server-rendered presentation DOM (mesh layout markup,
inline component CSS) and drop every runtime artifact (JS bundles, JSON
configs, trackers, polyfills, preload links). Shared <style> blocks are
deduplicated into css/ files; assets are copied as a closure of what the
remaining DOM/CSS actually references.
"""
import glob, hashlib, html, json, os, re, shutil
from bs4 import BeautifulSoup, Comment

BASE = 'www.grazeandrose.com'
OUT = 'out'
if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

g = json.load(open('.build/graph.json'))
SLUGS = g['reachable']  # 21 nav-reachable pages

# ---------------------------------------------------------------- helpers
def page_depth(slug):
    """New depth of a page: repo-root index.html = 0."""
    return slug.count('/') + 1 if slug else 0

def prefix_for(slug):
    return '../' * page_depth(slug)

def target_slug(href, cur):
    """Resolve a mirror href (page-relative) to a slug in our page set."""
    if href.startswith(('http', 'mailto:', 'tel:', '#', 'data:')):
        return None
    href = href.split('#')[0].split('?')[0]
    if not href:
        return None
    pagedir = os.path.join(BASE, cur)
    full = os.path.normpath(os.path.join(pagedir, href)).replace(chr(92), '/')
    rel = os.path.relpath(full, BASE).replace(chr(92), '/')
    if rel.startswith('..'):
        return None
    parts = [x for x in rel.split('/') if x]
    if parts and parts[-1] == 'index.html':
        parts = parts[:-1]
    slug = '/'.join(parts)
    return slug if slug in SLUGS else None

def is_asset_href(href):
    return '_assets/' in href or '_files/' in href

def strip_one_up(href):
    """Asset URLs: pages moved one level up; drop one leading ../ ."""
    return re.sub(r'^(\.\./)+', lambda m: '../' * (len(m.group(0)) // 3 - 1), href)

# ---------------------------------------------------------------- css dedupe
CSS_DIR = os.path.join(OUT, 'css')
os.makedirs(CSS_DIR, exist_ok=True)
css_written = {}

def css_file_for(block_text):
    h = hashlib.md5(block_text.encode('utf-8')).hexdigest()[:12]
    name = 'b%s.css' % h
    path = os.path.join(CSS_DIR, name)
    if h not in css_written:
        # css lives at /css/*.css; url() refs resolve relative to /css/,
        # assets sit at /_assets & /_files (same depth as the page root)
        txt = block_text.replace('../../_assets/', '../_assets/')
        txt = txt.replace('../../_files/', '../_files/')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(txt)
        css_written[h] = name
    return css_written[h]

# ---------------------------------------------------------------- global site css
SITE_CSS = '''/* Graze & Rose - static-site additions (nav dropdown, forms, galleries) */
/* dropdown menu: open on hover / focus (Wix did this in JS) */
wix-dropdown-menu ul li { position: relative; }
wix-dropdown-menu ul li > ul {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 100%;
  background: rgb(255,255,255);
  box-shadow: 0 1px 4px rgba(0,0,0,.2);
  list-style: none;
  z-index: 100;
  padding: 0;
  margin: 0;
}
wix-dropdown-menu ul li:hover > ul,
wix-dropdown-menu ul li:focus-within > ul { display: block; }
wix-dropdown-menu ul li > ul li a {
  display: block;
  padding: 9px 14px;
  font-family: spinnaker, sans-serif;
  font-size: 12px;
  line-height: normal;
  color: #2f2e2e;
  text-decoration: none;
  white-space: nowrap;
}
wix-dropdown-menu ul li > ul li a:hover { color: #000; text-decoration: underline; }

/* date picker: native input, keep the Wix calendar button */
.wixui-date-picker__input::-webkit-calendar-picker-indicator { opacity: 0; position: absolute; inset: 0; width: 100%; height: 100%; cursor: pointer; }

/* keep pointer events on nav above page content */
wix-dropdown-menu { z-index: 1000; }

/* print: hide nav */
@media print { wix-dropdown-menu, #SITE_HEADER { display: none; } }

/* galleries: Wix hides the SSR slide stack (JS reveals it); show it statically */
.wixui-gallery .ERjQpM { visibility: visible; position: relative; width: 100%; aspect-ratio: 980 / 915; }
.wixui-gallery .ERjQpM .wixui-gallery__item { position: absolute; inset: 0; opacity: 0; transition: opacity .35s ease; pointer-events: none; }
.wixui-gallery .ERjQpM .wixui-gallery__item.on { opacity: 1; pointer-events: auto; }
.wixui-gallery .ERjQpM img { width: 100%; height: 100%; object-fit: cover; object-position: 50% 50%; }
'''
with open(os.path.join(OUT, 'site.css'), 'w', encoding='utf-8') as f:
    f.write(SITE_CSS)

SITE_JS = '''// Graze & Rose - static site behaviors (mailto forms, date pickers, galleries)
(function () {
  "use strict";

  // ---- inquiry forms: compose a mailto: with the field values
  document.querySelectorAll("form.wixui-form").forEach(function (form) {
    form.setAttribute("action", "mailto:grazecatercda@gmail.com");
    form.setAttribute("method", "post");
    form.setAttribute("enctype", "text/plain");
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var lines = [];
      form.querySelectorAll("input, select, textarea").forEach(function (inp) {
        if (!inp.name && !inp.id) return;
        var label = "";
        var lab = form.querySelector('label[for="' + inp.id + '"]');
        if (lab) label = lab.textContent.replace(/\\*|required/g, "").trim();
        var val = inp.value || "";
        if (inp.type === "checkbox") val = inp.checked ? "Yes" : "No";
        lines.push(label + ": " + val);
      });
      var subj = "Inquiry from grazeandrose.com";
      var page = document.title.replace(/\\s*\\|.*$/, "");
      subj = page ? page + " - inquiry" : subj;
      var body = lines.join("\\r\\n");
      location.href = "mailto:grazecatercda@gmail.com?subject=" +
        encodeURIComponent(subj) + "&body=" + encodeURIComponent(body);
    });
  });

  // ---- date pickers: native picker behind the Wix-styled button
  document.querySelectorAll(".wixui-date-picker").forEach(function (dp) {
    var input = dp.querySelector("input");
    var btn = dp.querySelector("button");
    if (!input) return;
    input.removeAttribute("readonly");
    input.setAttribute("type", "date");
    if (btn) {
      btn.addEventListener("click", function () {
        try { input.showPicker && input.showPicker(); } catch (e) { input.focus(); }
      });
    }
  });

  // ---- slide-show galleries: cycle the restored slides
  document.querySelectorAll('[data-testid="slide-show-gallery"]').forEach(function (gal) {
    var slides = Array.prototype.slice.call(gal.querySelectorAll('.wixui-gallery__item'));
    if (!slides.length) return;
    var current = 0;
    var counter = gal.querySelector('[data-testid="gallery-counter"]');
    function show(idx) {
      current = (idx + slides.length) % slides.length;
      slides.forEach(function (s, i) {
        s.classList.toggle('on', i === current);
        s.setAttribute('aria-hidden', i === current ? 'false' : 'true');
      });
      if (counter) counter.textContent = (current + 1) + '/' + slides.length;
    }
    // Wix's own nav buttons (prev/next inside the gallery)
    var navBtns = gal.querySelectorAll('[data-testid="gallery-navButtons"] button');
    if (navBtns.length >= 2) {
      navBtns[0].addEventListener('click', function () { show(current - 1); });
      navBtns[1].addEventListener('click', function () { show(current + 1); });
    }
    // auto-advance, pause on hover
    var timer = setInterval(function () { show(current + 1); }, 4500);
    gal.addEventListener('mouseenter', function () { clearInterval(timer); });
    show(0);
  });
})();
'''
with open(os.path.join(OUT, 'site.js'), 'w', encoding='utf-8') as f:
    f.write(SITE_JS)

# ---------------------------------------------------------------- asset closure
ASSET_FILES = set()   # paths under _assets/ or _files/ to copy
def mark_asset(relpath):
    """relpath like '_assets/static.wixstatic.com/media/x.png'."""
    relpath = relpath.replace(chr(92), '/')
    if relpath.startswith('_assets/') or relpath.startswith('_files/'):
        ASSET_FILES.add(relpath)

def collect_css_urls(css_text, base_dir):
    """Collect url() refs from a css file, resolved against its mirror dir."""
    for m in re.finditer(r'url\(\s*["\']?([^"\')]+?)["\']?\s*\)', css_text):
        r = m.group(1)
        if r.startswith('data:') or r.startswith('http'):
            continue
        full = os.path.normpath(os.path.join(base_dir, r)).replace(chr(92), '/')
        idx = full.find('_assets/')
        idx2 = full.find('_files/')
        if idx >= 0:
            mark_asset(full[idx:])
        elif idx2 >= 0:
            mark_asset(full[idx2:])

# ---------------------------------------------------------------- per page
HEAD_EXTRA_LINKS = []   # (rel, href) for deduped css; filled per page

def process_page(slug):
    src = BASE + ('/' + slug if slug else '') + '/index.html'
    raw = open(src, encoding='utf-8').read()
    soup = BeautifulSoup(raw, 'html.parser')
    cur = slug

    # ---- head: capture title/desc, then wipe and rebuild
    title = soup.title.get_text().strip() if soup.title else 'Graze and Rosé Catering'
    desc = ''
    md = soup.find('meta', attrs={'name': 'description'})
    if md:
        desc = md.get('content', '').strip()

    head = soup.head
    dedup_links = []          # css/ file names, in DOM order
    for style in head.find_all('style'):
        text = style.string or ''
        if not text.strip():
            continue
        collect_css_urls(text, os.path.dirname(src))
        dedup_links.append(css_file_for(text))

    # ---- body: prune
    body = soup.body
    for t in body.find_all(['script']):
        t.decompose()
    # body-level <link> tags are only Wix runtime preload hints (as=fetch etc.)
    for t in body.find_all('link'):
        t.decompose()
    for c in body.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()

    # drop hidden soap decoration images + their containers' emptiness (keep DOM, harmless)

    # ---- link rewriting
    for a in body.find_all('a', href=True):
        href = a['href']
        slug_t = target_slug(href, cur)
        if slug_t is not None:
            a['href'] = href  # page links: depth-shift is uniform, strings stay valid
        elif is_asset_href(href):
            a['href'] = strip_one_up(href)
            idx = a['href'].find('_assets/')
            idx2 = a['href'].find('_files/')
            if idx >= 0:
                mark_asset(a['href'][idx:])
            elif idx2 >= 0:
                mark_asset(a['href'][idx2:])
    for img in body.find_all('img', src=True):
        srcv = img['src']
        # Live-rendition upgrade: for every image with known container dims
        # (data-image-info), the live site serves a rendition at exactly those
        # dims from wixstatic. We fetched those deterministic URLs and use
        # them, giving the same pixels the live CDN serves.
        wow = img.find_parent('wow-image')
        if wow is not None:
            info = wow.get('data-image-info')
            if info:
                try:
                    dd = json.loads(html.unescape(info))
                    uri = (dd.get('imageData') or {}).get('uri')
                    tw, th = dd.get('targetWidth'), dd.get('targetHeight')
                    if uri and tw and th:
                        fname = f"{uri.split('~')[0]}__w{int(tw)}xh{int(th)}.jpg"
                        dpath = os.path.join('downloads', fname)
                        if os.path.exists(dpath) and os.path.getsize(dpath) > 1000:
                            rel = '_assets/static.wixstatic.com/media/' + fname
                            img['src'] = prefix_for(slug) + rel
                            if img.get('srcset'):
                                del img['srcset']
                            continue
                except Exception:
                    pass
        if is_asset_href(srcv):
            img['src'] = strip_one_up(srcv)
            idx = img['src'].find('_assets/')
            if idx >= 0:
                mark_asset(img['src'][idx:])
    # inline style url() refs (rare)
    for el in body.find_all(style=True):
        st = el['style']
        if '_assets/' in st:
            el['style'] = strip_one_up(st)

    # ---- nav dropdown: remove inline display:none (site.css controls it)
    for ul in body.find_all('ul'):
        if ul.get('aria-hidden') == 'true' and ul.get('style'):
            ul['style'] = re.sub(r'display\s*:\s*none\s*;?', '', ul['style']).strip() or None

    # ---- forms: mark for mailto (site.js wires the rest)
    for form in body.find_all('form'):
        form['data-static-mailto'] = '1'

    # ---- rebuild head (preserve cascade order: css links and deduped style
    #      blocks are emitted in their original document order)
    new_head = soup.new_tag('head')
    def append(tag):
        new_head.append(tag)
    mt = soup.new_tag('meta'); mt.attrs['charset'] = 'utf-8'; append(mt)
    mv = soup.new_tag('meta'); mv.attrs['name'] = 'viewport'
    mv.attrs['content'] = 'width=device-width, initial-scale=1'; append(mv)
    if desc:
        md2 = soup.new_tag('meta'); md2.attrs['name'] = 'description'
        md2.attrs['content'] = desc; append(md2)
    ti = soup.new_tag('title'); ti.string = title; append(ti)
    pre = prefix_for(slug)
    fav = soup.new_tag('link'); fav.attrs.update({'rel': 'icon', 'href': pre + 'favicon.png', 'type': 'image/png'})
    append(fav)

    # pass 1: collect css url() refs from external files + register assets
    seen_css = set()
    for tag in head.find_all(['link', 'style']):
        if tag.name == 'link':
            href = tag.get('href', '')
            if href and '.css' in href and is_asset_href(href):
                pagedir = os.path.dirname(src)
                full = os.path.normpath(os.path.join(pagedir, href)).replace(chr(92), '/')
                if os.path.exists(full):
                    idx = full.find('_assets/')
                    if idx >= 0:
                        mark_asset(full[idx:])
                        collect_css_urls(open(full, encoding='utf-8', errors='ignore').read(),
                                         os.path.dirname(full))
    # pass 2: emit in order
    for tag in head.find_all(['link', 'style']):
        if tag.name == 'style':
            text = tag.string or ''
            if text.strip():
                l2 = soup.new_tag('link'); l2.attrs['rel'] = 'stylesheet'
                l2.attrs['href'] = pre + 'css/' + css_file_for(text)
                append(l2)
        else:
            href = tag.get('href', '')
            rel = tag.get('rel', [''])[0] if tag.get('rel') else ''
            if href and '.css' in href and is_asset_href(href):
                nh = strip_one_up(href)
                if nh not in seen_css:
                    seen_css.add(nh)
                    l2 = soup.new_tag('link'); l2.attrs['rel'] = 'stylesheet'; l2.attrs['href'] = nh
                    append(l2)
    l2 = soup.new_tag('link'); l2.attrs['rel'] = 'stylesheet'; l2.attrs['href'] = pre + 'site.css'
    append(l2)

    head.replace_with(new_head)

    # script at end of body
    sc = soup.new_tag('script'); sc.attrs['src'] = pre + 'site.js'; sc.attrs['defer'] = True
    body.append(sc)

    # ---- write page
    dst = os.path.join(OUT, slug.replace('/', os.sep), 'index.html') if slug else os.path.join(OUT, 'index.html')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(str(soup))

for slug in SLUGS:
    process_page(slug)
    print('.', end='', flush=True)
print()

# ---------------------------------------------------------------- live renditions
rend_copied = 0
for f in glob.glob('downloads/*.jpg'):
    if os.path.getsize(f) < 1000:
        continue
    dst = os.path.join(OUT, '_assets', 'static.wixstatic.com', 'media', os.path.basename(f))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(f, dst)
    rend_copied += 1

# ---------------------------------------------------------------- gallery restore
# Wix SSR emits only the first gallery slide (+ ghost skeletons); the full
# ordered slide list lives in the page's siteassets JSON config. Restore the
# missing slides as real <img> elements and copy their renditions.
def restore_galleries():
    total_added = 0
    for slug in SLUGS:
        srcp = BASE + ('/' + slug if slug else '') + '/index.html'
        raw = open(srcp, encoding='utf-8').read()
        galleries = set(re.findall(r'id="(comp-[a-z0-9]+)"[^>]*data-testid="slide-show-gallery"', raw))
        if not galleries:
            continue
        # find the page's siteassets config (referenced by its preloads)
        configs = []
        for cid in re.findall(r'"artifactId"...', raw):
            pass
        for m in re.finditer(r'href="[^"]*_assets/siteassets\.parastorage\.com/pages/pages/([^"]+)"', raw):
            configs.append(m.group(1))
        cfgs = []
        for name in configs:
            p = '_assets/siteassets.parastorage.com/pages/pages/' + name
            if os.path.exists(p):
                cfgs.append(open(p, encoding='utf-8', errors='ignore').read())
        if not cfgs:
            continue
        outp = os.path.join(OUT, slug.replace('/', os.sep), 'index.html') if slug else os.path.join(OUT, 'index.html')
        soup = BeautifulSoup(open(outp, encoding='utf-8').read(), 'html.parser')
        for gid in galleries:
            slide_uris = None
            for cfg in cfgs:
                i0 = cfg.find('"' + gid + '":{"skin"')
                if i0 < 0:
                    continue
                seg = cfg[i0:i0 + 20000]
                j0 = seg.find('"items":[')
                if j0 < 0:
                    continue
                start = j0 + len('"items":[')
                depth = 0
                end = -1
                for k in range(start, len(seg)):
                    ch = seg[k]
                    if ch == '[':
                        depth += 1
                    elif ch == ']':
                        if depth == 0:
                            end = k
                            break
                        depth -= 1
                if end < 0:
                    continue
                slide_uris = re.findall(
                    r'"uri":"(d69fc6_[a-f0-9]{32}~mv2\.(?:jpg|jpeg|png))"',
                    seg[start:end])
                if slide_uris:
                    break
            if not slide_uris:
                continue
            gal = soup.find(id=gid)
            if gal is None:
                continue
            holder = gal.find(class_='ERjQpM') or gal
            existing = gal.find_all(class_='wixui-gallery__item')
            have = set()
            for e in existing:
                im = e.find('img')
                if im and im.get('src'):
                    have.add(os.path.splitext(os.path.basename(im['src']))[0].split('__')[0])
            # full rebuild: one clean slide per configured image, in order
            for e in existing:
                e.decompose()
            for uri in slide_uris:
                stem = uri.split('~')[0]
                fname = stem + '__w980xh915.jpg'
                if not os.path.exists(os.path.join('downloads', fname)):
                    # rendition not available: keep the gallery at what SSR gave us
                    continue
                slide = soup.new_tag('div')
                slide.attrs = {'class': 'ub9SrO aKIkDa wixui-gallery__item',
                               'data-testid': 'gallery-item-item',
                               'data-image-mode': 'clipImage'}
                img = soup.new_tag('img')
                img.attrs = {'src': prefix_for(slug) + '_assets/static.wixstatic.com/media/' + fname,
                             'alt': '', 'loading': 'lazy',
                             'style': 'width:100%;height:100%;object-fit:cover;object-position:50% 50%'}
                slide.append(img)
                holder.append(slide)
                total_added += 1
                dst = os.path.join(OUT, '_assets', 'static.wixstatic.com', 'media', fname)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(os.path.join('downloads', fname), dst)
        with open(outp, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    return total_added

g_added = restore_galleries()

# ---------------------------------------------------------------- favicon
fav_src = '_assets/static.wixstatic.com/media/d69fc6_a3f7111fb96c4512a137accc098d0bc7~mv2__0f2d0e1640.png'
shutil.copyfile(fav_src, os.path.join(OUT, 'favicon.png'))
mark_asset(fav_src)

# ---------------------------------------------------------------- copy assets
copied = 0
for rel in sorted(ASSET_FILES):
    src = rel  # path relative to repo root
    if not os.path.exists(src):
        print("MISSING:", rel)
        continue
    dst = os.path.join(OUT, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    copied += 1
print("pages:", len(SLUGS), "| css blocks:", len(css_written), "| assets copied:", copied, "| live renditions:", rend_copied, "| gallery slides restored:", g_added)

# ---------------------------------------------------------------- size
tot = sum(os.path.getsize(os.path.join(dp, fn)) for dp, dn, fnl in os.walk(OUT) for fn in fnl)
print("site size: %.2f MB" % (tot / 1048576))
