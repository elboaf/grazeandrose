"""Render clean static pages from content.json + Wix's own mesh geometry CSS."""
import json, os, re, shutil, html
from PIL import Image

BASE = 'www.grazeandrose.com'
OUT = 'site'
d = json.load(open('.build/content.json', encoding='utf-8'))
PAGES = d['pages']
CHROME = d['chrome']
ASSETS = d['assets']   # newrel -> mirror source path

# ---------------------------------------------------------------- slug maps
def page_href(slug, cur=''):
    """Relative href from page `cur` to page `slug`."""
    if slug == cur:
        return 'index.html'
    parts = slug.split('/') if slug else []
    curparts = cur.split('/') if cur else []
    while curparts and parts and parts[0] == curparts[0]:
        parts.pop(0); curparts.pop(0)
    up = ['..'] * len(curparts)
    return '/'.join(up + parts + ['index.html']) if parts else 'index.html'

def fix_href(href, cur):
    """Convert a mirror-relative href (from page cur's dir) to the new site."""
    if href.startswith(('http', 'mailto:', 'tel:', '#')):
        return href
    href = href.split('#')[0]
    pagedir = os.path.join(BASE, cur)
    full = os.path.normpath(os.path.join(pagedir, href)).replace(chr(92), '/')
    rel = os.path.relpath(full, BASE).replace(chr(92), '/')
    if rel.startswith('..'):
        return href  # asset or external, keep
    parts = [x for x in rel.split('/') if x]
    if parts and parts[-1] == 'index.html':
        parts = parts[:-1]
        slug = '/'.join(parts)
        return page_href(slug, cur)
    return href  # an actual file (pdf)

# ---------------------------------------------------------------- asset prep
os.makedirs(OUT + '/img', exist_ok=True)
os.makedirs(OUT + '/fonts', exist_ok=True)
os.makedirs(OUT + '/files', exist_ok=True)

# ------- fonts: subset of woff2 files the theme uses
FONT_MAP = {
    'fonts/spinnaker.woff2': '_assets/static.parastorage.com/tag-bundler/api/v1/fonts-cache/googlefont/woff2/s/spinnaker/v19/w8gYH2oyX-I0_rvR6HmX23YKiumCBw.woff2',
    'fonts/spinnaker-ext.woff2': '_assets/static.parastorage.com/tag-bundler/api/v1/fonts-cache/googlefont/woff2/s/spinnaker/v19/w8gYH2oyX-I0_rvR6HmX1XYKiumCB-Eo.woff2',
    'fonts/niconne.woff2': '_assets/static.parastorage.com/tag-bundler/api/v1/fonts-cache/googlefont/woff2/s/niconne/v15/w8gaH2QvRug1_rTfnQyn2XwNqOs.woff2',
    'fonts/niconne-ext.woff2': '_assets/static.parastorage.com/tag-bundler/api/v1/fonts-cache/googlefont/woff2/s/niconne/v15/w8gaH2QvRug1_rTfnQKn2XwNqOuyBg.woff2',
    'fonts/museo-700.woff2': '_assets/static.parastorage.com/fonts/v2/e7793d7d-669f-464d-9e4d-f2b5c71cd178/v1/museo-w01-700.woff2',
    'fonts/museo-700-ext.woff2': '_assets/static.parastorage.com/fonts/v2/e7793d7d-669f-464d-9e4d-f2b5c71cd178/v1/museo-w05-700.woff2',
}
for dst, src in FONT_MAP.items():
    if os.path.exists(src):
        shutil.copyfile(src, OUT + '/' + dst)
    else:
        print("MISSING FONT:", src)

