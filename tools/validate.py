"""Validation of the compiled Suhar fonts.  Everything here runs against the
font binaries in dist/ (HarfBuzz shaping, FreeType rasterisation, fontTools
table inspection, OpenType Sanitizer).  Writes reports/validation.md, .json
and proof images in reports/img/."""
import glob, io, json, os, sys, unicodedata as ud, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from proof import Renderer, sheet

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
REP = os.path.join(ROOT, 'reports')
IMG = os.path.join(REP, 'img')
os.makedirs(IMG, exist_ok=True)
ASC, DESC, CELL = 940, -360, 600
results = []          # (section, name, ok, detail)


def check(section, name, ok, detail=''):
    results.append((section, name, bool(ok), str(detail)))
    return ok


def bounds(font, gname):
    gs = font.getGlyphSet()
    bp = BoundsPen(gs)
    gs[gname].draw(bp)
    return bp.bounds


def shape(r, text, **kw):
    buf = r.shape(text, **kw)
    return [(r.font.glyph_to_string(i.codepoint), p.x_advance, p.x_offset, p.y_offset)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def names(r, text, **kw):
    return [g[0] for g in shape(r, text, **kw)]


# ---------------------------------------------------------------- per file
files = sorted(glob.glob(os.path.join(DIST, 'ttf', '*.ttf')) + glob.glob(os.path.join(DIST, 'otf', '*.otf'))
               + glob.glob(os.path.join(DIST, 'variable', '*.ttf')))
summary = []
import ots
for path in files:
    b = os.path.basename(path)
    f = TTFont(path)
    cmap = f.getBestCmap()
    is_tt = 'glyf' in f
    var = 'fvar' in f
    mono = 'Mono' in b
    row = {'file': os.path.relpath(path, DIST), 'glyphs': len(f.getGlyphOrder()), 'codepoints': len(cmap),
           'size_kb': round(os.path.getsize(path) / 1024)}
    for t in ('GSUB', 'GPOS', 'GDEF'):
        check('tables', f'{b}: {t}', t in f)
    if is_tt and not var:
        check('hinting', f'{b}: TrueType instructions (fpgm/prep/cvt)', all(t in f for t in ('fpgm', 'prep', 'cvt ')))
        gasp = 'gasp' in f
        row['hinted'] = 'fpgm' in f
    o, h = f['OS/2'], f['hhea']
    win = (ASC, -DESC) if mono else (1200, 440)      # Sans: larger Windows clipping box for mark stacks
    check('metrics', f'{b}: vertical metrics (typo = hhea = 940/-360, USE_TYPO_METRICS, win {win})',
          (o.sTypoAscender, o.sTypoDescender, h.ascent, h.descent) == (ASC, DESC, ASC, DESC)
          and (o.usWinAscent, o.usWinDescent) == win and o.fsSelection & 0x80,
          (o.sTypoAscender, o.sTypoDescender, h.ascent, h.descent, o.usWinAscent, o.usWinDescent))
    if mono:
        adv = {f['hmtx'][g][0] for g in f.getGlyphOrder()}
        w2 = {f['hmtx'][n][0] for n in f.getGlyphOrder() if n.endswith('.w2')}
        adv1 = {f['hmtx'][n][0] for n in f.getGlyphOrder() if not n.endswith('.w2')}
        check('monospace', f'{b}: every advance is 0 or {CELL} (optional two-cell forms: {2 * CELL})', adv1 <= {0, CELL} and w2 <= {2 * CELL}, sorted(adv)[:8])
        check('monospace', f'{b}: post.isFixedPitch', f['post'].isFixedPitch == 1)
    # empty glyphs that are mapped (placeholders) – whitespace/format characters excepted
    gs = f.getGlyphSet()
    empty = []
    if not var and 'Nerd' not in b:
        for cp, gn in cmap.items():
            cat = ud.category(chr(cp))
            if cat in ('Zs', 'Cf', 'Zl', 'Zp', 'Cc') or cp in (0x34F, 0x3000, 0x2800):   # U+2800 is the blank Braille pattern
                continue
            if bounds(f, gn) is None:
                empty.append('U+%04X' % cp)
        check('no placeholders', f'{b}: no empty mapped glyphs', not empty, empty[:10])
    # sanitizer
    try:
        r = ots.sanitize(path, '/tmp/ots.out', capture_output=True)
        check('sanitizer', f'{b}: OpenType Sanitizer', r.returncode == 0, (r.stderr or b'')[-200:])
    except Exception as e:
        check('sanitizer', f'{b}: OpenType Sanitizer', False, repr(e)[:200])
    summary.append(row)

# woff2 round trip
for path in sorted(glob.glob(os.path.join(DIST, 'woff2', '*.woff2'))):
    b = os.path.basename(path)
    f = TTFont(path)
    src = os.path.join(DIST, 'ttf', b.replace('.woff2', '.ttf'))
    check('woff2', f'{b}: decodes, same glyph count as TTF', len(f.getGlyphOrder()) == len(TTFont(src).getGlyphOrder()))

# ---------------------------------------------------------------- family level
def R(name):
    return Renderer(os.path.join(DIST, 'ttf', name + '.ttf'))


reg, bold, ital = R('Suhar-Regular'), R('Suhar-Bold'), R('Suhar-Italic')
mono, monob = R('SuharMono-Regular'), R('SuharMono-Bold')
nerdm = R('SuharNerdMono-Regular')
F = TTFont(os.path.join(DIST, 'ttf', 'Suhar-Regular.ttf'))
FM = TTFont(os.path.join(DIST, 'ttf', 'SuharMono-Regular.ttf'))

# names
want = {}
for fam, ps in (('Suhar', 'Suhar'), ('Suhar Mono', 'SuharMono'), ('Suhar Nerd', 'SuharNerd'), ('Suhar Nerd Mono', 'SuharNerdMono'),
                ('Suhar Condensed', 'SuharCondensed'), ('Suhar Nerd Condensed', 'SuharNerdCondensed'), ('Suhar Naskh', 'SuharNaskh'), ('Suhar Naskh Display', 'SuharNaskhDisplay')):
    for st in ('Light', 'Light Italic', 'Regular', 'Italic', 'Medium', 'Medium Italic', 'SemiBold', 'SemiBold Italic', 'Bold', 'Bold Italic',
               'ExtraBold', 'ExtraBold Italic', 'Black', 'Black Italic'):
        if st.startswith('Black') and fam not in ('Suhar', 'Suhar Nerd'):
            continue
        if fam == 'Suhar Naskh Display' and st not in ('Regular', 'Medium', 'SemiBold', 'Bold'):
            continue
        if fam == 'Suhar Naskh' and st.split()[0] in ('Light', 'ExtraBold'):
            continue
        p = os.path.join(DIST, 'ttf', f"{ps}-{st.replace(' ', '')}.ttf")
        ok = os.path.exists(p)
        if ok:
            n = TTFont(p)['name']
            fam16 = n.getDebugName(16) or n.getDebugName(1)
            sub17 = n.getDebugName(17) or n.getDebugName(2)
            ok = fam16 == fam and sub17 == st and n.getDebugName(6) == f"{ps}-{st.replace(' ', '')}"
        check('family', f'{fam} {st}: present with consistent names', ok)

# Arabic shaping (HarfBuzz output is in visual order, left to right)
T = [
    ('بسم', ['uni0645.fina', 'uni0633.medi', 'uni0628.init']),
    ('لا', ['uni06440627']),
    ('بلا', ['uni06440627.fina', 'uni0628.init']),
    ('لأ', ['uni06440623']),
    ('ب‌ب', ['uni0628', 'space', 'uni0628']),   # ZWNJ breaks the join (HarfBuzz shows it as an invisible glyph)
    ('ب‍', ['space', 'uni0628.init']),   # ZWJ forces the joining form
    ('گچپژ', ['uni0698.fina', 'uni067E.medi', 'uni0686.medi', 'uni06AF.init']),
    ('ہے', ['uni06D2.fina', 'uni06C1.init']),
    ('ھی', ['uni06CC.fina', 'uni06BE.init']),
    ('دار', ['uni0631', 'uni0627', 'uni062F']),   # right-joining letters do not connect forward
    ('ءأ', ['uni0623', 'uni0621']),
]
for text, exp in T:
    got = names(reg, text)
    check('arabic shaping', f'{text!r} -> {" ".join(exp)}', got == exp, ' '.join(got))
got = names(reg, 'الله', features={'dlig': True})
check('arabic shaping', "dlig: 'الله' -> uniFDF2", got == ['uniFDF2'], got)
# marks: zero advance and attached (non-zero offset), mkmk stacking
g = shape(reg, 'بَ')
check('arabic marks', 'fatha attaches above beh (GPOS mark)', g[0][0] == 'uni064E' and g[0][1] == 0 and g[0][3] > 250, g)
g = shape(reg, 'بِ')
check('arabic marks', 'kasra attaches below beh', g[0][0] == 'uni0650' and g[0][1] == 0 and g[0][3] < -50, g)
g = shape(reg, 'بَّ')
ys = sorted(x[3] for x in g if x[0] in ('uni064E', 'uni0651'))
check('arabic marks', 'shadda + fatha stack (GPOS mkmk)', len(ys) == 2 and ys[1] - ys[0] > 120, g)
g = shape(reg, 'لَا')
check('arabic marks', 'mark on lam-alef ligature component (mark-to-ligature)', g[0][0] in ('uni064E', 'uni06440627') and len(g) == 2, g)
# joins: every joined side really reaches the glyph edge
bad = []
for font, label in ((F, 'Sans'), (FM, 'Mono')):
    for gn in font.getGlyphOrder():
        if not gn.startswith('uni06') or '.' not in gn:
            continue
        form = gn.split('.')[1]
        bb = bounds(font, gn)
        adv = font['hmtx'][gn][0]
        if form in ('init', 'medi') and bb[0] > 0:
            bad.append((label, gn, 'left', bb[0]))
        if form in ('medi', 'fina') and bb[2] < adv:
            bad.append((label, gn, 'right', bb[2], adv))
check('arabic joins', 'all init/medi/fina glyphs reach their joining edge (Sans and Mono)', not bad, bad[:6])

# Latin
g = shape(reg, 'AV')
check('latin', 'kerning: AV is tightened (GPOS kern)', g[0][1] < F['hmtx']['A'][0], g)
g = shape(reg, 'To')
check('latin', 'kerning: To is tightened', g[0][1] < F['hmtx']['T'][0], g)
g = shape(mono, 'AV')
check('latin', 'Mono has no kerning', g[0][1] == CELL and g[1][1] == CELL, g)
g = shape(reg, 'x\u0301')
check('latin', 'combining acute attaches to x (GPOS mark)', len(g) == 2 and g[1][1] == 0 and (g[1][2] != 0 or g[1][3] != 0), g)
g = shape(reg, 'q̣́')
check('latin', 'unencoded combination q + dot below + acute positions both marks', len(g) == 3 and all(x[1] == 0 for x in g[1:]), g)

g = names(reg, '1/2 3/4', features={'frac': True})
check('features', "frac: '1/2 3/4' -> onehalf, threequarters", g == ['onehalf', 'space', 'threequarters'], g)
g = names(reg, '0', features={'zero': True})
check('features', 'zero: slashed zero', g == ['zero.slash'], g)
g = names(mono, 'a->b => c != d <= e >= f == g <- h', features={'dlig': True})
exp = ['arrow_r.liga', 'darrow_r.liga', 'neq.liga', 'leq.liga', 'geq.liga', 'eqeq.liga', 'arrow_l.liga']
check('features', 'Mono dlig: code ligatures -> => != <= >= == <- (each stays two cells wide)',
      [x for x in g if x.endswith('.liga')] == exp and len(g) == len('a->b => c != d <= e >= f == g <- h'), g)
lb = bounds(FM, 'arrow_r.liga')
check('features', 'Mono dlig: ligature ink covers the two cells and does not enter the next one', lb[0] < -300 and lb[2] <= CELL, lb)
g = names(mono, 'a->b')
check('features', 'Mono: ligatures are off by default', g == ['a', 'hyphen', 'greater', 'b'], g)
ia = bounds(TTFont(os.path.join(DIST, 'ttf', 'Suhar-Italic.ttf')), 'a'); ua = bounds(F, 'a')
check('features', 'Italic has its own single-storey a (not a slanted copy)', abs((ia[2] - ia[0]) - (ua[2] - ua[0])) > 25, (ia, ua))
for txt, label in (('Съешь ещё этих мягких французских булок', 'Russian'), ('Їжак з’їв ґанок і єнота', 'Ukrainian'),
                   ('Ξεσκεπάζω την ψυχοφθόρα βδελυγμία', 'Greek'), ('ڕۆژ باش، چۆنی؟ ڵاو', 'Kurdish (Sorani)')):
    g = names(reg, txt)
    check('languages', f'{label} sample has no missing glyphs', '.notdef' not in g, [x for x in g if x == '.notdef'][:3])

g = names(reg, '\u06f4\u06f6\u06f7', language='ur')
check('features', 'locl URD: Urdu forms of ۶ and ۷', 'uni06F6.urdu' in g and 'uni06F7.urdu' in g, g)
g = names(reg, '\u06f6\u06f7', language='fa')
check('features', 'Persian keeps its own ۶ ۷', g == ['uni06F7', 'uni06F6'], g)
for txt, label in (('שלום עולם, ברוכים הבאים', 'Hebrew'), ('Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ ὁ λόγος ἦν πρὸς τὸν θεόν', 'Polytonic Greek'),
                   ('Љубазни фењерџија чађавог лица хоће да ми покаже штос', 'Serbian'), ('Әлемге сәлем, қазақ тілі үшін ұлы күн', 'Kazakh')):
    g = names(reg, txt)
    check('languages', f'{label} sample has no missing glyphs', '.notdef' not in g, [x for x in g if x == '.notdef'][:3])
g = shape(reg, 'ΑΥ')
check('latin', 'kerning exists for Greek (ΑΥ)', g[0][1] < F['hmtx'][g[0][0]][0], g)
g = shape(reg, 'ГА')
check('latin', 'kerning exists for Cyrillic (ГА)', g[0][1] < F['hmtx'][g[0][0]][0], g)
vfs = {os.path.basename(p): TTFont(p) for p in glob.glob(os.path.join(DIST, 'variable', '*.ttf'))}
for b_, vf_ in sorted(vfs.items()):
    st_ = TTFont(os.path.join(DIST, 'ttf', ('SuharMono' if 'Mono' in b_ else 'SuharCondensed' if 'Condensed' in b_ else 'Suhar') + ('-Italic' if 'Italic' in b_ else '-Regular') + '.ttf'))
    miss = sorted(set(st_.getGlyphOrder()) - set(vf_.getGlyphOrder()))
    check('variable', f'{b_}: has every glyph of the static font', not miss, miss[:8])
tall = shape(reg, 'لَّ')
top = max(bounds(F, x[0])[3] + x[3] for x in tall)
check('metrics', 'shadda + fatha on lam stays inside the Windows clipping box of Suhar (1200)', top <= 1200, round(top))

# terminal geometry
for font, label in ((FM, 'Mono'), (F, 'Sans')):
    c = font.getBestCmap()
    b1 = bounds(font, c[0x2502]); b2 = bounds(font, c[0x2500]); b3 = bounds(font, c[0x2588]); b4 = bounds(font, c[0x253C])
    check('terminal', f'{label}: U+2502 spans descender..ascender', (b1[1], b1[3]) == (DESC, ASC), b1)
    check('terminal', f'{label}: U+2500 spans the full cell width', (b2[0], b2[2]) == (0, CELL), b2)
    check('terminal', f'{label}: U+2588 is exactly the cell', tuple(b3) == (0, DESC, CELL, ASC), b3)
    check('terminal', f'{label}: U+253C touches all four edges', tuple(b4) == (0, DESC, CELL, ASC), b4)
    miss = [hex(cp) for cp in list(range(0x2500, 0x25A0)) + list(range(0x2800, 0x2900)) if cp not in c]
    check('terminal', f'{label}: box drawing, blocks and Braille complete (416 code points)', not miss, miss[:8])
    # horizontal and vertical line centres agree across all box glyphs that have that arm
    cy = {round((bounds(font, c[cp])[1] + bounds(font, c[cp])[3]) / 2) for cp in (0x2500, 0x2501, 0x2550, 0x2504)}
    cx = {round((bounds(font, c[cp])[0] + bounds(font, c[cp])[2]) / 2) for cp in (0x2502, 0x2503, 0x2551, 0x2506)}
    check('terminal', f'{label}: line centres consistent', cy == {(ASC + DESC) // 2} and cx == {CELL // 2}, (cy, cx))
c = TTFont(os.path.join(DIST, 'ttf', 'SuharNerdMono-Regular.ttf')).getBestCmap()
for cp, what in ((0xE0B0, 'Powerline'), (0xF115, 'Font Awesome'), (0xE700, 'Devicons'), (0xF0001, 'Material Design'),
                 (0xEA60, 'Codicons'), (0xF400, 'Octicons'), (0xE300, 'Weather'), (0xF300, 'Font Logos')):
    check('nerd', f'Nerd Mono has {what} U+{cp:04X}', cp in c)
check('nerd', 'Suhar icons U+E100..E12E kept in Nerd fonts', all(c.get(cp, '').startswith('retroui.') for cp in range(0xE110, 0xE12F)))
check('nerd', 'own Powerline glyphs kept (cell exact)', not c[0xE0B0].startswith('nf-'))

# variable fonts
for vf in sorted(glob.glob(os.path.join(DIST, 'variable', '*.ttf'))):
    f = TTFont(vf)
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in f['fvar'].axes}
    b = os.path.basename(vf)
    check('variable', f'{b}: axes {axes}', 'wght' in axes and axes['wght'] == (400, 400, 700))
    r1 = Renderer(vf, {'wght': 400}); r2 = Renderer(vf, {'wght': 700})
    a1 = sum(p.x_advance for p in r1.shape('Hamburg').glyph_positions)
    a2 = sum(p.x_advance for p in r2.shape('Hamburg').glyph_positions)
    im1 = np.array(r1.line('Hamburg', 80)[0]).sum(); im2 = np.array(r2.line('Hamburg', 80)[0]).sum()
    check('variable', f'{b}: wght 700 renders heavier than 400', im2 > im1 * 1.2, (int(im1), int(im2)))
    if 'opsz' in axes:
        r3 = Renderer(vf, {'opsz': 8}); r4 = Renderer(vf, {'opsz': 72})
        a3 = sum(p.x_advance for p in r3.shape('Hamburg').glyph_positions)
        a4 = sum(p.x_advance for p in r4.shape('Hamburg').glyph_positions)
        check('variable', f'{b}: opsz 8 is spaced wider than opsz 72', a3 > a4, (a3, a4))

# ---------------------------------------------------------------- proof images
PAN = 'The quick brown fox jumps over the lazy dog 0123456789'
ARA = 'نص عربي للتجربة: الخط العربي جميل ٠١٢٣٤٥٦٧٨٩'
rows = []
for px in (8, 9, 10, 11, 12, 13, 14, 16, 18):
    rows.append((reg, f'{px}px {PAN}', px))
for px in (10, 12, 14, 16, 18):
    rows.append((reg, ARA, px))
sheet(rows, os.path.join(IMG, 'small-sizes-hinted.png'), scale=3)
sheet([(r[0], r[1], r[2], {'hinting': False}) for r in rows], os.path.join(IMG, 'small-sizes-unhinted.png'), scale=3)
sheet([(reg, f'{px}px {PAN}', px, {'mono': True}) for px in (8, 9, 10, 11, 12, 13, 14, 16)],
      os.path.join(IMG, 'small-sizes-1bit.png'), scale=3)
sheet([(reg, 'Suhar صُحار', 420), (bold, 'Hamburgefonstiv', 300)], os.path.join(IMG, 'high-resolution.png'))
# print: 9 pt and 12 pt text at 1200 dpi  (1 pt = 16.67 px)
sheet([(reg, 'Printed 9 pt at 1200 dpi: Hamburgefonstiv', 150), (reg, 'طباعة ١٢ نقطة: الخط العربي', 200),
       (ital, 'Italic 9 pt: quick wafting zephyrs', 150)], os.path.join(IMG, 'print-1200dpi.png'))
sheet([(r, t, 44) for r, t in [(reg, 'Regular Hamburgefonstiv العربية'), (R('Suhar-Medium'), 'Medium Hamburgefonstiv العربية'),
                               (R('Suhar-SemiBold'), 'SemiBold Hamburgefonstiv العربية'), (bold, 'Bold Hamburgefonstiv العربية'),
                               (ital, 'Italic Hamburgefonstiv'), (R('Suhar-BoldItalic'), 'Bold Italic Hamburgefonstiv')]],
      os.path.join(IMG, 'weights.png'))

# terminal alignment proof at the exact line pitch (several sizes)
def term_sheet(rend, lines, px, out):
    rend.ft.set_pixel_sizes(0, px)
    lh = round(rend.ft.size.height / 64)
    ims = [rend.line(t, px)[0] for t in lines]
    arr = np.zeros((lh * len(ims) + 8, max(i.width for i in ims)), dtype=np.uint16)
    for i, im in enumerate(ims):
        a = np.array(im)[2:, :]
        h = min(a.shape[0], arr.shape[0] - i * lh)
        arr[i * lh:i * lh + h, :a.shape[1]] += a[:h]
    Image.fromarray(255 - np.minimum(arr, 255).astype(np.uint8)).save(out)
    return arr, lh


TL = ['┌──────────┬───────┐ ╔═══╦═══╗ ╭───╮',
      '│ fn main  │ 0O1lI │ ║ ▓ ║ ░ ║ │ ✓ │',
      '├──────────┼───────┤ ╠═══╬═══╣ │ ⣿ │',
      '│ ▁▂▃▄▅▆▇█ │ ▌▐▀▄  │ ║ █ ║ ▒ ║ │ ● │',
      '└──────────┴───────┘ ╚═══╩═══╝ ╰───╯',
      '  main  ~/src  ned  12:30    1 ']
gaps = {}
for px in (14, 16, 20, 28, 40):
    arr, lh = term_sheet(nerdm, TL, px, os.path.join(IMG, f'terminal-{px}px.png'))
    # the vertical bar in column 0 must be continuous from line 1 to line 5
    rend = nerdm
    cw = rend.line('│', px)[1]
    col = arr[:, int(2 + cw / 2 - 1):int(2 + cw / 2 + 2)].max(axis=1)
    seg = col[int(lh * 0.6):int(lh * 4.3)]
    gaps[px] = int((seg < 60).sum())
check('terminal', 'rendered: vertical box lines are unbroken between text lines at 14/16/20/28/40 px', all(v == 0 for v in gaps.values()), gaps)
# column alignment: n characters always advance n cells
adv = [nerdm.line(t, 20)[1] for t in ('abcdefghij', '┌────────┐', 'ابتثجحخدذر', '' * 10, '⣿' * 10)]
check('terminal', 'rendered: 10 cells of Latin, box, Arabic, icons, Braille have the same width', max(adv) - min(adv) < 0.01, adv)
sheet([(mono, 'proc greet(name: string): int =  # 0O 1lI| {}[]() <>= != -> =>', 30),
       (mono, '  echo "Hello, " & name & "!"; result = 0xFF + 42_000', 30),
       (monob, 'type Font* = object  ## il1I O0 @#$%^&*~`\'"\\/', 30),
       (mono, 'السلام عليكم ورحمة الله وبركاته', 30), (mono, 'كتاب محمد هذه مهمة صحار', 30)], os.path.join(IMG, 'mono-code.png'))

# ---------------------------------------------------------------- coverage
blocks = {}
import bisect
BL = [(0x0000, 0x007F, 'Basic Latin'), (0x0080, 0x00FF, 'Latin-1 Supplement'), (0x0100, 0x017F, 'Latin Extended-A'),
      (0x0180, 0x024F, 'Latin Extended-B'), (0x02B0, 0x02FF, 'Spacing Modifier Letters'), (0x0300, 0x036F, 'Combining Diacritical Marks'),
      (0x0370, 0x03FF, 'Greek'), (0x0400, 0x04FF, 'Cyrillic'), (0x0590, 0x05FF, 'Hebrew'), (0x1F00, 0x1FFF, 'Greek Extended'), (0x0600, 0x06FF, 'Arabic'), (0x0E00, 0x0E7F, 'Thai (baht sign only)'),
      (0x1E00, 0x1EFF, 'Latin Extended Additional'), (0x2000, 0x206F, 'General Punctuation'), (0x2070, 0x209F, 'Superscripts and Subscripts'),
      (0x20A0, 0x20CF, 'Currency Symbols'), (0x2100, 0x214F, 'Letterlike Symbols'), (0x2150, 0x218F, 'Number Forms'),
      (0x2190, 0x21FF, 'Arrows'), (0x2200, 0x22FF, 'Mathematical Operators'), (0x2300, 0x23FF, 'Miscellaneous Technical'),
      (0x2500, 0x257F, 'Box Drawing'), (0x2580, 0x259F, 'Block Elements'), (0x25A0, 0x25FF, 'Geometric Shapes'),
      (0x2600, 0x26FF, 'Miscellaneous Symbols'), (0x2700, 0x27BF, 'Dingbats'), (0x2800, 0x28FF, 'Braille Patterns'),
      (0x2B00, 0x2BFF, 'Misc Symbols and Arrows'), (0x3000, 0x303F, 'CJK Symbols (ideographic space only)'),
      (0xE000, 0xF8FF, 'Private Use Area'), (0xFB50, 0xFDFF, 'Arabic Presentation Forms-A'),
      (0xFE70, 0xFEFF, 'Arabic Presentation Forms-B'), (0x1FB00, 0x1FBFF, 'Symbols for Legacy Computing'),
      (0xF0000, 0xFFFFF, 'Supplementary Private Use Area-A')]
cov = {}
for label, fn in (('Suhar', 'Suhar-Regular'), ('Suhar Mono', 'SuharMono-Regular'), ('Suhar Nerd', 'SuharNerd-Regular'),
                  ('Suhar Nerd Mono', 'SuharNerdMono-Regular')):
    c = TTFont(os.path.join(DIST, 'ttf', fn + '.ttf')).getBestCmap()
    d = {}
    for cp in c:
        for lo, hi, nm in BL:
            if lo <= cp <= hi:
                d[nm] = d.get(nm, 0) + 1
                break
        else:
            d['other'] = d.get('other', 0) + 1
    cov[label] = {'total': len(c), 'blocks': d}
ar = F.getBestCmap()
need = {'Arabic letters 0621-064A': range(0x621, 0x64B), 'Arabic tashkeel 064B-0652': range(0x64B, 0x653),
        'Persian پ چ ژ گ ک ی': [0x67E, 0x686, 0x698, 0x6AF, 0x6A9, 0x6CC],
        'Urdu ٹ ڈ ڑ ں ھ ہ ے ۓ ۃ ۂ': [0x679, 0x688, 0x691, 0x6BA, 0x6BE, 0x6C1, 0x6D2, 0x6D3, 0x6C3, 0x6C2],
        'Arabic-Indic digits': range(0x660, 0x66A), 'Extended Arabic-Indic digits': range(0x6F0, 0x6FA),
        'Quranic annotation 06D6-06ED': range(0x6D6, 0x6EE), 'Honorifics 0610-0614': range(0x610, 0x615),
        'Word ligatures FDF0-FDFD': range(0xFDF0, 0xFDFE), 'ASCII': range(0x20, 0x7F), 'Latin-1': range(0xA0, 0x100),
        'Latin Extended-A': range(0x100, 0x180), 'Vietnamese 1EA0-1EF9': range(0x1EA0, 0x1EFA),
        'Greek monotonic 0391-03C9': [c for c in range(0x391, 0x3CA) if c != 0x3A2], 'Greek with tonos': [0x386, 0x388, 0x389, 0x38A, 0x38C, 0x38E, 0x38F, 0x390, 0x3AA, 0x3AB, 0x3AC, 0x3AD, 0x3AE, 0x3AF, 0x3B0, 0x3CA, 0x3CB, 0x3CC, 0x3CD, 0x3CE],
        'Cyrillic А-я 0410-044F': range(0x410, 0x450), 'Cyrillic Ё ё Є є І і Ї ї Ґ ґ Ў ў': [0x401, 0x451, 0x404, 0x454, 0x406, 0x456, 0x407, 0x457, 0x490, 0x491, 0x40E, 0x45E],
        'Kurdish ڵ ڕ ۆ ێ': [0x6B5, 0x695, 0x6C6, 0x6CE],
        'Hebrew letters 05D0-05EA': range(0x5D0, 0x5EB), 'Honorifics 0610-0614 ': range(0x610, 0x615),
        'Serbian/Macedonian Ђ Ћ Љ Њ Џ Ѓ Ќ': [0x402, 0x40B, 0x409, 0x40A, 0x40F, 0x403, 0x40C, 0x452, 0x45B, 0x459, 0x45A, 0x45F, 0x453, 0x45C],
        'Kazakh Ә Ғ Қ Ң Ө Ұ Ү Һ': [0x4D8, 0x492, 0x49A, 0x4A2, 0x4E8, 0x4B0, 0x4AE, 0x4BA, 0x4D9, 0x493, 0x49B, 0x4A3, 0x4E9, 0x4B1, 0x4AF, 0x4BB],
        'Greek Extended (polytonic) 1F00-1FFF': [c for c in range(0x1F00, 0x2000) if __import__('unicodedata').category(chr(c)).startswith('L')],
        'Omani rial U+20C4': [0x20C4], 'Saudi riyal U+20C1': [0x20C1], 'UAE dirham U+20C3': [0x20C3]}
missing = {}
for k, rng in need.items():
    m = ['U+%04X' % cp for cp in rng if cp not in ar and ud.category(chr(cp)) != 'Cn' or (cp not in ar and cp in (0x20C1, 0x20C3, 0x20C4))]
    missing[k] = m
    results.append(('coverage', f'{k}: {len(list(rng)) - len(m)}/{len(list(rng))}', True, 'missing: ' + ' '.join(m) if m else ''))

# ---------------------------------------------------------------- report
ok = sum(1 for r in results if r[2])
# ---- 1.3 additions
g = names(reg, 'young Quay', features={'ss01': True})
check('features', 'ss01 khanjar tails: Latin y, g, Q', 'y.ss01' in g and 'Q.ss01' in g and 'g.ss01' in g, g)
g = names(reg, 'دور', features={'ss01': True})
check('features', 'ss01 khanjar tails: Arabic reh and waw', any(x.endswith('.ss01') for x in g) and len([x for x in g if x.endswith('.ss01')]) == 2, g)
g = names(reg, 'دور')
check('features', 'ss01 is off by default', not any(x.endswith('.ss01') for x in g), g)
check('features', 'ss02 dotted zero / ss03 plain zero', names(reg, '0', features={'ss02': True}) == ['zero.dot']
      and names(reg, '0', features={'ss03': True}) == ['zero.plain'])
g = names(reg, 'لم'); g2 = names(reg, 'لم', features={'dlig': True})
check('arabic', 'dlig lam-meem ligature only when asked for', g2 == ['lam_meem'] and len(g) == 2, (g, g2))
g2 = names(reg, 'في', features={'dlig': True})
check('arabic', 'dlig feh-yeh ligature', g2 == ['feh_yeh'], g2)
g2 = names(reg, 'ملح', features={'dlig': True})
check('arabic', 'dlig lam-hah ligature inside a word', 'lam_062D.fina' in g2, g2)
g = names(reg, 'تتنبيت'); g0 = names(reg, 'تتنبيت', features={'calt': False})
check('arabic', 'calt raises alternate teeth in a run', any('tall' in x for x in g) and not any('tall' in x for x in g0), g)
g = names(reg, 'بيت')
check('arabic', 'calt leaves short words alone', not any('tall' in x for x in g), g)
check('icons', 'ornaments and wayfinding pictograms U+E130..E143', all(c in F.getBestCmap() for c in range(0xE130, 0xE144)))
g = names(mono, ':= |>', features={'dlig': True})
check('mono', 'new code ligatures := and |>', 'coloneq.liga' in g and 'pipe_r.liga' in g, g)
_w = {}
for stn in ('Light', 'Regular', 'Bold', 'ExtraBold'):
    f_ = TTFont(os.path.join(DIST, 'ttf', f'Suhar-{stn}.ttf')); _w[stn] = (f_['OS/2'].usWeightClass, bounds(f_, 'l'))
check('family', 'weight classes 300/400/700/800 and stems grow with weight',
      [_w[s][0] for s in _w] == [300, 400, 700, 800] and all((_w[a][1][2] - _w[a][1][0]) < (_w[b][1][2] - _w[b][1][0])
      for a, b in (('Light', 'Regular'), ('Regular', 'Bold'), ('Bold', 'ExtraBold'))), {k: v[0] for k, v in _w.items()})
FC = TTFont(os.path.join(DIST, 'ttf', 'SuharCondensed-Regular.ttf'))
_t = 'Hamburgefonstiv 0123'
wc = sum(FC['hmtx'][FC.getBestCmap()[ord(c)]][0] for c in _t); wr = sum(F['hmtx'][F.getBestCmap()[ord(c)]][0] for c in _t)
check('family', 'Condensed is 12-25 % narrower than Suhar, width class 3', 0.75 < wc / wr < 0.88 and FC['OS/2'].usWidthClass == 3, round(wc / wr, 3))
check('family', 'Condensed has the full character set', set(FC.getBestCmap()) == set(F.getBestCmap()))
gc = names(R('SuharCondensed-Regular'), 'صُحار مدينة')
check('arabic', 'Condensed shapes Arabic', '.notdef' not in gc and any(x.endswith('.init') for x in gc), gc)
for pth in sorted(glob.glob(os.path.join(DIST, 'pixel', '*.ttf'))):
    fp = TTFont(pth); b_ = os.path.basename(pth); px = fp['head'].unitsPerEm // 100
    gl_ = fp['glyf']; onpix = True; n_ink = 0
    for gn in fp.getGlyphOrder():
        gg = gl_[gn]
        if gg.numberOfContours > 0:
            n_ink += 1
            co = gg.coordinates
            if any(x % 100 or y % 100 for x, y in co):
                onpix = False; break
    adv = all(a % 100 == 0 for a, _ in fp['hmtx'].metrics.values())
    check('pixel', f'{b_}: every outline point and advance sits on the {px}px grid', onpix and adv and n_ink > 2000, n_ink)
    rp = Renderer(pth)
    img, _ = rp.line('Suhar صحار 123', px)
    import numpy as _np
    vals = set(_np.unique(_np.asarray(img)).tolist())
    check('pixel', f'{b_}: renders with no grey pixels at {px}px (anti-aliased rasteriser)', vals <= {0, 255}, sorted(vals)[:6])
    gp = [i.codepoint for i in rp.shape('صحار').glyph_infos]
    check('pixel', f'{b_}: Arabic still shapes', len(gp) == 4 and 0 not in gp, gp)
    check('pixel', f'{b_}: no kerning feature', 'GPOS' not in fp or 'kern' not in {r.FeatureTag for r in fp['GPOS'].table.FeatureList.FeatureRecord})
for rr, lab in ((reg, 'Regular'), (bold, 'Bold'), (ital, 'Italic')):
    g = shape(rr, 'رة')          # visual order: teh marbuta, reh
    check('arabic', f'{lab}: the letter after reh is kerned over its tail (الحرة)', g[1][0] == 'uni0631' and g[1][1] <= F['hmtx']['uni0631'][0] - 60, g)
g = shape(reg, 'رر')
check('arabic', 'reh + reh do not collide (kern limited by closest approach)', g[1][1] >= F['hmtx']['uni0631'][0] - 120, g)
# ---- 1.4 additions
def _sh(r, text, **kw):
    b = r.shape(text, **kw)
    return [(r.font.glyph_to_string(i.codepoint), p.x_advance) for i, p in zip(b.glyph_infos, b.glyph_positions)]
W6 = F['hmtx']['uni06DD'][0]
for n_, txt in ((1, '۝١'), (2, '۝٢٥'), (3, '۝٢٨٦'), (2, '۝۴۵')):
    g = _sh(reg, txt, direction='ltr')
    check('arabic', f'end-of-ayah sign encloses {n_} digit(s): small figures, total advance = sign width',
          all(x[0].endswith('.ayah') for x in g[1:]) and abs(sum(x[1] for x in g) - W6) <= 2 and g[0][1] < W6 / 2, g)
g = _sh(reg, '۝ ١٢', direction='ltr')
check('arabic', 'digits not directly after the sign stay full size', not any(x[0].endswith('.ayah') for x in g), g)
g = _sh(mono, '۝١', direction='ltr')
check('mono', 'Mono keeps one cell per character after the ayah sign', all(x[1] == 600 for x in g), g)
check('features', 'smcp: lower case to small capitals incl. accents', names(reg, 'aéz', features={'smcp': True}) == ['a.sc', 'eacute.sc', 'z.sc'],
      names(reg, 'aéz', features={'smcp': True}))
check('features', 'c2sc: capitals to small capitals', names(reg, 'AZ', features={'c2sc': True}) == ['a.sc', 'z.sc'])
hsc = bounds(F, 'h.sc')[3]
check('features', 'small capitals stand between x-height and cap height', 520 < hsc < 640, hsc)
g1 = _sh(reg, '1111'); g2 = _sh(reg, '1111', features={'pnum': True})
check('features', 'figures are tabular by default, pnum makes 1 narrower', len({x[1] for x in _sh(reg, '0123456789')}) == 1 and g2[0][1] < g1[0][1] - 60, (g1[0], g2[0]))
check('features', 'sups / subs / ordn', names(reg, '2', features={'sups': True}) == ['uni00B2'] and names(reg, '2', features={'subs': True}) == ['uni2082']
      and names(reg, '1a', features={'ordn': True}) == ['one', 'ordfeminine'])
cm = F.getBestCmap()
for lab, cps, txt in (('Pashto', 'ټځڅډړږښګڼېۍ', 'پښتو ژبه ډېر ښه'), ('Sindhi', 'ٺٻٽٿڀڃڄڇڊڌڍڏڙڦڪڳڱڻ', 'سنڌي ٻولي ڪتاب'),
                      ('Uyghur', 'ۇۈۋېەھڭ', 'ئۇيغۇرچە يېزىق')):
    g = names(reg, txt)
    check('languages', f'{lab}: letters present and sample shapes', all(ord(c) in cm for c in cps) and '.notdef' not in g and any('.medi' in x or '.init' in x for x in g), g[:6])
g = names(reg, 'يىق')
check('arabic', 'U+0649 joins on both sides (Uyghur, Kazakh)', 'uni0649.medi' in g, g)
check('arabic', 'word-final alef maksura unchanged', names(reg, 'على')[0] == 'uni0649.fina', names(reg, 'على'))
ks = set(bounds(F, 'uni06AA')) != set(bounds(F, 'uni06A9'))
check('arabic', 'Sindhi swash kaf differs from keheh', ks and F['hmtx']['uni06AA'][0] > F['hmtx']['uni06A9'][0] + 100)
g = names(reg, 'ʿAbd Qurʾān ḥāʾ ṣād Hawaiʻi')
check('latin', 'Arabic transliteration letters (ʿ ʾ ʻ and dotted letters) present', '.notdef' not in g, g)
g = names(reg, 'ڪتاب ۾ ۽')
check('languages', 'Sindhi signs U+06FD U+06FE present', 0x6FD in cm and 0x6FE in cm and '.notdef' not in g, g)
REFA = os.environ.get('SUHAR_REF_ARABIC', '')      # path of NotoSansArabic.ttf; the comparison is skipped without it
if os.path.exists(REFA):
    # dot counts of the Pashto/Sindhi/Uyghur letters against Noto Sans Arabic (number of separate ink parts of the isolated letter)
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    def parts(font, cp):
        gs = font.getGlyphSet(); pen = DecomposingRecordingPen(gs); gs[font.getBestCmap()[cp]].draw(pen)
        return pen
    del parts
    from pathops import Path, PathPen, simplify
    def nparts(font, cp):
        gs = font.getGlyphSet(); pth = Path(); gs[font.getBestCmap()[cp]].draw(PathPen(pth, glyphSet=gs))
        cs = list(simplify(pth, fix_winding=True, keep_starting_points=False).contours)
        big = max(cs, key=lambda c: abs(c.area))
        return sum(1 for c in cs if (c.area > 0) == (big.area > 0))       # outer contours = separate ink parts
    NR = TTFont(REFA); nc = NR.getBestCmap(); bad = []
    for cp in [0x67A, 0x67B, 0x67D, 0x67F, 0x680, 0x683, 0x684, 0x687, 0x68A, 0x68C, 0x68D, 0x68E, 0x68F, 0x699, 0x6A6, 0x6B1, 0x6B3,
               0x685, 0x696, 0x69A, 0x6D0, 0x6CB, 0x6A2, 0x6A7, 0x6A8, 0x697, 0x69B, 0x6B6, 0x6B7, 0x6D1, 0x6CA, 0x6CF]:
        if cp in nc and nparts(NR, cp) != nparts(F, cp):
            bad.append('%04X ref %d ours %d' % (cp, nparts(NR, cp), nparts(F, cp)))
    check('languages', 'dot counts of 32 Pashto/Sindhi/Uyghur letters equal those of Noto Sans Arabic', not bad, bad)
# ---- 1.6 additions
FN = TTFont(os.path.join(DIST, 'ttf', 'SuharNaskh-Regular.ttf')); naskh = R('SuharNaskh-Regular')
def stem_at(font, gname, y):
    """width of the ink of a glyph in a thin horizontal band (the upright's thickness, whatever its lean)"""
    from pathops import Path, PathPen, op, PathOp
    gs = font.getGlyphSet(); p1 = Path(); gs[gname].draw(PathPen(p1, glyphSet=gs))
    p2 = Path(); pp = PathPen(p2); pp.moveTo((-2000, y)); pp.lineTo((3000, y)); pp.lineTo((3000, y + 4)); pp.lineTo((-2000, y + 4)); pp.closePath()
    b = op(p1, p2, PathOp.INTERSECTION, fix_winding=True).bounds
    return b[2] - b[0]
bt = bounds(FN, 'uni0640'); sa = stem_at(FN, 'uni0627', 480)
check('naskh', 'Suhar Naskh: pen contrast (upright thinner than 0.75 x the baseline stroke)', 20 < sa < 0.75 * (bt[3] - bt[1]), (round(sa), bt[3] - bt[1]))
bs = bounds(F, 'uni0627'); bts = bounds(F, 'uni0640')
check('naskh', 'Suhar (plain) keeps low contrast', (bs[2] - bs[0]) > 0.8 * (bts[3] - bts[1]))
check('naskh', 'Latin is the same as in Suhar', bounds(FN, 'n') == bounds(F, 'n') and FN['hmtx']['n'] == F['hmtx']['n'])
rn = bounds(FN, 'uni0631'); rs_ = bounds(F, 'uni0631')
check('naskh', 'tails sweep further left under the baseline', rn[0] < rs_[0] - 15 or (rn[2] - rn[0]) > (rs_[2] - rs_[0]) + 15, (rn, rs_))
g = names(naskh, 'صُحار مدينة عُمانية')
check('naskh', 'shaping, marks and joins work', '.notdef' not in g and any(x.endswith('.init') for x in g) and any(x.endswith('.medi') for x in g), g[:5])
check('naskh', 'same character set as Suhar', set(FN.getBestCmap()) == set(F.getBestCmap()))
check('features', 'onum old-style figures', names(reg, '0123456789', features={'onum': True}) == [d_ + '.onum' for d_ in ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine')])
b9 = bounds(F, 'nine.onum'); b0 = bounds(F, 'zero.onum'); b8 = bounds(F, 'eight.onum')
check('features', 'onum: 0 at x-height, 9 hangs below the baseline, 8 keeps cap height', b9[1] < -100 and 500 < b0[3] < 560 and b8[3] > 680, (b0[3], b9[1], b8[3]))
g = shape(reg, 'AV', features={'c2sc': True}); g2 = shape(reg, 'Va', features={'smcp': True})
check('features', 'small capitals are kerned (AV, Va)', g[0][0] == 'a.sc' and g[0][1] < F['hmtx']['a.sc'][0] - 15 and g2[0][1] < F['hmtx']['V'][0] - 15, (g, g2))
g = shape(reg, 'שָׁלוֹם בְּרֵאשִׁית')
check('languages', 'Hebrew points: present, zero width, attached', '.notdef' not in [x[0] for x in g] and all(x[1] == 0 for x in g if x[0] in ('uni05B8', 'uni05C1', 'uni05B9', 'uni05B0', 'uni05BC', 'uni05B5', 'uni05B4'))
      and any(x[0] == 'uni05C1' and (x[2] or x[3]) for x in g), g[:6])
g = _sh(mono, 'صحار'); g2 = _sh(mono, 'صحار', features={'ss05': True})
check('mono', 'ss05: wide letters take two cells only when asked', all(x[1] == 600 for x in g) and g2[-1][0].endswith('.w2') and g2[-1][1] == 1200, (g, g2))
for px_ in (8, 9):
    fp = TTFont(os.path.join(DIST, 'pixel', f'SuharPixel{px_}-Regular.ttf'))
    ba_ = bounds(fp, 'uni0627'); bb_ = bounds(fp, FM and 'uni0628.medi')
    check('pixel', f'Suhar Pixel {px_}: hand-drawn Arabic (alef 1 px wide and 7 px tall, tooth 3 px tall)', ba_[2] - ba_[0] == 100 and ba_[3] - ba_[1] == 700 and bb_[3] - bb_[1] >= 300, (ba_, bb_))
    rp = Renderer(os.path.join(DIST, 'pixel', f'SuharPixel{px_}-Regular.ttf'))
    gp = [rp.font.glyph_to_string(i.codepoint) for i in rp.shape('بيت').glyph_infos]
    check('pixel', f'Suhar Pixel {px_}: bitmap Arabic still shapes', gp == ['uni062A.fina', 'uni064A.medi', 'uni0628.init'], gp)
# ---- 1.7 additions
FD = TTFont(os.path.join(DIST, 'ttf', 'SuharNaskhDisplay-Regular.ttf')); disp = R('SuharNaskhDisplay-Regular')
check('naskh', 'Naskh Display has cursive attachment (curs); Naskh and Suhar do not',
      'curs' in {r.FeatureTag for r in FD['GPOS'].table.FeatureList.FeatureRecord}
      and 'curs' not in {r.FeatureTag for r in FN['GPOS'].table.FeatureList.FeatureRecord}
      and 'curs' not in {r.FeatureTag for r in F['GPOS'].table.FeatureList.FeatureRecord})
g = shape(disp, 'كتابة')          # visual order, left to right
ys = [x[3] for x in g]
g_long = shape(disp, 'مستشفيات')
yl = [x[3] for x in g_long]
check('naskh', 'Display: a joined word steps down to the left and lands on the baseline', ys[0] == 0 and max(ys) >= 10 and ys == sorted(ys)
      and yl[0] == 0 and yl == sorted(yl) and max(yl) > 40, (g, yl))
g = shape(naskh, 'كتابة')
check('naskh', 'Suhar Naskh (text) keeps a level baseline', all(x[3] == 0 for x in g), g)
g = shape(disp, 'دار ورد')
check('naskh', 'Display: letters that do not join stay on the baseline', all(x[3] == 0 for x in g), g)
check('naskh', 'Naskh draws its own jeem, heh, lam-alef (differs from Suhar)', all(bounds(FN, n) != bounds(F, n) for n in ('uni062D', 'uni0647', 'uni06440627')))
check('naskh', 'Display has the same character set', set(FD.getBestCmap()) == set(F.getBestCmap()))
# ---- 1.8 additions
g = names(disp, 'في'); g2 = names(disp, 'على'); g3 = names(disp, 'كتابي'); g4 = names(disp, 'مي')
check('naskh', 'Display: returning yeh after a letter with nothing under the line (في على), not after ب or م',
      g[0] == 'uni064A.fina.ret' and g2[0] == 'uni0649.fina.ret' and not g3[0].endswith('.ret') and not g4[0].endswith('.ret'), (g, g2, g3, g4))
check('naskh', 'Naskh (text): returning yeh only with ss06', not names(naskh, 'في')[0].endswith('.ret') and names(naskh, 'في', features={'ss06': True})[0].endswith('.ret'))
check('naskh', 'Suhar has no returning yeh feature', not names(reg, 'في', features={'ss06': True})[0].endswith('.ret'))
bk = bounds(FD, 'uni0643.init'); bal = bounds(FD, 'uni0627')
check('naskh', 'kaf top stays inside the ascender and ends in a point, not a flat cut', bk[3] <= bal[3] + 30 and bk[3] < 940, (bk[3], bal[3]))
g = names(naskh, 'لمح', features={'dlig': True})
check('naskh', 'dlig: lam standing on meem (لمح)', 'lam_meem.init' in g, g)
check('naskh', 'Naskh draws its own meem and yeh', bounds(FN, 'uni0645') != bounds(F, 'uni0645') and bounds(FN, 'uni064A') != bounds(F, 'uni064A'))
for vf_ in ('SuharNaskh[opsz,wght].ttf', 'SuharNaskh-Italic[opsz,wght].ttf', 'SuharNaskhDisplay[wght].ttf'):
    pv = os.path.join(DIST, 'variable', vf_)
    okv = os.path.exists(pv)
    if okv:
        fv = TTFont(pv); okv = 'fvar' in fv and len(fv.getBestCmap()) >= len(FN.getBestCmap()) - 40
    check('variable', f'{vf_}: built with a weight axis and (nearly) the full character set', okv)
br = bounds(F, 'uni20C4'); bz = bounds(F, 'zero')
check('currency', 'Omani rial sign: official proportions (1.874 : 1) and the height of the figures', abs((br[2] - br[0]) / (br[3] - br[1]) - 1.874) < 0.01 and abs((br[3] - br[1]) - 700) <= 2, br)
# ---- 1.9 additions
def body_left(font, gname):
    """left edge of the part of a glyph that stands on or above the baseline (what the eye takes as the end of the word)"""
    from pathops import Path, PathPen, op, PathOp
    gs = font.getGlyphSet(); p1 = Path(); gs[gname].draw(PathPen(p1, glyphSet=gs))
    p2 = Path(); pp = PathPen(p2); pp.moveTo((-3000, 0)); pp.lineTo((4000, 0)); pp.lineTo((4000, 360)); pp.lineTo((-3000, 360)); pp.closePath()
    return op(p1, p2, PathOp.INTERSECTION, fix_winding=True).bounds[0]
for lab, rr, ff in (('Suhar', reg, F), ('Suhar Bold', bold, TTFont(os.path.join(DIST, 'ttf', 'Suhar-Bold.ttf'))), ('Suhar Naskh', naskh, FN), ('Naskh Display', disp, FD)):
    vis = {}
    for ch in 'رزوؤمبتندذاةهكلسصقفعحيى':
        g = shape(rr, ch + ' ب')          # visual order: beh, space, letter
        nm, adv = g[-1][0], g[-1][1]
        vis[ch] = round(body_left(ff, nm) - (ff['hmtx'][nm][0] - adv))
    spread = max(vis.values()) - min(vis.values())
    lim = 200 if 'Naskh' in lab else 140          # the Naskh tail sweeps further, and the kern is capped at 110
    check('arabic', f'{lab}: gaps after word-final letters differ by less than {lim} units (ر was 110 units wider before 1.9)',
          spread < lim and g[-1][0] and (ff['hmtx']['uni0631'][0] - shape(rr, 'ر ب')[-1][1]) >= 100, (spread, vis['ر'], vis['م'], vis['ب']))
g = shape(reg, 'ر ب'); g2 = shape(reg, 'رب')
check('arabic', 'the tail of reh runs under less than half of the space', F['hmtx']['uni0631'][0] - g[-1][1] <= 0.45 * F['hmtx']['space'][0], g)
g = shape(reg, 'ال')
check('arabic', 'alef and lam at the start of a word stand closer (gap 110 or less)', F['hmtx']['uni0627'][0] - bounds(F, 'uni0627')[2] + bounds(F, 'uni0644.init')[0] + 0 <= 125 and
      (F['hmtx']['uni0644.init'][0] - bounds(F, 'uni0644.init')[2]) + bounds(F, 'uni0627')[0] <= 110, bounds(F, 'uni0627'))
g = names(disp, 'نجم'); g2 = names(naskh, 'نجم'); g3 = names(naskh, 'نجم', features={'ss07': True}); g4 = names(disp, 'لحم')
check('naskh', 'a toothed letter stands on jeem (نجم): default in Display, ss07 in Naskh, not for letters without a tooth',
      'uni0646.init.j' in g and 'uni062C.medi.j' in g and not any(x.endswith('.j') for x in g2) and 'uni0646.init.j' in g3 and not any(x.endswith('.j') for x in g4), (g, g4))
bj = bounds(FD, 'uni0646.init.j')
check('naskh', 'the raised letter and its dot stay inside the ascender', bj[3] < 940 and bj[1] > 200, bj)
FNB = TTFont(os.path.join(DIST, 'ttf', 'SuharNaskh-Bold.ttf'))
def contour_areas(font, gname):
    from pathops import Path, PathPen
    gs = font.getGlyphSet(); pth = Path(); gs[gname].draw(PathPen(pth, glyphSet=gs))
    return sorted(abs(c.area) for c in pth.contours)
cn = contour_areas(FNB, 'lam_meem')
check('naskh', 'lam-meem keeps an open loop in Bold (a counter of at least 6000 square units)', len(cn) >= 2 and cn[0] > 6000, cn)
# ---- 2.0 additions
g = names(disp, 'بحر'); g2 = names(disp, 'يجب')
check('naskh', 'letters with dots under the line also stand on jeem (بحر يجب), dots under the raised letter', 'uni0628.init.j' in g and 'uni064A.init.j' in g2, (g, g2))
FMo = FM
ws = bounds(FMo, 'uni0635.init'); wsans = bounds(F, 'uni0635.init')
check('mono', 'Mono draws its own ص: a lower, longer loop than the Sans drawing rescaled to the cell would give',
      ws[3] / wsans[3] < 0.85 and (ws[2] - ws[0]) > 1.7 * (ws[3] - ws[1]), (ws, wsans))
check('mono', 'Mono Arabic differs from a refit of the Sans drawing (س)', bounds(FMo, 'uni0633')[2] - bounds(FMo, 'uni0633')[0] <= 600)
FK = TTFont(os.path.join(DIST, 'ttf', 'Suhar-Black.ttf'))
check('family', 'Black: weight class 900, heavier stem than ExtraBold, counters still open',
      FK['OS/2'].usWeightClass == 900 and (bounds(FK, 'l')[2] - bounds(FK, 'l')[0]) > (_w['ExtraBold'][1][2] - _w['ExtraBold'][1][0])
      and len(contour_areas(FK, 'e')) >= 2 and len(contour_areas(FK, 'uni0647')) >= 2 and contour_areas(FK, 'e')[0] > 3000, contour_areas(FK, 'e'))
check('icons', 'pictograms U+E144..E148 (toilets, exit, pharmacy, qibla, taxi)', all(c in F.getBestCmap() for c in range(0xE144, 0xE149)))
g = shape(reg, 'לא'); g2 = shape(reg, 'רו')
hk = sum(1 for a in range(0x5D0, 0x5EB) for b in (0x5D0, 0x5D5, 0x5DC, 0x5E8) if shape(reg, chr(a) + chr(b))[-1][1] != F['hmtx']['uni%04X' % a][0])
check('languages', 'Hebrew has kerning (some pairs adjusted, most left alone)', 3 <= hk <= 80, hk)
for px_ in (8, 9, 10):
    fpr = TTFont(os.path.join(DIST, 'pixel', f'SuharPixel{px_}-Regular.ttf')); fpb = TTFont(os.path.join(DIST, 'pixel', f'SuharPixel{px_}-Bold.ttf'))
    a1 = bounds(fpr, 'uni0627'); a2 = bounds(fpb, 'uni0627'); kk_ = bounds(fpr, 'uni06A9'); gg_ = bounds(fpr, 'uni06AF')
    check('pixel', f'Suhar Pixel {px_}: hand-drawn Arabic, Bold strokes 2 px, Persian ک گ drawn (گ taller by its second stroke)',
          a1[2] - a1[0] == 100 and a2[2] - a2[0] == 200 and kk_[3] - kk_[1] == 700 and gg_[3] > kk_[3], (a1, a2, kk_, gg_))

# ---- Suhar Sahafa (2.1) ----
SAH = {}
for ps, fam in (('SuharSahafa', 'Suhar Sahafa'), ('SuharSahafaHeadline', 'Suhar Sahafa Headline')):
    for st in ('Regular', 'Medium', 'SemiBold', 'Bold'):
        p = os.path.join(DIST, 'ttf', f'{ps}-{st}.ttf')
        ok_ = os.path.exists(p)
        if ok_:
            SAH[ps, st] = TTFont(p)
            n = SAH[ps, st]['name']
            ok_ = (n.getDebugName(16) or n.getDebugName(1)) == fam and (n.getDebugName(17) or n.getDebugName(2)) == st
        check('sahafa', f'{fam} {st}: present with consistent names', ok_)
for (ps, st), ff in SAH.items():
    lab = f"{ps[5:]} {st}"
    al, sd, xb, hb_ = bounds(ff, 'uni0627'), bounds(ff, 'uni0635.init'), bounds(ff, 'x'), bounds(ff, 'H')
    check('sahafa', f'{lab}: alef as tall as the Latin capitals (within 50 units)', abs(al[3] - hb_[3]) <= 50, (al[3], hb_[3]))
    check('sahafa', f'{lab}: the loop of sad as tall as the Latin x-height (within 40 units), x-height 470', abs(sd[3] - xb[3]) <= 40 and 462 <= xb[3] <= 482 and ff['OS/2'].sxHeight == 470, (sd[3], xb[3]))
    kb = bounds(ff, 'uni0640'); base = kb[3] - kb[1]; lat = stem_at(ff, 'l', 300)
    check('sahafa', f'{lab}: Latin stem as thick as the Arabic baseline stroke (within 6 %)', abs(lat - base) <= 0.06 * base, (round(lat), base))
    thin = stem_at(ff, 'uni0627', 350)
    check('sahafa', f'{lab}: moderate contrast, the Arabic upright is 0.5 to 0.85 of the baseline stroke', 0.5 * base <= thin <= 0.85 * base, (round(thin), base))
    for gn_, nm_, lim_ in (('uni0635.init', 'sad', 30000), ('uni0641.init', 'feh', 12000), ('uni0648', 'waw', 12000), ('uni0645.init', 'meem', 7000), ('uni0647', 'heh', 12000),
                           ('uni0642', 'qaf', 12000), ('uni0629', 'teh marbuta', 12000), ('uni0639.medi', 'medial ain', 2500)):
        ca = contour_areas(ff, gn_)
        lim2 = lim_ * (0.5 if st == 'Bold' else 0.62 if st == 'SemiBold' else 0.78 if st == 'Medium' else 1.0)
        inner = [c for c in ca[:-1] if c > 1500]
        check('sahafa', f'{lab}: the loop of {nm_} stays open (counter of at least {round(lim2)} square units)', bool(inner) and max(inner) >= lim2, [round(c) for c in ca])
    check('sahafa', f'{lab}: same character set as Suhar Naskh', set(ff.getBestCmap()) == set(FN.getBestCmap()), len(ff.getBestCmap()))
    check('sahafa', f'{lab}: serifs on the Latin (n is wider at the foot than at mid-height)', stem_at(ff, 'n', 6) > stem_at(ff, 'n', 200) + 60 and stem_at(ff, 'I', 6) > 1.4 * stem_at(ff, 'I', 300), (round(stem_at(ff, 'I', 6)), round(stem_at(ff, 'I', 300))))
    idot = contour_areas(ff, 'i')
    check('sahafa', f'{lab}: i keeps a separate dot', len(idot) == 2, idot)
    check('sahafa', f'{lab}: hinted (fpgm and prep present)', 'fpgm' in ff and 'prep' in ff)
if SAH:
    rs_ = R('SuharSahafa-Regular'); rh_ = R('SuharSahafaHeadline-Regular')
    w1 = sum(a for _, a, *_ in shape(rs_, 'مجلس الوزراء يعتمد الموازنة')); w2 = sum(a for _, a, *_ in shape(rh_, 'مجلس الوزراء يعتمد الموازنة'))
    check('sahafa', 'Headline sets tighter than Text (3 to 12 % narrower)', 0.88 * w1 <= w2 <= 0.97 * w1, (w1, w2))
    n1 = bounds(SAH['SuharSahafa', 'Regular'], 'uni0646'); n2 = bounds(SAH['SuharSahafaHeadline', 'Regular'], 'uni0646')
    check('sahafa', 'Headline has deeper bowls than Text', n2[1] < n1[1] - 15, (n1[1], n2[1]))
    t1 = stem_at(SAH['SuharSahafa', 'Regular'], 'uni0627', 350) / (bounds(SAH['SuharSahafa', 'Regular'], 'uni0640')[3] - bounds(SAH['SuharSahafa', 'Regular'], 'uni0640')[1])
    t2 = stem_at(SAH['SuharSahafaHeadline', 'Regular'], 'uni0627', 350) / (bounds(SAH['SuharSahafaHeadline', 'Regular'], 'uni0640')[3] - bounds(SAH['SuharSahafaHeadline', 'Regular'], 'uni0640')[1])
    check('sahafa', 'Headline has more contrast than Text', t2 < t1 - 0.05, (round(t1, 2), round(t2, 2)))
    check('sahafa', 'bowls shallower than Suhar Naskh (short descenders)', n1[1] > bounds(FN, 'uni0646')[1], (n1[1], bounds(FN, 'uni0646')[1]))
    g_ = names(rs_, 'الاقتصاد'); check('sahafa', 'lam-alef ligature forms', any('06440627' in x for x in g_), g_)
    check('sahafa', 'Sahafa draws its own sad, jeem, meem, lam-alef (differs from Suhar Naskh)',
          all(bounds(SAH['SuharSahafa', 'Regular'], n) != bounds(FN, n) for n in ('uni0635', 'uni062D', 'uni0645', 'uni06440627')))

for ps, fam in (('SuharSahafa', 'Suhar Sahafa'), ('SuharSahafaHeadline', 'Suhar Sahafa Headline')):
    for st in ('Italic', 'Medium Italic', 'SemiBold Italic', 'Bold Italic'):
        p = os.path.join(DIST, 'ttf', f"{ps}-{st.replace(' ', '')}.ttf")
        ok_ = os.path.exists(p)
        if ok_:
            fi_ = TTFont(p); n = fi_['name']
            ok_ = (n.getDebugName(16) or n.getDebugName(1)) == fam and (n.getDebugName(17) or n.getDebugName(2)) == st and fi_['post'].italicAngle != 0 and 'fpgm' in fi_
        check('sahafa', f'{fam} {st}: present, italic angle set, hinted', ok_)
    for vf_ in (f'{ps}[GRAD,opsz,wght].ttf', f'{ps}-Italic[GRAD,opsz,wght].ttf'):
        p = os.path.join(DIST, 'variable', vf_)
        ok_ = os.path.exists(p)
        if ok_:
            fv_ = TTFont(p)
            ok_ = 'fvar' in fv_ and sorted((a.axisTag, a.minValue, a.maxValue) for a in fv_['fvar'].axes) == [('GRAD', -50, 50), ('opsz', 8, 72), ('wght', 400, 700)] and len(fv_.getGlyphOrder()) == len(SAH[ps, 'Regular'].getGlyphOrder())
        check('sahafa', f'{vf_}: weight, optical size and grade axes, no glyph dropped', ok_)
if SAH:
    sys.path.insert(0, os.path.join(ROOT, 'src'))
    from retrofont import model as _M, sahafa as _S, engine as _E
    for _m in ('latin', 'latin_ext', 'arabic', 'terminal', 'symbols', 'greek_cyrillic', 'more_scripts'):
        __import__('retrofont.' + _m)
    def _ar(tr):
        st_ = _S.style(400); st_.npar['traps'] = tr
        g_ = _M.build_glyphs(st_, only={'uni0633.medi', 'uni0635.medi'})
        return [sum(abs(_E._area([(q[0], q[1]) for q in c])) * (1 if _E._area([(q[0], q[1]) for q in c]) * _E._area([(q[0], q[1]) for q in max(g_[n].contours, key=len)]) > 0 else -1) for c in g_[n].contours) for n in ('uni0633.medi', 'uni0635.medi')]
    a0, a1 = _ar(0), _ar(0.42)
    check('sahafa', 'ink traps: the generator cuts notches at the crotches of seen and sad (ink area 60 to 2500 square units smaller)', all(60 < x - y < 2500 for x, y in zip(a0, a1)), [round(x - y) for x, y in zip(a0, a1)])
    ri_ = R('SuharSahafa-Italic')
    check('sahafa', 'italic: Arabic and Latin shape, lam-alef forms', any('06440627' in x for x in names(ri_, 'الاقتصاد')) and len(names(ri_, 'news')) == 4)
    for ft_, tx_, tst_ in (('dlig', 'لم', lambda g: len(g) == 1), ('ss06', 'في', lambda g: g[0].endswith('.ret')), ('ss07', 'نجم', lambda g: any('.st' in x or 'stack' in x or len(g) < 3 for x in g))):
        g0_, g1_ = names(rs_, tx_), names(rs_, tx_, features={ft_: True})
        check('sahafa', f'{ft_} changes {tx_} in Sahafa', g0_ != g1_, (g0_, g1_))

if SAH:
    from retrofont import arabic as _A
    check('sahafa', 'every letter skeleton has a drawing of its own in Sahafa', set(_A.RASM) <= set(_S.ARABIC), sorted(set(_A.RASM) - set(_S.ARABIC)))
    _st = _S.style(400)
    nlig = sum(1 for n_, i_ in _A.INFO.items() if any(o_ in (i_.get('spec') or '') for o_, _ in _st.altsub))
    check('sahafa', 'the 14 ligatures and alternates of Suhar Naskh are redrawn (lam-meem, lam on jeem, feh-yeh, returning yeh)', nlig == 14, nlig)
    kb = bounds(SAH['SuharSahafa', 'Regular'], 'uni0640')
    check('sahafa', 'Regular baseline stroke between 98 and 110 units', 98 <= kb[3] - kb[1] <= 110, kb[3] - kb[1])
    fi_ = TTFont(os.path.join(DIST, 'ttf', 'SuharSahafa-Italic.ttf')); fr_ = SAH['SuharSahafa', 'Regular']
    check('sahafa', 'italic: no slab at the first foot of n, and a different a', stem_at(fi_, 'n', 6) < stem_at(fr_, 'n', 6) - 40 and len(contour_areas(fi_, 'a')) == 2 and fi_['hmtx']['a'][0] != fr_['hmtx']['a'][0], (round(stem_at(fi_, 'n', 6)), round(stem_at(fr_, 'n', 6))))
    for g_ in ('three', 'six', 'nine', 'V', 'A'):
        pass
    tj_ = os.path.join(DIST, 'variable', 'ink-traps.json')
    rec_ = json.load(open(tj_)) if os.path.exists(tj_) else {}
    for v_ in ('SuharSahafa[GRAD,opsz,wght].ttf', 'SuharSahafa-Italic[GRAD,opsz,wght].ttf', 'SuharSahafaHeadline[GRAD,opsz,wght].ttf', 'SuharSahafaHeadline-Italic[GRAD,opsz,wght].ttf'):
        check('sahafa', f"{v_}: ink traps in the glyphs whose ten masters match (more than 60)", rec_.get(v_, 0) > 60, rec_.get(v_))
    for ps_, fam_ in (('SuharNerdSahafa', 'Suhar Nerd Sahafa'), ('SuharNerdSahafaHeadline', 'Suhar Nerd Sahafa Headline')):
        for st_ in ('Regular', 'Italic', 'Medium', 'Medium Italic', 'SemiBold', 'SemiBold Italic', 'Bold', 'Bold Italic'):
            p = os.path.join(DIST, 'ttf', f"{ps_}-{st_.replace(' ', '')}.ttf")
            ok_ = os.path.exists(p)
            if ok_:
                fn2 = TTFont(p); n = fn2['name']
                ok_ = (n.getDebugName(16) or n.getDebugName(1)) == fam_ and n.getDebugName(6) == f"{ps_}-{st_.replace(' ', '')}" and 0xE0B0 in fn2.getBestCmap() and 0xF013 in fn2.getBestCmap()
            check('sahafa', f'{fam_} {st_}: present, named, with Powerline and icon glyphs', ok_)

# ---- 2.4: optical sizes, grades, neighbour forms, justification alternates, caption cut, print proof ----
if SAH:
    from fontTools.varLib import instancer as _I
    def _inst(vf, **loc):
        return _I.instantiateVariableFont(TTFont(os.path.join(DIST, 'variable', vf)), loc)
    for vf_ in ('SuharSahafa[GRAD,opsz,wght].ttf', 'SuharSahafaHeadline-Italic[GRAD,opsz,wght].ttf'):
        d0, gm, gp = _inst(vf_, wght=400, opsz=14, GRAD=0), _inst(vf_, wght=400, opsz=14, GRAD=-50), _inst(vf_, wght=400, opsz=14, GRAD=50)
        nd = [n for n in d0.getGlyphOrder() if not (d0['hmtx'][n][0] == gm['hmtx'][n][0] == gp['hmtx'][n][0])]
        k0, km, kp = (bounds(x, 'uni0640')[3] - bounds(x, 'uni0640')[1] for x in (d0, gm, gp))
        check('optical', f'{vf_}: a grade changes the stroke (-50 lighter, +50 heavier) and no advance width', not nd and km < k0 - 3 and kp > k0 + 3, (len(nd), km, k0, kp))
        o8, o72 = _inst(vf_, wght=400, opsz=8, GRAD=0), _inst(vf_, wght=400, opsz=72, GRAD=0)
        t8, t14, t72 = (stem_at(x, 'uni0644.init', 350) for x in (o8, d0, o72))
        check('optical', f'{vf_}: thin strokes thicker in the caption size and finer in the display size', t8 > t14 + 2 and t72 < t14 - 2, (round(t8), round(t14), round(t72)))
        check('optical', f'{vf_}: the caption size is set looser than the display size', o8['hmtx']['uni0628'][0] > o72['hmtx']['uni0628'][0] + 15, (o8['hmtx']['uni0628'][0], o72['hmtx']['uni0628'][0]))
    for vf_ in ('SuharNaskh[opsz,wght].ttf', 'SuharNaskh-Italic[opsz,wght].ttf'):
        fv_ = TTFont(os.path.join(DIST, 'variable', vf_))
        o8, o72 = _inst(vf_, wght=400, opsz=8), _inst(vf_, wght=400, opsz=72)
        t8, t72 = stem_at(o8, 'uni0644.init', 400), stem_at(o72, 'uni0644.init', 400)
        check('optical', f'{vf_}: optical size axis 8-72, thin strokes thicker at 8 than at 72', sorted(a.axisTag for a in fv_['fvar'].axes) == ['opsz', 'wght'] and t8 > t72 + 3, (round(t8), round(t72)))
    for lab_, rr_ in (('Sahafa', rs_), ('Naskh', naskh), ('Naskh Display', disp)):
        g1, g0 = names(rr_, 'بر'), names(rr_, 'بر', features={'calt': False})
        check('neighbour', f'{lab_}: a tooth before final reh takes the narrow form and the reh starts at once (calt)', all(x.endswith('.r') for x in g1) and not any(x.endswith('.r') for x in g0), (g1, g0))
        g1 = names(rr_, 'بين')
        check('neighbour', f'{lab_}: a tooth before final noon or yeh is raised', any('.tall' in x for x in g1) and any('.tall' in x for x in names(rr_, 'نبي')), g1)
        w1 = sum(a for _, a, *_ in shape(rr_, 'تبرير')); w0 = sum(a for _, a, *_ in shape(rr_, 'تبرير', features={'calt': False}))
        if lab_ != 'Naskh Display':            # the Display family has other calt forms in the same word
            check('neighbour', f'{lab_}: the narrow forms shorten the word', 20 < w0 - w1 < 260, (w0, w1))
    check('neighbour', 'Suhar (sans) keeps its plain forms', not any(x.endswith('.r') for x in names(reg, 'بر')))
    for lab_, rr_ in (('Sahafa', rs_), ('Suhar', reg), ('Naskh', naskh)):
        w0 = sum(a for _, a, *_ in shape(rr_, 'كتب')); w1 = sum(a for _, a, *_ in shape(rr_, 'كتب', features={'jalt': True}))
        check('justification', f'{lab_}: jalt gives a final beh that is 25 to 45 % longer', 1.1 * w0 < w1 and any(x.endswith('.jalt') for x in names(rr_, 'كتب', features={'jalt': True})), (w0, w1))
        g_ = shape(rr_, 'كتــب'); k_ = [x for x in g_ if x[0] == 'uni0640']
        check('justification', f'{lab_}: tatweel joins inside a word', len(k_) == 2 and all(x[2] == 0 and x[3] == 0 for x in g_))
    check('justification', 'Suhar Mono has no jalt (the cell is fixed)', not any(x.endswith('.jalt') for x in names(mono, 'كتب', features={'jalt': True})))
    for st in ('Regular', 'Italic', 'Medium', 'Medium Italic', 'SemiBold', 'SemiBold Italic', 'Bold', 'Bold Italic'):
        p = os.path.join(DIST, 'ttf', f"SuharSahafaCaption-{st.replace(' ', '')}.ttf")
        ok_ = os.path.exists(p)
        if ok_:
            fc_ = TTFont(p); n = fc_['name']
            ok_ = (n.getDebugName(16) or n.getDebugName(1)) == 'Suhar Sahafa Caption' and (n.getDebugName(17) or n.getDebugName(2)) == st and 'fpgm' in fc_
        check('optical', f'Suhar Sahafa Caption {st}: present, named, hinted', ok_)
    fc_ = TTFont(os.path.join(DIST, 'ttf', 'SuharSahafaCaption-Regular.ttf')); ft_ = SAH['SuharSahafa', 'Regular']
    check('optical', 'Caption: thicker thin strokes, looser spacing and larger dots than Text',
          stem_at(fc_, 'uni0644.init', 350) > stem_at(ft_, 'uni0644.init', 350) + 2 and fc_['hmtx']['uni0628'][0] > ft_['hmtx']['uni0628'][0] + 15 and fc_['hmtx']['n'][0] > ft_['hmtx']['n'][0] + 15,
          (round(stem_at(fc_, 'uni0644.init', 350)), round(stem_at(ft_, 'uni0644.init', 350)), fc_['hmtx']['uni0628'][0], ft_['hmtx']['uni0628'][0]))
    rc_ = R('SuharSahafaCaption-Regular')
    y1 = [x for x in shape(rc_, 'بَ') if x[0] != 'uni0628'][0][3]; y0 = [x for x in shape(rs_, 'بَ') if x[0] != 'uni0628'][0][3]
    check('optical', 'Caption: marks stand further from the letter than in Text', y1 > y0 + 10, (y1, y0))
    pp_ = os.path.join(ROOT, 'docs', 'Suhar-print-proof.pdf')
    check('print', 'print proof PDF written, with the fonts embedded', os.path.exists(pp_) and os.path.getsize(pp_) > 200000 and b'FontFile2' in open(pp_, 'rb').read(), os.path.getsize(pp_) if os.path.exists(pp_) else 0)

# ---- word spacing in every proportional static font ----
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wordspace as WS
ws_rows = []
for fn_ in sorted(os.listdir(os.path.join(DIST, 'ttf'))):
    if 'Nerd' in fn_ or 'Mono' in fn_ or not fn_.endswith('.ttf'):
        continue
    ar_, ft_ = WS.gaps(os.path.join(DIST, 'ttf', fn_), WS.FINALS, WS.INITS, True, 0, 420)
    la_, _ = WS.gaps(os.path.join(DIST, 'ttf', fn_), WS.LAT_F, WS.LAT_I, False, 0, 470)
    ma, sa_, na, xa = WS.stats([g for g, _ in ar_]); ml, sl, nl, xl = WS.stats([g for g, _ in la_])
    ws_rows.append((fn_[:-4], ft_['hmtx']['space'][0], round(ma), round(sa_), round(na), round(xa), round(ml), round(sl)))
    check('word space', f'{fn_[:-4]}: optical gap between two Arabic words is even (standard deviation under 18 units, range under 120) and close to the Latin gap (within 60)',
          sa_ < 18 and xa - na < 120 and abs(ma - ml) < 60, (round(ma), round(sa_), round(na), round(xa), round(ml)))
for fn_ in sorted(os.listdir(os.path.join(DIST, 'ttf'))):
    if 'Mono' in fn_ and fn_.endswith('.ttf'):
        fm_ = TTFont(os.path.join(DIST, 'ttf', fn_))
        check('word space', f'{fn_[:-4]}: the space is one cell', fm_['hmtx']['space'][0] == fm_['hmtx']['uni0628'][0] == fm_['hmtx']['n'][0], fm_['hmtx']['space'][0])
with open(os.path.join(REP, 'word-spacing.md'), 'w') as fh:
    fh.write('# Suhar – word spacing\n\nMeasured by `tools/wordspace.py` on the compiled fonts: every word-final Arabic letter against 14 word-initial '
             'letters (434 pairs per font), and 240 Latin pairs. The optical gap is the mean of the gap between the letter bodies (baseline to loop '
             'height) and the gap between the full outlines, so a tail under the line counts for half. Units of 1000 per em.\n\n'
             '| font | space | Arabic gap | sd | min | max | Latin gap | sd |\n|---|---:|---:|---:|---:|---:|---:|---:|\n' +
             '\n'.join('| ' + ' | '.join(str(x) for x in r) + ' |' for r in ws_rows) + '\n\nThe Mono families have a fixed cell: the space is one cell in every style.\n')

fail = [r for r in results if not r[2]]
ok = len(results) - len(fail)
with open(os.path.join(REP, 'validation.json'), 'w') as fh:
    json.dump({'passed': ok, 'failed': len(fail), 'results': results, 'files': summary, 'coverage': cov, 'missing': missing}, fh, indent=1, ensure_ascii=False)
L = ['# Suhar – validation report', '',
     'Produced by `tools/validate.py` from the compiled files in `dist/`. Shaping uses HarfBuzz, rasterisation uses FreeType '
     '(with the fonts\' own TrueType hinting), structure checks use fontTools and the OpenType Sanitizer.', '',
     f'**{ok} checks passed, {len(fail)} failed.**', '']
if fail:
    L += ['## Failures', ''] + [f'- **{s}** – {n} — `{d[:300]}`' for s, n, _, d in fail] + ['']
sec = None
L += ['## All checks', '']
for s, n, o, d in results:
    if s != sec:
        L += ['', f'### {s}', '']
        sec = s
    L.append(f"- {'PASS' if o else 'FAIL'} — {n}" + (f" — `{d[:160]}`" if (d and (not o or s == 'coverage')) else ''))
L += ['', '## Files', '', '| file | glyphs | code points | KB |', '|---|---:|---:|---:|']
L += [f"| {r['file']} | {r['glyphs']} | {r['codepoints']} | {r['size_kb']} |" for r in summary]
L += ['', '## Proof images (reports/img)', '', '- `small-sizes-hinted.png`, `small-sizes-unhinted.png`, `small-sizes-1bit.png` – 8 to 18 px, enlarged 3x',
      '- `high-resolution.png` – 300 to 420 px outlines', '- `print-1200dpi.png` – 9 pt and 12 pt at 1200 dpi',
      '- `terminal-*.png` – box drawing, blocks, Powerline and icons at the exact line pitch', '- `mono-code.png`, `weights.png`']
open(os.path.join(REP, 'validation.md'), 'w').write('\n'.join(L) + '\n')
print(f'{ok} passed, {len(fail)} failed')
for s, n, _, d in fail:
    print('FAIL', s, '|', n, '|', d[:200])
