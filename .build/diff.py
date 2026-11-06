"""Pixel-diff mirror vs pruned screenshots; report per-page verdicts."""
import os, glob
from PIL import Image, ImageChops

OUTDIR = '.build/shots'
report = []
for mpath in sorted(glob.glob(OUTDIR + '/m_*.png')):
    name = os.path.basename(mpath)[2:]
    npath = os.path.join(OUTDIR, 'n_' + name)
    if not os.path.exists(npath):
        report.append((name, 'MISSING NEW', 0, 0))
        continue
    a = Image.open(mpath).convert('RGB')
    b = Image.open(npath).convert('RGB')
    # normalize height: compare the overlapping region (top-aligned)
    h = min(a.size[1], b.size[1])
    a2, b2 = a.crop((0, 0, a.size[0], h)), b.crop((0, 0, b.size[0], h))
    diff = ImageChops.difference(a2, b2)
    bbox = diff.getbbox()
    # quantize: fraction of pixels that differ by more than a small threshold
    g = diff.convert('L')
    hist = g.histogram()
    total = sum(hist)
    sig = sum(hist[24:])  # pixels differing by >= 24 gray levels
    frac = sig / total if total else 0
    verdict = 'MATCH' if frac < 0.02 else ('CLOSE' if frac < 0.08 else 'DIFF')
    report.append((name, verdict, frac, (bbox, a.size, b.size)))

for name, verdict, frac, extra in report:
    bs = f"{extra[2][0]}x{extra[2][1]} vs {extra[1][0]}x{extra[1][1]}" if isinstance(extra, tuple) else ''
    print(f"{name:55} {verdict:6} {frac*100:6.2f}%  {bs}")