# ------- images: copy + downscale oversized
img_stats = []
for newrel, src in ASSETS.items():
    dst = OUT + '/' + newrel
    if not os.path.exists(src):
        print("MISSING IMG:", src)
        continue
    try:
        im = Image.open(src)
        w, h = im.size
        changed = False
        # cap render size at 2x the largest display size we saw
        if w > 2400 or h > 2400:
            scale = 2400 / max(w, h)
            im = im.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
            changed = True
        ext = os.path.splitext(dst)[1].lower()
        if ext in ('.jpg', '.jpeg'):
            im.convert('RGB').save(dst, 'JPEG', quality=85, optimize=True)
        elif ext == '.png':
            im.save(dst, 'PNG', optimize=True)
        else:
            shutil.copyfile(src, dst)
        img_stats.append((newrel, w, h, im.size[0], im.size[1]))
    except Exception as e:
        shutil.copyfile(src, dst)

# ------- PDF
pdfsrc = '_files/ugd/d69fc6_d3058a5d3c2747f4aa0172ce74bfa1f7.pdf'
shutil.copyfile(pdfsrc, OUT + '/files/catering-service-terms.pdf')

# ---------------------------------------------------------------- shared css
CSS = '''/* Graze & Rose — rebuilt static site. Theme values from the original Wix site. */
@font-face{font-family:'spinnaker';font-style:normal;font-weight:400;src:url(fonts/spinnaker.woff2) format('woff2');unicode-range:U+0000-00FF,U+2013,U+2014,U+2018,U+2019,U+201C,U+2019,U+2013,U+2014,U+2026;font-display:swap}
@font-face{font-family:'spinnaker';font-style:normal;font-weight:400;src:url(fonts/spinnaker-ext.woff2) format('woff2');unicode-range:U+0100-024F,U+1E00-1EFF;font-display:swap}
@font-face{font-family:'niconne';font-style:normal;font-weight:400;src:url(fonts/niconne.woff2) format('woff2');unicode-range:U+0000-00FF;font-display:swap}
@font-face{font-family:'niconne';font-style:normal;font-weight:400;src:url(fonts/niconne-ext.woff2) format('woff2');unicode-range:U+0100-024F;font-display:swap}
@font-face{font-family:'museo-w01-700';font-style:normal;font-weight:400;src:url(fonts/museo-700.woff2) format('woff2');unicode-range:U+0000-00FF;font-display:swap}
@font-face{font-family:'museo-w01-700';font-style:normal;font-weight:400;src:url(fonts/museo-700-ext.woff2) format('woff2');unicode-range:U+0100-024F;font-display:swap}

:root{
  --color_11:255,255,255;--color_12:232,230,230;--color_13:199,199,199;
  --color_14:117,117,117;--color_15:0,0,0;--color_16:223,167,182;--color_17:191,119,138;
  --color_18:159,39,71;--color_19:106,26,47;--color_20:53,13,24;--color_21:255,240,235;
  --color_22:255,224,212;--color_23:248,209,194;--color_24:149,125,116;--color_25:107,90,84;
  --color_26:227,224,192;--color_27:198,195,152;--color_28:170,165,91;--color_29:113,110,61;
  --color_30:57,55,30;--color_31:188,200,217;--color_32:143,157,179;--color_33:85,107,141;
  --color_34:57,71,94;--color_35:28,36,47;--color_41:159,39,71;--color_45:0,0,0;
  --color_46:117,117,117;--color_50:255,255,255;
  --font_0:normal normal bold 25px/1.4em verdana,geneva,sans-serif;
  --font_2:normal normal normal 24px/1.4em spinnaker,sans-serif;
  --font_3:normal normal normal 60px/1.4em spinnaker,sans-serif;
  --font_4:normal normal normal 25px/1.4em niconne,fantasy;
  --font_5:normal normal normal 20px/1.4em spinnaker,sans-serif;
  --font_6:normal normal normal 21px/1.4em spinnaker,sans-serif;
  --font_7:normal normal normal 18px/1.4em spinnaker,sans-serif;
  --font_8:normal normal normal 13px/1.4em 'courier new',monospace;
  --font_9:normal normal normal 11px/1.4em 'palatino linotype',serif;
}
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{font-family:spinnaker,sans-serif;background:rgb(var(--color_12));color:rgb(var(--color_46))}
img{border:0;max-width:100%}
a{color:inherit}
#site{min-height:100vh;display:flex;flex-direction:column}
#page{flex:1;width:100%}

/* ---- header ---- */
#SITE_HEADER{position:relative;background:rgb(var(--color_11));overflow:visible}
#SITE_HEADER .mesh{position:relative;width:100%;min-height:300px}
.hdr-logo{position:relative;margin:87px 0px 39px;left:-135px;transform:translateX(calc((100vw - 980px)*.5 + 490px));width:227px}
.hdr-logo img{width:227px;height:222px;object-fit:cover;display:block}
.hdr-line1,.hdr-line2{position:absolute;border-top:1px solid rgb(0,0,0);width:980px;left:50%;transform:translateX(-50%)}
.hdr-line1{top:130px}
.hdr-line2{top:238px}
#site-nav{position:relative;width:980px;margin:0 auto;top:-15px;z-index:10}
#site-nav ul{list-style:none;display:flex;width:100%}
#site-nav .top-item{flex:1;position:relative;background:#fff}
#site-nav .top-item>a{display:flex;align-items:center;justify-content:center;gap:6px;
  font-family:spinnaker,sans-serif;font-size:12px;line-height:normal;color:#2f2e2e;
  text-decoration:none;padding:14px 8px;letter-spacing:.05em}
#site-nav .top-item>a:hover,#site-nav li.active>a{color:#000}
#site-nav .top-item.active{background:rgb(var(--color_12))}
#site-nav .arrow{width:9px;height:6px;transition:transform .15s}
#site-nav .top-item:hover .arrow{transform:rotate(180deg)}
#site-nav .submenu{position:absolute;top:100%;left:0;width:100%;background:#fff;display:none;
  box-shadow:0 1px 4px rgba(0,0,0,.2);z-index:20}
#site-nav .top-item:hover .submenu,#site-nav .top-item:focus-within .submenu{display:block}
#site-nav .submenu a{display:block;padding:9px 14px;font-size:12px;color:#2f2e2e;text-decoration:none;line-height:1.4}
#site-nav .submenu a:hover{background:rgb(var(--color_22));color:#000}

/* ---- page canvas ---- */
.page-canvas{width:980px;margin:0 auto;background:rgb(var(--color_11));min-height:200px}

/* ---- sections/strips: geometry injected per page ---- */
.mesh{position:relative}
.mesh>.m{position:relative}
section.block{position:relative}
.strip{position:relative;display:flex;width:100%}
.strip>.col{position:relative}

/* rich text base */
.rt p{margin:0}
.rt h1,.rt h2,.rt h3,.rt h4,.rt h5{font-weight:normal;margin:0}
.rt h1{font:var(--font_0);color:rgb(var(--color_45))}
.rt h2{font:var(--font_2);color:rgb(var(--color_45))}
.rt h3{font:var(--font_6);color:rgb(var(--color_46))}
.rt h4{font:var(--font_7);color:rgb(var(--color_46))}
.rt p{font:var(--font_9);color:rgb(var(--color_46))}
.rt.p0 p,.rt.p0 h1{font-size:inherit}
.font_0{font:var(--font_0);color:rgb(var(--color_45))}
.font_2{font:var(--font_2);color:rgb(var(--color_45))}
.font_3{font:var(--font_3);color:rgb(var(--color_45))}
.font_4{font:var(--font_4);color:rgb(var(--color_45))}
.font_5{font:var(--font_5);color:rgb(var(--color_46))}
.font_6{font:var(--font_6);color:rgb(var(--color_46))}
.font_7{font:var(--font_7);color:rgb(var(--color_46))}
.font_8{font:var(--font_8);color:rgb(var(--color_14))}
.font_9{font:var(--font_9);color:rgb(var(--color_15))}

/* images */
.img-blk img{display:block}

/* buttons */
.gr-button{display:inline-block;font-family:spinnaker,sans-serif;font-size:14px;line-height:1.4;
  text-decoration:none;text-align:center;padding:10px 18px;cursor:pointer;border-style:solid;border-width:1px}

/* forms */
.frm{width:100%}
.frm label{display:block;font-family:spinnaker,sans-serif;font-size:14px;color:#4C443C;margin:10px 0 4px}
.frm label .req{color:#9F2747}
.frm input[type=text],.frm input[type=email],.frm input[type=tel],.frm input[type=date],.frm select,.frm textarea{
  width:100%;padding:8px 10px;font-family:spinnaker,sans-serif;font-size:14px;color:#2f2e2e;
  border:1px solid rgb(var(--color_13));background:#fff;border-radius:0}
.frm textarea{min-height:90px;resize:vertical}
.frm input:focus,.frm select:focus,.frm textarea:focus{outline:1px solid rgb(var(--color_18));border-color:rgb(var(--color_18))}
.frm .chk{display:flex;gap:8px;align-items:flex-start;margin:8px 0;font-size:13px;color:#4C443C}
.frm .chk input{margin-top:2px}
.frm-note{font-size:12px;color:#6E655B;margin-top:10px}

/* horizontal lines */
.hr{border-top:2px solid rgb(var(--color_18));width:100%}

/* gallery */
.gallery{position:relative;width:100%}
.gallery .gslides{position:relative;width:100%;overflow:hidden}
.gallery img.gi{display:none;width:100%;height:auto}
.gallery img.gi.first{display:block}
.gallery .gnav{display:flex;gap:8px;margin-top:10px}
.gallery .gnav button{border:1px solid rgb(var(--color_13));background:#fff;cursor:pointer;
  padding:4px 12px;font-family:spinnaker,sans-serif;font-size:13px;color:#2f2e2e}
.gallery .gnav button:hover{background:rgb(var(--color_22))}
.gallery .gnav .gcount{font-size:12px;color:#6E655B;align-self:center}

/* footer */
#SITE_FOOTER{background:rgb(var(--color_11));position:relative;padding:20px 0 24px}
#SITE_FOOTER .mesh{position:relative;width:980px;margin:0 auto;min-height:130px}
.ft-links{position:absolute;left:0;top:20px;font-family:spinnaker,sans-serif;font-size:13px;color:#2f2e2e;line-height:1.9}
.ft-links a{color:#2f2e2e;text-decoration:none}
.ft-links a:hover{text-decoration:underline}
.ft-social{position:absolute;left:311px;top:20px;display:flex;gap:8px}
.ft-social img{width:24px;height:24px}
.ft-note{position:absolute;left:504px;top:20px;font-size:13px;color:#2f2e2e;font-family:spinnaker,sans-serif}
.ft-note a{color:#2f2e2e;text-decoration:none}
.ft-note a:hover{text-decoration:underline}

/* small screens: stack, keep colors/type */
@media (max-width:1000px){
  .page-canvas{width:100%}
  #site-nav{width:100%;top:0}
  #site-nav ul{flex-wrap:wrap}
  #site-nav .top-item{flex:1 1 50%}
  #SITE_HEADER .mesh{min-height:0;padding:18px 0 8px}
  .hdr-logo{margin:0 auto;transform:none;position:static;width:160px}
  .hdr-logo img{width:160px;height:157px}
  .hdr-line1,.hdr-line2{display:none}
  .strip{flex-direction:column}
  .strip>.col{width:100%!important}
  .mesh>.m{position:static!important;margin:8px 10px!important;left:auto!important;transform:none!important;width:auto!important}
  .ft-links,.ft-social,.ft-note{position:static;margin:10px 16px;display:block}
  #SITE_FOOTER .mesh{width:100%;min-height:0}
}
'''

