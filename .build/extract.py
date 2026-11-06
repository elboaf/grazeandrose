"""Extract structured content from the Wix mirror into content.json."""
import json, os, re, html
from bs4 import BeautifulSoup
from urllib.parse import urlparse

BASE = 'www.grazeandrose.com'
g = json.load(open('.build/graph.json'))
PAGES = g['reachable']          # 21 nav-reachable slugs
ASSETS = {}                     # rel-path in new site -> source path in mirror

# ---------- theme ----------
def get_theme(soup, raw):
    m = re.search(r'--font_0:(.*?);--font_1:(.*?);--font_2:(.*?);--font_3:(.*?);'
                  r'--font_4:(.*?);--font_5:(.*?);--font_6:(.*?);--font_7:(.*?)00;', raw)
    fonts = {}
    if m:
        vals = [m.group(i) for i in range(1, 9)]
        for i, v in enumerate(vals):
            fonts[f'font_{i}'] = v.rstrip('0123456789').rstrip('-').rstrip()
            fonts[f'font_{i}'] = v
    colors = {}
    m = re.search(r'--color_0:(.*?);--color_1:(.*?)--color_9', raw, re.S)
    seg = m.group(0) if m else ''
    for i in range(0, 60):
        mm = re.search(r'--color_%d:([0-9, ]+);' % i, raw)
        if mm:
            colors[f'color_{i}'] = mm.group(1).strip()
    return {'fonts': fonts, 'colors': colors}

# ---------- helpers ----------
def comp_css(raw):
    """Map comp id -> its geometry/custom-prop rules from the inline CSS blocks."""
    out = {}
    for m in re.finditer(r'#(comp-[a-z0-9_]+|[A-Za-z]\w*)\{([^}]*)\}', raw):
        out.setdefault(m.group(1), '')
        out[m.group(1)] += m.group(2)
    return out

def css_num(rules, prop):
    m = re.search(prop + r':\s*(-?[\d.]+)px', rules)
    return float(m.group(1)) if m else None

def asset_ref(rel_path, src):
    """Register a mirror file for copying; return the new-site path."""
    if rel_path not in ASSETS:
        ASSETS[rel_path] = src
    return rel_path

def wix_img(src, page_dir, soup_node=None):
    """Convert a mirror img src to a new asset path."""
    if not src:
        return None, None
    s = src.replace('../', '')
    if not s.startswith('_assets'):
        s = '_assets/' + s.lstrip('/')
    full = os.path.normpath(s).replace('\\', '/')
    if not os.path.exists(full):
        return None, None
    m = re.search(r'/media/([^/]+?)(?:__[a-f0-9]+)?\.(png|jpe?g|gif|webp|avif)$', full, re.I)
    if not m:
        return None, None
    stem = m.group(1)
    ext = m.group(2).lower().replace('jpeg', 'jpg')
    newrel = 'img/' + stem + '.' + ext
    asset_ref(newrel, full)
    return newrel, full

def clean_inline(tag):
    """Rebuild an inline styled span tree as minimal HTML."""
    parts = []
    for child in tag.children:
        if isinstance(child, str):
            parts.append(html.escape(child.replace('\u200b', '')))
        elif child.name in ('span', 'a', 'b', 'strong', 'i', 'em', 'u', 's', 'br'):
            if child.name == 'br':
                parts.append('<br>')
                continue
            attrs = []
            style = child.get('style', '')
            if child.name == 'a':
                href = child.get('href', '')
                # normalize relative hrefs later at render time; keep as-is
                attrs.append('href="%s"' % html.escape(href, quote=True))
            cls = ' '.join(child.get('class', []))
            if 'font_' in cls:
                f = [c for c in child.get('class', []) if c.startswith('font_')]
                if f:
                    attrs.append('class="%s"' % f[0])
            if style:
                # keep only visual props
                keep = []
                for decl in style.split(';'):
                    d = decl.strip()
                    if d.split(':')[0].strip() in (
                        'font-size', 'font-weight', 'font-family', 'color',
                        'text-decoration', 'letter-spacing', 'font-style',
                        'background-color', 'text-transform', 'line-height'):
                        if d:
                            keep.append(d)
                if keep:
                    attrs.append('style="%s"' % html.escape(';'.join(keep) + ';', quote=True))
            inner = clean_inline(child)
            parts.append('<%s %s>%s</%s>' % (child.name, ' '.join(attrs), inner, child.name))
        else:
            parts.append(clean_inline(child))
    return ''.join(parts)

