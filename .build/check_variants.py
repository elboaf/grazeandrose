import re, glob, os, collections
files = glob.glob('_assets/static.wixstatic.com/media/*')
byid = collections.defaultdict(list)
for f in files:
    name = os.path.basename(f)
    base = name.split('__')[0]
    byid[base].append(f)

used = collections.defaultdict(set)
for p in glob.glob('out/**/index.html', recursive=True):
    c = open(p, encoding='utf-8').read()
    for m in re.findall(r'src="[^"]*media/([^"]+)"', c):
        used[m.split('__')[0]].add(m)

worse = 0
for base, variants in sorted(byid.items()):
    if base not in used:
        continue
    sizes = {v: os.path.getsize(v) for v in variants}
    biggest = max(sizes.values())
    for uv in used[base]:
        f = os.path.join('_assets', 'static.wixstatic.com', 'media', uv.replace('/', os.sep))
        if os.path.exists(f) and os.path.getsize(f) < biggest * 0.5:
            worse += 1
            print("SUBOPTIMAL:", uv[:80], os.path.getsize(f)//1024, "KB < best", biggest//1024, "KB")
print("media ids used:", len(used), "| suboptimal:", worse)