with open(OUT + '/style.css', 'w', encoding='utf-8') as f:
    f.write(CSS)

# ---------------------------------------------------------------- per-page css (mesh geometry)
def page_css(pg, css_raw):
    """Pull the page's inline mesh CSS, filtered to rules our DOM keeps."""
    path = BASE + ('/' + pg['slug'] if pg['slug'] else '') + '/index.html'
    raw = open(path, encoding='utf-8').read()
    blocks = re.findall(r'<style[^>]*>(.*?)</style>', raw, re.S)
    out = []
    for b in blocks:
        if '@font-face' in b or '@keyframes' in b:
            # strip those, keep only comp/mesh rules
            b2 = re.sub(r'@font-face\s*\{[^}]*\}*', '', b)
            b2 = re.sub(r'@keyframes\s+[^{]+\{(?:[^{}]*\{[^}]*\})*[^{}]*\}', '', b2)
            b = b2
        # keep only rules that start with our kept selectors
        kept = []
        for m in re.finditer(r'([^{}]+)\{([^}]*)\}', b):
            sel = m.group(1).strip()
            body = m.group(2)
            if sel.startswith(('#comp-', '#SITE_', '#PAGES_', '#masterPage', '#pageBackground',
                               '[data-mesh-id=', '#dukwo', '#Container', '#WPht', '#FvGr',
                               '#DrpDwnMn0', '#iazg', '#soapAfterPagesContainer')):
                if sel.startswith(('#DrpDwnMn0', '#iazg', '#soapAfterPagesContainer')):
                    continue  # replaced by clean header css
                kept.append((sel, body))
        if kept:
            out.append(''.join('%s{%s}' % (s, bdy) for s, bdy in kept))
    return '\n'.join(out)

