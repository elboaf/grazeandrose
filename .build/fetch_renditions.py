"""Download the live wixstatic renditions for every fill/LQIP image.

Wix's runtime swaps blurry placeholders for rendition URLs computed from the
media id + container size. Those renditions are deterministic, so we fetch
exactly what the live site serves and use them in the static rebuild.
"""
import glob, html, json, os, re, time
import urllib.request

OUTDIR = 'downloads'
os.makedirs(OUTDIR, exist_ok=True)

jobs = {}   # (uri, w, h) -> out filename
for p in glob.glob('www.grazeandrose.com/**/index.html', recursive=True):
    if '.bak' in p:
        continue
    h = open(p, encoding='utf-8').read()
    for m in re.finditer(r'data-image-info="([^"]*)"', h):
        try:
            d = json.loads(html.unescape(m.group(1)))
        except Exception:
            continue
        imgdata = d.get('imageData') or {}
        uri = imgdata.get('uri')
        tw, th = d.get('targetWidth'), d.get('targetHeight')
        if not uri or not tw or not th:
            continue
        key = (uri, int(tw), int(th))
        if key not in jobs:
            jobs[key] = f"{uri.split('~')[0]}__w{tw}xh{th}.jpg"

print("renditions to fetch:", len(jobs))
ok = fail = 0
for (uri, w, h), fname in sorted(jobs.items()):
    dst = os.path.join(OUTDIR, fname)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        ok += 1
        continue
    url = (f"https://static.wixstatic.com/media/{uri}"
           f"/v1/fill/w_{w},h_{h},al_c,q_80,usm_0.66_1.00_0.01,enc_avif,quality_auto/{uri}")
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=30).read()
            with open(dst, 'wb') as f:
                f.write(data)
            ok += 1
            break
        except Exception as e:
            if attempt == 0:
                time.sleep(2)
            else:
                fail += 1
                print("FAIL:", uri[:40], w, h, str(e)[:60])
print(f"downloaded ok={ok} fail={fail}")
