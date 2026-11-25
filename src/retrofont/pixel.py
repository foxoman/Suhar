"""Pixel fonts: every glyph of a hinted Suhar TTF is rasterised by FreeType at one pixel size (1-bit, hinted)
and the bitmap is stored as an outline of whole-pixel rectangles.  At its design size (and integer multiples)
the result is drawn pixel for pixel, with no anti-aliasing blur, by any renderer; shaping tables are kept,
kerning is removed, advances are whole pixels."""
import os, sys, io
import freetype
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools import subset

UNIT = 100          # font units per pixel

PIXEL_SETS = [('Suhar-Regular', 'Suhar Pixel', 'Regular', (8, 9, 10, 11, 12, 13)),
              ('Suhar-Bold', 'Suhar Pixel', 'Bold', (8, 9, 10, 11, 12, 13)),
              ('SuharMono-Regular', 'Suhar Mono Pixel', 'Regular', (12, 14)),
              ('SuharMono-Bold', 'Suhar Mono Pixel', 'Bold', (12, 14))]


def _rects(bits):
    """1-bit array -> list of (x0, y0, x1, y1) in pixel units (y down), runs merged vertically"""
    out, open_ = [], {}
    h, w = bits.shape
    for y in range(h + 1):
        runs = set()
        if y < h:
            row = bits[y]; x = 0
            while x < w:
                if row[x]:
                    x0 = x
                    while x < w and row[x]:
                        x += 1
                    runs.add((x0, x))
                else:
                    x += 1
        for r in list(open_):
            if r not in runs:
                out.append((r[0], open_.pop(r), r[1], y))
        for r in runs:
            open_.setdefault(r, y)
    return out


def make(src, px, family, style, dst, hand_arabic=False):
    opt = subset.Options()
    opt.glyphs = ['*']; opt.layout_features = ['*']; opt.layout_scripts = ['*']; opt.name_IDs = ['*']; opt.name_languages = ['*']
    opt.notdef_outline = True; opt.glyph_names = True; opt.hinting = False; opt.legacy_cmap = True; opt.symbol_cmap = True
    opt.prune_unicode_ranges = False; opt.recalc_bounds = True; opt.drop_tables += ['kern', 'gasp']
    font = TTFont(src)
    feats = sorted({f.FeatureTag for t in ('GSUB', 'GPOS') if t in font for f in font[t].table.FeatureList.FeatureRecord} - {'kern'})
    opt.layout_features = feats
    sub = subset.Subsetter(opt); sub.populate(glyphs=font.getGlyphOrder(), unicodes=list(font.getBestCmap())); sub.subset(font)
    scale_upem(font, px * UNIT)
    face = freetype.Face(src); face.set_pixel_sizes(0, px)
    flags = freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO
    order = font.getGlyphOrder(); glyf = font['glyf']; hmtx = font['hmtx']
    src_order = TTFont(src, lazy=True).getGlyphOrder(); gid = {n: i for i, n in enumerate(src_order)}
    src_adv = TTFont(src)['hmtx'].metrics
    for name in order:
        face.load_glyph(gid[name], flags)
        bm = face.glyph.bitmap
        pen = TTGlyphPen(None)
        if bm.rows and bm.width:
            data = np.array(bm.buffer, dtype=np.uint8).reshape(bm.rows, bm.pitch)
            bits = np.unpackbits(data, axis=1)[:, :bm.width]
            left, top = face.glyph.bitmap_left, face.glyph.bitmap_top
            for x0, y0, x1, y1 in _rects(bits):
                X0, X1 = (left + x0) * UNIT, (left + x1) * UNIT
                Y1, Y0 = (top - y0) * UNIT, (top - y1) * UNIT
                pen.moveTo((X0, Y0)); pen.lineTo((X0, Y1)); pen.lineTo((X1, Y1)); pen.lineTo((X1, Y0)); pen.closePath()
        glyf[name] = pen.glyph()
        adv = src_adv[name][0]
        a = 0 if adv == 0 else max(1, int(round(adv * px / 1000.0))) * UNIT
        glyf[name].recalcBounds(glyf)
        hmtx[name] = (a, getattr(glyf[name], 'xMin', 0) if glyf[name].numberOfContours else 0)
    if hand_arabic:
        from . import pixel_arabic as PA
        for name, b in PA.table(bold=style == 'Bold').items():
            if name not in glyf.glyphs:
                continue
            ys = [y for _, y in b.px]
            top, bot = max(ys), min(ys)
            arr = np.zeros((top - bot + 1, b.w), dtype=np.uint8)
            for x, y in b.px:
                arr[top - y, x] = 1
            off = 0 if b.jl else 1
            pen = TTGlyphPen(None)
            for x0, y0, x1, y1 in _rects(arr):
                X0, X1 = (off + x0) * UNIT, (off + x1) * UNIT
                Y1, Y0 = (top + 1 - y0) * UNIT, (top + 1 - y1) * UNIT
                pen.moveTo((X0, Y0)); pen.lineTo((X0, Y1)); pen.lineTo((X1, Y1)); pen.lineTo((X1, Y0)); pen.closePath()
            glyf[name] = pen.glyph()
            glyf[name].recalcBounds(glyf)
            hmtx[name] = ((b.w + off) * UNIT, off * UNIT + 0)
    asc = int(np.ceil(font['hhea'].ascent / UNIT)) * UNIT; desc = -int(np.ceil(-font['hhea'].descent / UNIT)) * UNIT
    font['hhea'].ascent, font['hhea'].descent, font['hhea'].lineGap = asc, desc, 0
    o = font['OS/2']; o.sTypoAscender, o.sTypoDescender, o.sTypoLineGap = asc, desc, 0; o.usWinAscent, o.usWinDescent = asc, -desc
    for t in ('fpgm', 'prep', 'cvt ', 'hdmx', 'VDMX', 'LTSH'):
        if t in font:
            del font[t]
    from fontTools.ttLib import newTable
    g = newTable('gasp'); g.gaspRange = {0xFFFF: 0x0001}; font['gasp'] = g        # grid-fit, never smooth
    fam = f"{family} {px}"; ps = fam.replace(' ', '') + '-' + style
    for rec in list(font['name'].names):
        v = {1: fam, 2: style, 3: f"{ps};{px}px", 4: f"{fam} {style}".replace(' Regular', ''), 6: ps, 16: None, 17: None}.get(rec.nameID, 0)
        if v is None:
            font['name'].removeNames(nameID=rec.nameID)
        elif v:
            rec.string = v
    font['head'].lowestRecPPEM = px
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    font.save(dst)
    return dst