# ---------------------------------------------------------------- block renderers
def esc(s):
    return html.escape(s, quote=True)

def render_text(b, depth_css):
    blocks = b['blocks']
    wcss = ''
    if b.get('w'):
        wcss = 'width:%dpx;' % int(b['w'])
    html_parts = []
    for blk in blocks:
        tag = blk['tag']
        cls = (' class="%s"' % blk['class']) if blk.get('class') else ''
        style = (' style="%s"' % esc(blk['style'])) if blk.get('style') else ''
        html_parts.append('<%s%s%s>%s</%s>' % (tag, cls, style, blk['html'], tag))
    return '<div class="rt m %s" style="%s">%s</div>' % ('', wcss, ''.join(html_parts))

def render_image(b, cur):
    src = b['src']
    w = b.get('w'); h = b.get('h')
    dim = ''
    if w:
        dim += 'width:%dpx;' % int(w)
    if h:
        dim += 'height:%dpx;' % int(h)
    return ('<div class="img-blk m" style="%s"><img src="%s" alt="%s"%s%s loading="lazy"></div>'
            % (dim, src, esc(b.get('alt', '')),
               (' width="%d"' % int(w)) if w else '',
               (' height="%d"' % int(h)) if h else ''))

def render_button(b, cur):
    href = fix_href(b['href'], cur)
    if href.startswith('http') or href.startswith('mailto'):
        target = ' target="_blank" rel="noopener"'
    else:
        target = ''
    style = ''
    c = b.get('colors', {})
    if c.get('bg'):
        style += 'background:%s;' % c['bg']
    if c.get('fg'):
        style += 'color:%s;' % c['fg']
    if c.get('border'):
        style += 'border-color:%s;' % c['border']
    return ('<a class="gr-button m" style="%s" href="%s"%s>%s</a>'
            % (style, esc(href, quote=True), target, esc(b['label'])))