def rich_text(el):
    """Extract a rich-text element's blocks: list of {tag, html}."""
    blocks = []
    for top in el.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol'],
                           recursive=False):
        tag = top.name
        txt = top.get_text().replace('\u200b', '').strip()
        if not txt and tag != 'p':
            continue
        inner = clean_inline(top)
        cls = ' '.join(c for c in top.get('class', []) if c.startswith('font_'))
        style = top.get('style', '')
        blocks.append({'tag': tag, 'html': inner, 'class': cls, 'style': style,
                       'text': txt})
    return blocks

def img_of(el, page_dir):
    img = el.find('img')
    if not img:
        return None
    src = img.get('src', '')
    rel, full = wix_img(src, page_dir)
    if not rel:
        return None
    alt = img.get('alt', '')
    if alt.endswith('.png') or alt.endswith('.jpg') or alt.endswith('.jpeg'):
        alt = ''
    w = img.get('width') or None
    hgt = img.get('height') or None
    # data-image-info carries container dims for bg/fill images
    info = el.get('data-image-info')
    tw = th = None
    if info:
        try:
            d = json.loads(html.unescape(info))
            tw, th = d.get('targetWidth'), d.get('targetHeight')
        except Exception:
            pass
    return {'src': rel, 'alt': alt, 'w': int(float(w)) if w else tw,
            'h': int(float(hgt)) if hgt else th}

def bg_image_of(el):
    """wixui-image used as a column background (wow-image/bgImage)."""
    img = el.find('img')
    if not img:
        return None
    return img_of(el, None)

def form_fields(form_el):
    """Pull ordered fields from a wixui-form."""
    fields = []
    seen = set()
    for inp in form_el.find_all(['input', 'select', 'textarea']):
        iid = inp.get('id', '')
        if iid in seen or not iid:
            continue
        seen.add(iid)
        ftype = inp.get('type', 'text')
        label = ''
        lab = form_el.find('label', attrs={'for': iid})
        if lab:
            label = lab.get_text().replace('required', '').replace('*', '').strip()
        name = inp.get('name') or (iid.replace('input_', '') if iid else '')
        f = {'kind': inp.name, 'type': ftype if inp.name != 'textarea' else 'textarea',
             'label': label, 'name': name, 'required': inp.has_attr('required'),
             'placeholder': inp.get('placeholder', '')}
        if inp.name == 'select':
            f['options'] = [o.get_text().strip() for o in inp.find_all('option')
                            if o.get_text().strip()]
        fields.append(f)
    # checkboxes grouped (consent)
    checks = []
    for cb in form_el.find_all('input', type='checkbox'):
        iid = cb.get('id', '')
        lab = form_el.find('label', attrs={'for': iid})
        txt = ''
        if lab:
            holder = lab.find_parent(class_=re.compile('wixui-checkbox'))
            txt = holder.get_text().strip() if holder else lab.get_text().strip()
        checks.append({'label': txt})
    return fields, checks

def button_of(el):
    """StylableButton / wixui-button -> {label, href, colors}."""
    a = el.find('a')
    href = a.get('href', '') if a else ''
    label_el = el.find('span', attrs={'data-testid': 'labelElement'})
    if not label_el:
        label_el = el.find(class_='wixui-button__label') or el
    label = label_el.get_text().replace('\u200b', '').strip()
    style = el.get('style', '') or ''
    colors = {}
    m = re.search(r'--corvid-background-color:([^;]+)', style)
    if m:
        colors['bg'] = m.group(1).strip()
    m = re.search(r'--corvid-color:([^;]+)', style)
    if m:
        colors['fg'] = m.group(1).strip()
    m = re.search(r'--corvid-border-color:([^;]+)', style)
    if m:
        colors['border'] = m.group(1).strip()
    return {'label': label, 'href': href, 'colors': colors}

def line_of(el):
    style = el.get('style', '')
    colors = {}
    m = re.search(r'background-color:([^;]+)', style)
    if m:
        colors['bg'] = m.group(1).strip()
    w = css_num(el.get('style', '') + ' ', 'width') or None
    return {'colors': colors, 'w': w}

def bgcolor_of(comp_id, cssmap):
    rules = cssmap.get(comp_id, '')
    m = re.search(r'--bg-overlay-color:([^;}]+)', rules)
    if m:
        v = m.group(1).strip()
        if v.startswith('rgb(var'):
            return None  # theme var; resolve later if needed
        return v
    return None

def col_width(comp_id, cssmap):
    rules = cssmap.get(comp_id, '')
    return css_num(rules, 'width')

def pad_of(comp_id, cssmap):
    rules = cssmap.get(comp_id, '')
    m = re.search(r'padding:\s*([^;]+)', rules)
    return m.group(1).strip() if m else None

# ---------- page walker ----------
LEAF_PREFIX = ('WPht', 'FvGr', 'DrpDwn', 'SiteB')

