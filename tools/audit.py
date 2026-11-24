#!/usr/bin/env python3
"""Full self-audit for news-image-20261124, winner-family build
(35 checks, spec from the FINAL20 gap report: cream page, dark
share BAND 0.12-0.20, thumbnail dark @256 BAND 0.08-0.26, 13 drawn
cards = 3 leads + 10 standard, 19 briefs, 32 stories total, light
map 440x205, stat numerals 32px red #b3271e, region legend sums
to 32: Europe 7, Asia-Pacific 8, Americas 5, Mideast 5, Africa 3,
Oceania 2, World/Space 2 — counted by subject, so card 3, the
Riyadh tower statement, counts to Mideast, and brief 30, the
Houthi push on Aden, counts to Mideast too.

Advantage round (2026-11-25 ~02:00 WIB): leads reordered (Zaporizhzhia
1st), cards 4/5 CONFIRMED, brief 23 Sigonella, brief 29 AP.

Fit parameters: lead art 300x80, standard art 190x58, masthead
set at 66px so the full date fits one line, and the page's natural
content height fits the 1024px budget (see tools/render.py --measure).

Check 10 verifies the pill INTENT: the page is split into its
<article> cards and every card must carry exactly one pill. The pill
legend beside the briefs reuses the same chip markup for its key, so
a naive page-wide count would add the 4 legend chips to the 13 card
pills; scoping the count to card markup keeps the check honest — it
still fails the moment any single card loses its pill.

Checks the HTML for content rules and the PNG for measurement gates.
Usage: python3 tools/audit.py
"""
import re, sys
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / 'frontpage.html').read_text()
png = ROOT / 'entry.png'
im = Image.open(png).convert('RGB')
W, H = im.size
a = np.asarray(im.convert('L')).astype(int)
rgb = np.asarray(im).astype(int)

ok, fail = [], []
def chk(name, cond, detail=''):
    (ok if cond else fail).append(f"{name} {detail}")

print(f"== PNG {W}x{H} ==")
dark = float((a < 110).mean())
red = float(((rgb[:, :, 0] > 150) & (rgb[:, :, 1] < 100) & (rgb[:, :, 2] < 100)).mean())
t256 = np.asarray(im.convert('L').resize((256, 256)))
tdark = float((t256 < 110).mean())
chk('01 dark share in 0.12-0.20 band', 0.12 <= dark <= 0.20, f'{dark:.3f}')
chk('02 red share >=0.010', red >= 0.010, f'{red:.4f}')
chk('03 thumb dark @256 in 0.08-0.26 band', 0.08 <= tdark <= 0.26, f'{tdark:.3f}')
bright = (a > 200)
rows = bright[10:200].mean(axis=1)
dense = rows > 0.25
blocks, start = [], None
for i, v in enumerate(dense):
    if v and start is None: start = i
    if (not v or i == len(dense) - 1) and start is not None:
        blocks.append((start + 10, (i - 1 if not v else i) + 10)); start = None
top, bot = max(blocks, key=lambda b: b[1] - b[0])
seg = bright[top:bot + 1, 20:W - 20]
cols = np.where(seg.any(axis=0))[0]
span = (cols.max() - cols.min() + 1) / W
chk('04 date cap >=84px', bot - top + 1 >= 84, f'{bot - top + 1}px')
chk('05 date span >=92%', span >= 0.92, f'{span:.2%}')
chk('06 file <=700KB', png.stat().st_size <= 700 * 1024, f'{png.stat().st_size}B')
chk('07 size 1024x1024', (W, H) == (1024, 1024))

print("== HTML content ==")
kickbars = re.findall(r'class="kickbar">(\d+) &middot; ([^&<]+) &middot; ([^<]+)</div>', html)
chk('08 kickbar on 13/13 cards', len(kickbars) == 13, f'{len(kickbars)}')
srcs = re.findall(r'<div class="src">', html)
chk('09 source line on 13/13 cards', len(srcs) == 13, f'{len(srcs)}')
articles = re.findall(r'<article.*?</article>', html, re.S)
card_pills = [re.findall(r'class="pill p-[a-z]+">([A-Z]+)</span>', art) for art in articles]
flat_pills = [p for ps in card_pills for p in ps]
chk('10 pill on 13/13 cards', len(articles) == 13 and all(len(ps) == 1 for ps in card_pills),
    f'{len(flat_pills)} card pills on {len(articles)} cards, per-card {[len(ps) for ps in card_pills]}')