def render_line(b):
    style = ''
    if b.get('colors', {}).get('bg'):
        style += 'border-color:%s;' % b['colors']['bg']
    return '<div class="hr m" style="%s"></div>' % style

def render_form(b, cur):
    fields = b['fields']
    parts = []
    for f in fields:
        rid = 'f_' + re.sub(r'[^a-zA-Z0-9_]', '_', f.get('name') or f['label'][:8])
        req = ' <span class="req">*</span>' if f.get('required') else ''
        reqattr = ' required' if f.get('required') else ''
        ph = (' placeholder="%s"' % esc(f['placeholder'])) if f.get('placeholder') else ''
        if f['kind'] == 'select':
            opts = ''.join('<option>%s</option>' % esc(o) for o in f.get('options', []))
            parts.append('<label for="%s">%s%s</label><select id="%s" name="%s"%s>%s</select>'
                         % (rid, esc(f['label']), req, rid, esc(f['name']), reqattr, opts))
        elif f['kind'] == 'textarea':
            parts.append('<label for="%s">%s%s</label><textarea id="%s" name="%s"%s%s></textarea>'
                         % (rid, esc(f['label']), req, rid, esc(f['name']), reqattr, ph))
        elif f['type'] == 'date':
            parts.append('<label for="%s">%s%s</label><input type="date" id="%s" name="%s"%s>'
                         % (rid, esc(f['label']), req, rid, esc(f['name']), reqattr))
        else:
            parts.append('<label for="%s">%s%s</label><input type="%s" id="%s" name="%s"%s%s>'
                         % (rid, esc(f['label']), req, esc(f['type']), rid, esc(f['name']), reqattr, ph))
    btn = b.get('button')
    btnhtml = ''
    if btn:
        btnhtml = render_button({'label': btn['label'], 'href': btn.get('href', '#'),
                                 'colors': btn.get('colors', {})}, cur)
    else:
        btnhtml = '<button class="gr-button" type="submit">Submit</button>'
    note = '<p class="frm-note">This form opens your email app - or write us directly at grazecatercda@gmail.com.</p>'
    return '<form class="frm m" action="mailto:grazecatercda@gmail.com" method="post" enctype="text/plain">%s%s%s</form>' % (''.join(parts), btnhtml, note)