def is_comp(el):
    cid = el.get('id', '')
    return cid.startswith('comp-') or any(cid.startswith(p) for p in LEAF_PREFIX)

CSSMAP = {}

def walk(el, out, page_dir, strip=None, colidx=None):
    """Generic DOM-order walker. strip/colidx route output into a column."""
    cls = el.get('class', [])
    ident = ' '.join(cls)
    cid = el.get('id', '')

    def sink(blocklist):
        if strip is not None and colidx is not None:
            strip['columns'][colidx]['blocks'].extend(blocklist)
        else:
            out.extend(blocklist)

    # nested section: capture and recurse inside it
    if 'wixui-section' in ident:
        sec = {'type': 'section', 'bgcolor': bgcolor_of(cid, CSSMAP),
               'minh': None, 'blocks': []}
        m = re.search(r'min-height:(\d+)px', CSSMAP.get(cid, ''))
        if m:
            sec['minh'] = int(m.group(1))
        if strip is not None and colidx is not None:
            strip['columns'][colidx]['blocks'].append(sec)
        else:
            out.append(sec)
        for sub in el.find_all(True, recursive=False):
            walk(sub, sec['blocks'], page_dir)
        return

    # column strip: capture columns, recurse into each column's content
    if 'wixui-column-strip' in ident:
        colholder = None
        for sub in el.find_all(True, recursive=False):
            if sub.get('data-testid') == 'columns':
                colholder = sub
        cols = []
        if colholder is not None:
            cols = [c for c in colholder.find_all(True, recursive=False)
                    if 'wixui-column-strip__column' in ' '.join(c.get('class', []))]
        strip2 = {'type': 'strip', 'bgcolor': bgcolor_of(cid, CSSMAP), 'columns': []}
        for col in cols:
            colid = col.get('id', '')
            c = {'w': col_width(colid, CSSMAP), 'bgcolor': bgcolor_of(colid, CSSMAP),
                 'bgimg': None, 'blocks': []}
            wow = col.find('wow-image')
            if wow is not None and col.find(class_='wixui-rich-text') is None:
                img = img_of(wow, page_dir)
                if img:
                    c['bgimg'] = img
            strip2['columns'].append(c)
        sink([strip2])
        for i, col in enumerate(cols):
            for sub in col.find_all(True, recursive=False):
                walk(sub, out, page_dir, strip=strip2, colidx=i)
        return

    # leaf comps
    if is_comp(el):
        blocks = []
        walk_comp(el, CSSMAP, blocks, page_dir)
        sink(blocks)
        return

    # anything else (mesh wrappers, bg layers): recurse
    for sub in el.find_all(True, recursive=False):
        walk(sub, out, page_dir, strip=strip, colidx=colidx)

def walk_comp(el, cssmap, out, page_dir):
    cls = ' '.join(el.get('class', []))
    cid = el.get('id', '')
    if 'wixui-rich-text' in cls:
        blocks = rich_text(el)
        if blocks:
            out.append({'type': 'text', 'id': cid, 'blocks': blocks,
                        'w': col_width(cid, cssmap)})
    elif 'wixui-image' in cls or el.name == 'wow-image':
        img = img_of(el, page_dir)
        if img:
            out.append({'type': 'image', 'id': cid, **img, 'w': col_width(cid, cssmap)})
    elif 'wixui-gallery' in cls:
        items = []
        for gi in el.find_all(class_='wixui-gallery__item'):
            img = gi.find('img')
            if img:
                info = gi.get('data-image-info') or el.get('data-image-info')
                it = img_of(gi, page_dir)
                if it:
                    try:
                        d = json.loads(html.unescape(info))
                        it['w'] = d.get('targetWidth') or it['w']
                        it['h'] = d.get('targetHeight') or it['h']
                    except Exception:
                        pass
                    items.append(it)
        if items:
            out.append({'type': 'gallery', 'id': cid, 'items': items})
    elif 'StylableButton' in cls or 'wixui-button' in cls:
        b = button_of(el)
        if b['label'] or b['href']:
            out.append({'type': 'button', 'id': cid, **b})
    elif 'wixui-horizontal-line' in cls:
        out.append({'type': 'line', 'id': cid, **line_of(el)})
    elif 'wixui-form' in cls:
        fields, checks = form_fields(el)
        # form may contain rich text intro + button
        blocks = []
        for rt in el.find_all(class_='wixui-rich-text'):
            blocks.extend(rich_text(rt))
        btn = None
        sb = el.find(class_=re.compile('StylableButton'))
        if sb:
            btn = button_of(sb)
        out.append({'type': 'form', 'id': cid, 'fields': fields,
                    'checks': checks, 'blocks': blocks, 'button': btn})
    elif 'wixui-text-input' in cls or 'wixui-text-box' in cls or 'wixui-dropdown' in cls or 'wixui-date-picker' in cls:
        # bare field outside a form
        inp = el.find(['input', 'select', 'textarea'])
        if inp is not None:
            iid = inp.get('id', '')
            lab = el.find('label', attrs={'for': iid})
            f = {'kind': inp.name, 'type': inp.get('type', 'text'),
                 'label': lab.get_text().replace('required', '').replace('*', '').strip() if lab else '',
                 'name': inp.get('name') or iid.replace('input_', ''),
                 'required': inp.has_attr('required'),
                 'placeholder': inp.get('placeholder', '')}
            if inp.name == 'select':
                f['options'] = [o.get_text().strip() for o in inp.find_all('option')
                                if o.get_text().strip()]
            out.append({'type': 'field', 'id': cid, 'field': f})
    elif 'wixui-checkbox' in cls:
        txt = el.get_text().strip()
        out.append({'type': 'field', 'id': cid,
                    'field': {'kind': 'checkbox', 'type': 'checkbox', 'label': txt,
                              'name': 'consent', 'required': False, 'placeholder': ''}})
    elif 'wixui-column-strip' in cls:
        pass  # handled by walker
    else:
        # container without known class: recurse
        if el.find(True):
            for sub in el.find_all(True, recursive=False):
                walk_comp(sub, cssmap, out, page_dir)