chk('11 max 4 pill labels', len(set(flat_pills)) <= 4, f'{sorted(set(flat_pills))}')
lead_art = re.findall(r'<svg viewBox="0 0 300 80"', html)
std_art = re.findall(r'<svg viewBox="0 0 190 58"', html)
chk('12 lead art 300x80 x3', len(lead_art) == 3, f'{len(lead_art)}')
chk('13 standard art 190x58 x10', len(std_art) == 10, f'{len(std_art)}')
h3s = re.findall(r'<h3>(.*?)</h3>', html)
h3s = [re.sub(r'&[^;]+;', ' ', h).strip() for h in h3s]
chk('14 13 headlines', len(h3s) == 13, f'{len(h3s)}')
long_h3 = [h for h in h3s if len(h.split()) > 9]
chk('15 headlines <=9 words', not long_h3, f'over-long: {long_h3}')
briefs = re.findall(r'<div class="brief">', html)
chk('16 19 briefs', len(briefs) == 19, f'{len(briefs)}')
bsrc = re.findall(r'<div class="brief">.*?<span class="bsrc">', html)
chk('17 >=80% briefs sourced', len(bsrc) >= 0.8 * 19, f'{len(bsrc)}/19')
stops = re.findall(r'<div class="stop">', html)
chk('18 exactly 8 timeline stops', len(stops) == 8, f'{len(stops)}')
deck = re.search(r'class="sub">(.*?)</div>', html, re.S).group(1)
deck_low = deck.lower()
chk('19 deck names top-3 (Riyadh/tariffs/Zaporizhzhia)',
    all(w in deck_low for w in ['riyadh', 'tariffs', 'zaporizhzhia']), deck[:90])
dc = re.search(r'class="datecheck">(.*?)</div>\s*</div>', html, re.S).group(1)
chk('20 DATE CHECK heading', 'date check' in dc.lower() and ('&#10003;' in dc or '\u2713' in dc))
chk('21 >=6 exclusions', dc.count('&middot;') >= 6, f"{dc.count('&middot;')} separators")
chk('22 >=2 Not yet', dc.count('Not yet') >= 2, f"{dc.count('Not yet')} found")
chk('23 positive claim sentence', 'Every story here is Tuesday 24 November 2026' in dc)
verdict = re.search(r'class="verdict">(.*?)</div>\s*</div>', html, re.S).group(1)
vp = re.sub(r'<[^>]+>', '', verdict)
words = [w for w in vp.replace('THE VERDICT', '').split() if w.strip()]
chk('24 verdict <=14 words + number', len(words) <= 14 and any(c.isdigit() for c in vp),
    f'{len(words)} words: {" ".join(words)}')
chips = [int(x) for x in re.findall(r'<b>(\d+)</b><span>(?:Asia-Pacific|Europe|Americas|Mideast|Africa|Oceania|World / Space)</span>', html)]
chk('25 region legend sums to 32', sum(chips) == 32 and len(chips) == 7, f'{chips} sum={sum(chips)}')
chk('26 eyebrow 32 stories / 7 regions / 13 drawn',
    '32 stories' in html and '7 regions' in html and '13 drawn' in html)
css = re.search(r'<style>(.*?)</style>', html, re.S).group(1)
sizes = sorted(set(float(x) for x in re.findall(r'font-size:\s*([\d.]+)px', css)))
small = [s for s in sizes if s < 8.5]
chk('27 no CSS text <8.5px except footer 8px',
    small == [8.0] or not small, f'CSS sizes: {sizes}')
svg_sizes = sorted(set(float(x) for x in re.findall(r'<text[^>]*font-size="([\d.]+)"', html)))
chk('28 smallest SVG text >=9px', min(svg_sizes) >= 9, f'min {min(svg_sizes)}px; all: {svg_sizes}')
chk('29 stat numerals red 32px', '#b3271e' in css and 'font-size:32px' in css.replace(' ', ''))
chk('30 map SVG 440x205', 'width="440" height="205"' in html)
chk('31 legend line under map', 'maplegend' in html and 'PINS 1' in html.upper())
chk('32 date given as 24 NOVEMBER', '24 NOVEMBER' in html)
chk('33 6 stats in strip', len(re.findall(r'<div class="stat">', html)) == 6,
    f"{len(re.findall(chr(60)+'div class=\"stat\"'+chr(62), html))}")
chk('34 footer integrity line', 'Every story here is Tuesday 24 November 2026' in html)
dcspan = re.search(r'class="datecheck">.*?</div>\s*</div>', html, re.S)
outside = html[:dcspan.start()] + html[dcspan.end():] if dcspan else html
chk('35 no 23-November dating outside DATE CHECK', '23 November' not in outside,
    f"'23 November' outside datecheck: {'23 November' in outside}")

print()
print('PASS:'); [print('  [x]', x) for x in ok]
print('FAIL:'); [print('  [ ]', x) for x in fail]
print(f"\n{len(ok)} pass, {len(fail)} fail")
sys.exit(1 if fail else 0)