def render_field(b, cur):
    f = b['field']
    return render_form({'fields': [f], 'checks': [], 'blocks': [], 'button': None}, cur)

def render_gallery(b, cur):
    items = b['items']
    slides = ''.join('<img class="gi%s" src="%s" alt="" loading="lazy">' % (' first' if i == 0 else '', it['src'])
                     for i, it in enumerate(items))
    gid = 'g' + re.sub(r'[^a-zA-Z0-9]', '', b['id'])
    return ('<div class="gallery m" id="%s" data-n="%d"><div class="gslides">%s</div>'
            '<div class="gnav"><button type="button" data-d="-1">&larr;</button>'
            '<span class="gcount">1 / %d</span><button type="button" data-d="1">&rarr;</button></div></div>'
            % (gid, len(items), slides, len(items)))

def render_block(b, cur):
    t = b['type']
    if t == 'text':
        return render_text(b, None)
    if t == 'image':
        return render_image(b, cur)
    if t == 'button':
        return render_button(b, cur)
    if t == 'line':
        return render_line(b)
    if t == 'form':
        return render_form(b, cur)
    if t == 'field':
        return render_field(b, cur)
    if t == 'gallery':
        return render_gallery(b, cur)
    return ''

def render_strip(b, cur):
    cols = b['columns']
    parts = []
    style = ''
    if b.get('bgcolor'):
        style = 'background:%s;' % b['bgcolor']
    for c in cols:
        cstyle = ''
        if c.get('bgcolor') and c['bgcolor'] != 'transparent':
            cstyle += 'background:%s;' % c['bgcolor']
        if c.get('bgimg'):
            cstyle += ("background-image:url('%s');background-size:cover;background-position:center;"
                       "min-height:%dpx" % (c['bgimg']['src'], c['bgimg'].get('h') or 400))
        inner = ''.join(render_block(bb, cur) for bb in c['blocks'])
        parts.append('<div class="col" style="%s">%s</div>' % (cstyle, inner))
    return '<div class="strip" style="%s">%s</div>' % (style, ''.join(parts))

def render_section(b, cur, idx):
    style = ''
    if b.get('bgcolor'):
        style = 'background:%s;' % b['bgcolor']
    inner = ''.join(render_block(bb, cur) for bb in b['blocks'])
    return '<section class="block" id="sec%d" style="%s">%s</section>' % (idx, style, inner)