def extract_page(slug):
    path = BASE + ('/' + slug if slug else '') + '/index.html'
    raw = open(path, encoding='utf-8').read()
    soup = BeautifulSoup(raw, 'html.parser')
    global CSSMAP
    CSSMAP = comp_css(raw)
    cssmap = CSSMAP
    page_dir = os.path.dirname(path)

    title = soup.title.get_text().strip() if soup.title else ''
    desc = ''
    md = soup.find('meta', attrs={'name': 'description'})
    if md:
        desc = md.get('content', '')

    out = []
    main = soup.find(id='PAGES_CONTAINER')
    if main:
        for el in main.find_all(True, recursive=False):
            walk(el, out, page_dir)
    # hero: first image block
    return {'slug': slug, 'title': title, 'desc': desc, 'sections': out}

# ---------- nav + footer ----------
def chrome():
    path = BASE + '/index.html'
    raw = open(path, encoding='utf-8').read()
    soup = BeautifulSoup(raw, 'html.parser')
    nav = []
    menu = soup.find('wix-dropdown-menu')
    if menu:
        for li in menu.find_all('li', class_='wixui-dropdown-menu__item'):
            a = li.find('a')
            sub = []
            for sa in li.find_all('li'):
                s = sa.find('a')
                if s:
                    sub.append({'label': s.get_text().strip(), 'href': s.get('href', '')})
            nav.append({'label': a.get_text().strip(), 'href': a.get('href', ''),
                        'sub': sub})
    foot = []
    ftr = soup.find(id='SITE_FOOTER')
    if ftr:
        for rt in ftr.find_all(class_='wixui-rich-text'):
            foot.extend(rich_text(rt))
        for sb in ftr.find_all(class_=re.compile('StylableButton')):
            foot.append({'type': 'button', **button_of(sb)})
        for iw in ftr.find_all(class_='wixui-image'):
            img = img_of(iw, None)
            if img:
                foot.append({'type': 'image', **img})
        for ln in ftr.find_all(class_='wixui-horizontal-line'):
            foot.append({'type': 'line', **line_of(ln)})
    hdr_imgs = []
    hdr = soup.find(id='SITE_HEADER')
    if hdr:
        for iw in hdr.find_all(class_='wixui-image'):
            img = img_of(iw, None)
            if img:
                hdr_imgs.append(img)
    theme = get_theme(soup, raw)
    return {'nav': nav, 'footer': foot, 'header_images': hdr_imgs, 'theme': theme}

data = {'theme_pages': {}, 'pages': [], 'chrome': chrome(), 'assets': {}}
for slug in PAGES:
    pg = extract_page(slug)
    data['pages'].append(pg)

data['assets'] = ASSETS
json.dump(data, open('.build/content.json', 'w', encoding='utf-8'), indent=1)
print("pages:", len(data['pages']))
print("assets:", len(ASSETS))
for slug in PAGES:
    pg = [p for p in data['pages'] if p['slug'] == slug][0]
    nsec = len(pg['sections'])
    nblocks = sum(len(s['blocks']) for s in pg['sections'])
    print(f"  {slug or '(home)':55} sections={nsec} blocks={nblocks}")
