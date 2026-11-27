"""Suhar App: smaller fonts for programs that embed their font (Retro Nim UI apps, phone apps).

From the built fonts it writes nim/fonts/app/:
    SuharApp-*.ttf        every language of Suhar; no box drawing, braille, Powerline or terminal symbols; no hinting
                          (phone screens and Retro Nim UI do not use it); only the layout features an interface needs
    SuharAppLite-*.ttf    Arabic and Western European Latin only
    SuharAppRead-*.ttf    Suhar Sahafa, cut down the same way, for long reading text inside an app
and reports/app-fonts.md with the sizes and the vertical extents an interface has to leave room for.

    python3 tools/make_app_fonts.py"""
import os
import sys

import uharfbuzz as hb
from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'dist', 'ttf')
OUT = os.path.join(ROOT, 'nim', 'fonts', 'app')
STYLES = ('Regular', 'Bold', 'Italic', 'BoldItalic')
# what an interface needs: joining, required ligatures, neighbour forms, marks, kerning, local forms, figure widths
FEATURES = ['ccmp', 'locl', 'init', 'medi', 'fina', 'isol', 'rlig', 'liga', 'calt', 'kern', 'mark', 'mkmk', 'curs', 'dist', 'tnum', 'pnum']
DROP = [(0x2500, 0x259F), (0x2800, 0x28FF), (0xE0A0, 0xE0FF), (0x1FB00, 0x1FBFF), (0x23B0, 0x23FF), (0x2200, 0x220F)]
# The Arabic presentation forms stay: Retro Nim UI looks for them to decide whether a font has Arabic at all, and
# without them it draws Arabic in its built-in font.
LITE = [(0x20, 0x7E), (0xA0, 0x17F), (0x2010, 0x2027), (0x2030, 0x203A), (0x2044, 0x2044), (0x20A0, 0x20C4), (0x2122, 0x2122), (0x2190, 0x2193),
        (0x2212, 0x2212), (0x2260, 0x2265), (0x2713, 0x2714), (0x2022, 0x2022), (0x2026, 0x2026), (0x25CF, 0x25CF), (0x25CB, 0x25CB),
        (0x060C, 0x060C), (0x061B, 0x061B), (0x061F, 0x061F), (0x0621, 0x063A), (0x0640, 0x0652), (0x0660, 0x066D), (0x0670, 0x0671),
        (0x200C, 0x200F), (0x202A, 0x202E), (0x2066, 0x2069), (0xE100, 0xE148), (0xFE70, 0xFEFC)]


def inside(cp, ranges):
    return any(a <= cp <= b for a, b in ranges)


def make(src_ps, style, family, ps, keep):
    f = TTFont(os.path.join(SRC, f'{src_ps}-{style}.ttf'), recalcTimestamp=False)
    cps = [c for c in f.getBestCmap() if keep(c)]
    o = subset.Options()
    o.layout_features = FEATURES
    o.hinting = False
    o.glyph_names = False
    o.notdef_outline = True
    o.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14, 16, 17]
    o.name_languages = [0x409]
    o.drop_tables += ['DSIG', 'meta']
    s = subset.Subsetter(o)
    s.populate(unicodes=cps)
    s.subset(f)
    sub = {'Regular': 'Regular', 'Bold': 'Bold', 'Italic': 'Italic', 'BoldItalic': 'Bold Italic'}[style]
    for rec in f['name'].names:
        if rec.nameID in (1, 16):
            rec.string = family
        elif rec.nameID == 4:
            rec.string = f'{family} {sub}'
        elif rec.nameID == 6:
            rec.string = f'{ps}-{style}'
        elif rec.nameID == 3:
            rec.string = f"{rec.toUnicode().split(';')[0]};{ps}-{style}"
    f['head'].flags &= ~(1 << 3)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f'{ps}-{style}.ttf')
    f.save(p)
    return p, len(cps)


def extents(path, texts):
    f = TTFont(path)
    gs, order = f.getGlyphSet(), f.getGlyphOrder()
    font = hb.Font(hb.Face(open(path, 'rb').read()))
    hi, lo = -9999, 9999
    for t in texts:
        b = hb.Buffer()
        b.add_str(t)
        b.guess_segment_properties()
        hb.shape(font, b)
        for i, q in zip(b.glyph_infos, b.glyph_positions):
            bp = BoundsPen(gs)
            gs[order[i.codepoint]].draw(bp)
            if bp.bounds:
                hi, lo = max(hi, bp.bounds[3] + q.y_offset), min(lo, bp.bounds[1] + q.y_offset)
    return round(hi), round(lo)


PLAIN = [chr(c) for c in range(0x621, 0x64B)] + ['لا', 'لأ', 'لإ', 'لآ', 'كل', 'جي', 'عي'] + list('AÅÉÑÖÜgjpqyÇçşţ') + ['Hg', 'fj']
VOWELLED = ['أَ', 'إِ', 'لَّا', 'كُّ', 'طَّ', 'يٍّ', 'جِّ', 'عٍ', 'رٍّ', 'بِسْمِ ٱللَّهِ', 'Ǻ', 'Ế', 'ự']

if __name__ == '__main__':
    rows = []
    for src_ps, family, ps, keep, what in (
            ('Suhar', 'Suhar App', 'SuharApp', lambda c: not inside(c, DROP), 'Suhar, every language'),
            ('Suhar', 'Suhar App Lite', 'SuharAppLite', lambda c: inside(c, LITE), 'Suhar, Arabic and Western European Latin'),
            ('SuharSahafa', 'Suhar App Read', 'SuharAppRead', lambda c: not inside(c, DROP), 'Suhar Sahafa, every language')):
        for st in STYLES:
            p, n = make(src_ps, st, family, ps, keep)
            full = os.path.getsize(os.path.join(SRC, f'{src_ps}-{st}.ttf'))
            rows.append((os.path.basename(p), what, n, len(TTFont(p).getGlyphOrder()), round(os.path.getsize(p) / 1024), round(full / 1024),
                         extents(p, PLAIN), extents(p, VOWELLED)))
    asc = TTFont(os.path.join(OUT, 'SuharApp-Regular.ttf'))['hhea']
    L = ['# Suhar App fonts', '', 'Made by `tools/make_app_fonts.py` from the release fonts: no hinting, only the layout features an interface needs, '
         'and without box drawing, braille, Powerline and terminal symbols. The letter shapes, spacing and kerning are those of the release fonts.', '',
         '| file | contents | characters | glyphs | size (KB) | release font (KB) |', '|---|---|---:|---:|---:|---:|'] + \
        [f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |' for r in rows] + \
        ['', '## Room above and below the line', '', f'The line box of the fonts is {asc.ascent} above and {asc.descent} below the baseline (1000 units per em). '
         'Ink reaches these heights, in the Regular and Bold of each family:', '', '| file | plain text: top | bottom | fully vowelled text: top | bottom |', '|---|---:|---:|---:|---:|'] + \
        [f'| {r[0]} | {r[6][0]} | {r[6][1]} | {r[7][0]} | {r[7][1]} |' for r in rows if '-Regular' in r[0] or r[0].endswith('-Bold.ttf')] + \
        ['', 'Plain text is the Arabic alphabet with its hamza forms and lam-alef, and accented Latin capitals. Fully vowelled text has shadda with a vowel on '
         'tall letters and tanween under deep ones; it needs about a third of an em more room above and a quarter more below than the line box gives.']
    open(os.path.join(ROOT, 'reports', 'app-fonts.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[4:]))