# ---------------------------------------------------------------- chrome
def build_nav(cur):
    items = []
    for it in CHROME['nav']:
        label = it['label']
        href = it['href']
        target_slug = None
        # resolve nav href (mirror-relative from home)
        full = os.path.normpath(os.path.join(BASE, href)).replace(chr(92), '/')
        rel = os.path.relpath(full, BASE).replace(chr(92), '/')
        parts = [x for x in rel.split('/') if x]
        if parts and parts[-1] == 'index.html':
            parts = parts[:-1]
        target_slug = '/'.join(parts)
        phref = page_href(target_slug, cur)
        active = (target_slug == cur) or (cur == '' and target_slug == '')
        sub = ''
        if it['sub']:
            links = []
            for s in it['sub']:
                full2 = os.path.normpath(os.path.join(BASE, s['href'])).replace(chr(92), '/')
                rel2 = os.path.relpath(full2, BASE).replace(chr(92), '/')
                p2 = [x for x in rel2.split('/') if x]
                if p2 and p2[-1] == 'index.html':
                    p2 = p2[:-1]
                s2 = '/'.join(p2)
                links.append('<a href="%s">%s</a>' % (page_href(s2, cur), esc(s['label'])))
            sub = '<ul class="submenu">%s</ul>' % ''.join(links)
            arrow = '<svg class="arrow" viewBox="0 0 16 11" fill="black" xmlns="http://www.w3.org/2000/svg"><path d="M8 10.5L16 1.86193L14.7387 0.5L8 7.77613L1.26133 0.499999L-5.95321e-08 1.86193L8 10.5Z"></path></svg>'
        else:
            arrow = ''
        cls = 'top-item active' if active else 'top-item'
        items.append('<li class="%s"><a href="%s">%s%s</a>%s</li>'
                     % (cls, phref, esc(label), arrow, sub))
    return '<nav id="site-nav"><ul>%s</ul></nav>' % ''.join(items)

def header_html(cur):
    logo = CHROME['header_images'][0] if CHROME['header_images'] else None
    logo_img = '<img src="img/logo.png" alt="Graze &amp; Rosé">' if logo is None else \
        '<img src="%s" alt="Graze &amp; Rosé" width="%d" height="%d">' % (
            logo['src'], logo.get('w') or 227, logo.get('h') or 222)
    return ('<header id="SITE_HEADER"><div class="mesh">'
            '<div class="hdr-logo"><a href="%s">%s</a></div>'
            '<div class="hdr-line1"></div><div class="hdr-line2"></div>'
            '</div>%s</header>'
            % (page_href('', cur), logo_img, build_nav(cur)))

FOOT_LINKS = [
    ('Privacy Policy', 'https://www.privacypolicygenerator.info/live.php?token=fJzfJ1AdhRNVJmtSGs6DPeBxhPW7pMIR'),
    ('Contact Us', 'mailto:grazecatercda@gmail.com'),
    ('Catering Service Terms', 'FILE:files/catering-service-terms.pdf'),
]

def footer_html(cur):
    links = ''.join('<a href="%s"%s>%s</a><br>'
                    % (v.replace('FILE:', ''), ' target="_blank" rel="noopener"' if v.startswith('http') else '',
                       esc(k)) for k, v in FOOT_LINKS)
    social = ('<div class="ft-social">'
              '<a href="https://www.instagram.com/graze.and.rose" target="_blank" rel="noopener" aria-label="Instagram">'
              '<img src="img/social-instagram.png" alt="Instagram"></a>'
              '<a href="https://www.facebook.com/graze.and.rose" target="_blank" rel="noopener" aria-label="Facebook">'
              '<img src="img/social-facebook.png" alt="Facebook"></a></div>')
    note = ('<div class="ft-note">Do Not Sell My Personal Information<br>'
            '<a href="mailto:grazecatercda@gmail.com">grazecatercda@gmail.com</a></div>')
    return ('<footer id="SITE_FOOTER"><div class="mesh">'
            '<div class="ft-links">%s</div>%s%s</div></footer>' % (links, social, note))