HAND_SIZES = (8, 9, 10)                # sizes that use the hand-drawn Arabic bitmaps (alef 7 px)
ARABIC_BOOST = {8: 1.25, 9: 1.22}       # at these sizes Arabic is drawn as large as at 10 and 11 px


def boosted_source(stem, px, tmp):
    """hinted TTF of the same style with a larger Arabic body, for the smallest pixel sizes"""
    from . import build as B
    import ufo2ft
    for m in ('latin_ext', 'arabic', 'terminal', 'symbols', 'greek_cyrillic', 'more_scripts'):
        __import__('retrofont.' + m)
    st = B.mkstyle('Sans', 700 if 'Bold' in stem else 400, False)
    st.arboost = ARABIC_BOOST[px]
    ufo, gl = B.make(st, 'Sans')
    os.makedirs(tmp, exist_ok=True)
    raw = os.path.join(tmp, f'{stem}-boost{px}.raw.ttf'); out = os.path.join(tmp, f'{stem}-boost{px}.ttf')
    ufo2ft.compileTTF(ufo, removeOverlaps=False).save(raw)
    B.autohint(raw, out)
    return out


def main(dist='dist'):
    res = []
    for stem, family, style, sizes in PIXEL_SETS:
        for px in sizes:
            dst = os.path.join(dist, 'pixel', f"{family.replace(' ', '')}{px}-{style}.ttf")
            src = os.path.join(dist, 'ttf', stem + '.ttf')
            if px in ARABIC_BOOST and 'Mono' not in stem:
                src = boosted_source(stem, px, os.path.join(dist, '..', 'build', 'pixel-src'))
            make(src, px, family, style, dst, hand_arabic=px in HAND_SIZES and 'Mono' not in stem)
            print('pixel', dst, flush=True); res.append(dst)
    return res


if __name__ == '__main__':
    main(*sys.argv[1:])
