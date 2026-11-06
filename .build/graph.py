import re, glob, os, json
from collections import deque

BASE = 'www.grazeandrose.com'
pages = {}
for p in glob.glob(BASE + '/**/index.html', recursive=True):
    if '.bak' in p:
        continue
    d = os.path.relpath(os.path.dirname(p), BASE).replace(chr(92), '/')
    if d == '.':
        d = ''
    pages[d] = p.replace(chr(92), '/')
print(len(pages), "pages in mirror")

def slug_of_href(href, cur):
    href = href.split('#')[0].split('?')[0]
    if href.startswith('http') or href.startswith('mailto') or href.startswith('tel'):
        return None
    pagedir = os.path.join(BASE, cur)
    full = os.path.normpath(os.path.join(pagedir, href)).replace(chr(92), '/')
    rel = os.path.relpath(full, BASE).replace(chr(92), '/')
    if rel.startswith('..'):
        return None  # points outside the site tree (assets, etc.)
    parts = [x for x in rel.split('/') if x]
    if parts and parts[-1] == 'index.html':
        parts = parts[:-1]
    clean = '/'.join(parts)
    return clean if clean in pages else None

seen = ['']
q = deque([''])
edges = {}
while q:
    cur = q.popleft()
    hh = open(pages[cur], encoding='utf-8').read()
    outs = set()
    for m in re.finditer(r'href="([^"]+)"', hh):
        t = slug_of_href(m.group(1), cur)
        if t is not None:
            outs.add(t)
    edges[cur] = sorted(outs)
    for t in outs:
        if t not in seen:
            seen.append(t)
            q.append(t)

print("reachable:", len(seen))
for s in sorted(seen):
    print("  ", s if s else "(home)")
orphans = sorted(set(pages) - set(seen))
print("orphans:", orphans)
json.dump({'pages': pages, 'reachable': sorted(seen), 'edges': edges},
          open('.build/graph.json', 'w'), indent=1)