# ---------------------------------------------------------------- gallery js (tiny)
JS = '''// Graze & Rose - minimal page behavior (galleries)
document.querySelectorAll('.gallery').forEach(function(g){
  var imgs = g.querySelectorAll('img.gi'), i = 0, n = imgs.length;
  var count = g.querySelector('.gcount');
  g.querySelectorAll('.gnav button').forEach(function(btn){
    btn.addEventListener('click', function(){
      imgs[i].classList.remove('first');
      i = (i + parseInt(btn.dataset.d, 10) + n) % n;
      imgs[i].classList.add('first');
      if (count) count.textContent = (i+1) + ' / ' + n;
    });
  });
});
// mailto forms: assemble body from fields
document.querySelectorAll('form.frm').forEach(function(f){
  f.addEventListener('submit', function(ev){
    ev.preventDefault();
    var parts = [];
    f.querySelectorAll('input,select,textarea').forEach(function(inp){
      if (!inp.name) return;
      var lab = '';
      var l = f.querySelector('label[for="'+inp.id+'"]');
      if (l) lab = l.textContent.replace('*','').trim();
      parts.push(lab + ': ' + (inp.value || ''));
    });
    var subj = 'Inquiry from grazeandrose.com';
    var first = f.querySelector('input');
    location.href = 'mailto:grazecatercda@gmail.com?subject=' + encodeURIComponent(subj)
      + '&body=' + encodeURIComponent(parts.join('\\n'));
  });
});
'''

with open(OUT + '/site.js', 'w', encoding='utf-8') as f:
    f.write(JS)

# ---------------------------------------------------------------- render pages
DEPTH = {}   # slug -> depth for asset prefixing (site is root-based; pages use ../)
for pg in PAGES:
    slug = pg['slug']
    pdir = os.path.join(OUT, slug.replace('/', os.sep)) if slug else OUT
    os.makedirs(pdir, exist_ok=True)
    cur = slug
    prefix = '../' * (slug.count('/') + 1) if slug else ''

    secs = []
    for i, s in enumerate(pg['sections']):
        secs.append(render_section(s, cur, i))
    pagecss = page_css(pg, None)

    # rewrite mirror asset paths inside injected css to site-root paths
    pagecss = pagecss.replace('../../_assets/', prefix + 'assets/' if False else '../' * 1 + '_assets_old/')  # placeholder, fixed below

    title = pg['title'] or 'Graze and Rosé Catering'
    head = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>%s</title>\n' % esc(title))
    if pg['desc']:
        head += '<meta name="description" content="%s">\n' % esc(pg['desc'].replace('\n', ' '))
    head += ('<link rel="icon" href="%sfavicon.png" type="image/png">\n'
             '<link rel="stylesheet" href="%sstyle.css">\n' % (prefix, prefix))
    if pagecss:
        head += '<style>%s</style>\n' % pagecss
    body = ('%s<div id="page"><div class="page-canvas">%s</div></div>%s'
            % (header_html(cur), ''.join(secs), footer_html(cur)))
    doc = head + '</head>\n<body>\n<div id="site">' + body + \
        '<script src="%ssite.js"></script>\n</div>\n</body>\n</html>\n' % prefix
    with open(os.path.join(pdir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(doc)

# favicon + logo
fav = '_assets/static.wixstatic.com/media/d69fc6_a3f7111fb96c4512a137accc098d0bc7~mv2__0f2d0e1640.png'
if os.path.exists(fav):
    shutil.copyfile(fav, OUT + '/favicon.png')

print("pages written:", len(PAGES))
print("images:", len(img_stats))
tot = sum(os.path.getsize(os.path.join(dp, fn)) for dp, dn, fnl in os.walk(OUT) for fn in fnl)
print("site size: %.1f MB" % (tot / 1048576))
