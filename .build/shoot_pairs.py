"""Screenshot every page of mirror vs pruned site (JS disabled) and diff."""
import os, sys
from playwright.sync_api import sync_playwright

MIRROR_PORT = 8125
NEW_PORT = 8124
PAGES = [''] + [s.strip() for s in open('.build/graph.json').read().split('"reachable": [')[1].split(']')[0].replace('"', '').replace('\n', '').split(',') if s.strip()]
OUTDIR = '.build/shots'
os.makedirs(OUTDIR, exist_ok=True)

def url(port, slug):
    return f'http://localhost:{port}/{ "www.grazeandrose.com/" if port == MIRROR_PORT else "" }{slug + "/" if slug else ""}index.html'

def shot(page, url, path):
    page.goto(url, wait_until='load', timeout=30000)
    page.wait_for_timeout(700)
    page.screenshot(path=path, full_page=True)

results = []
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', headless=True)
    ctx = b.new_context(viewport={'width': 1440, 'height': 1000}, java_script_enabled=False)
    pg = ctx.new_page()

    for slug in PAGES:
        name = slug.replace('/', '_') or 'home'
        mpath = f'{OUTDIR}/m_{name}.png'
        npath = f'{OUTDIR}/n_{name}.png'
        try:
            shot(pg, url(MIRROR_PORT, slug), mpath)
            okm = True
        except Exception as e:
            okm = False
            print("mirror fail:", slug, str(e)[:80])
        try:
            shot(pg, url(NEW_PORT, slug), npath)
            okn = True
        except Exception as e:
            okn = False
            print("new fail:", slug, str(e)[:80])
        print('.', end='', flush=True)
    b.close()
print("\nscreenshots done")
