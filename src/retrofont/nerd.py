"""Add the Nerd Fonts symbol set (third party, see third_party/nerd-fonts) to a
compiled RetroUI font.  Glyphs that RetroUI already draws itself (Powerline
E0A0-E0A3 / E0B0-E0BF, power symbols, ...) are kept; only missing code points
are added.  Icons are scaled uniformly; in the Mono family every icon fits one
600-unit cell."""
import os, pickle
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from .model import MONO_W, ASCENT, DESCENT

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'third_party', 'nerd-fonts')
CACHE = os.path.join(ROOT, 'build', 'nerd-cache.pkl')
NERD_VERSION = '3.5.1'


def prepare():
    """pre-transform all icons once: {mono: {cp: (recording, advance)}}"""
    if os.path.exists(CACHE):
        return
    data = {}
    for mono, fname in ((False, 'SymbolsNerdFont-Regular.ttf'), (True, 'SymbolsNerdFontMono-Regular.ttf')):
        f = TTFont(os.path.join(SRC, fname))
        gs = f.getGlyphSet()
        cmap = f.getBestCmap()
        upm = f['head'].unitsPerEm
        cell_c = (f['hhea'].ascent + f['hhea'].descent) / 2
        if mono:
            s = MONO_W / upm * 1.16        # a little larger than the nominal cell; icons have their own margins
            dy = (ASCENT + DESCENT) / 2 - cell_c * s
        else:
            s = 0.44
            dy = 350 - cell_c * s
        out = {}
        for cp, gn in cmap.items():
            rec = DecomposingRecordingPen(gs)
            gs[gn].draw(rec)
            tr = RecordingPen()
            dxm = (MONO_W - upm * s) / 2 if mono else 0
            tp = TransformPen(tr, (s, 0, 0, s, dxm, dy))
            rec.replay(tp)
            val = [(op, tuple(None if p is None else (round(p[0]), round(p[1])) for p in args)) for op, args in tr.value]
            out[cp] = (val, MONO_W if mono else round(f['hmtx'][gn][0] * s))
        data[mono] = out
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, 'wb') as fh:
        pickle.dump(data, fh)


_DATA = None


def _data():
    global _DATA
    if _DATA is None:
        prepare()
        with open(CACHE, 'rb') as fh:
            _DATA = pickle.load(fh)
    return _DATA


def _nm(s, mono):
    if mono:
        return s.replace('Suhar Mono', 'Suhar Nerd Mono').replace('SuharMono', 'SuharNerdMono')
    if 'SuharCondensed' in s:
        return s.replace('SuharCondensed', 'SuharNerdCondensed')
    return s.replace('Suhar', 'Suhar Nerd', 1).replace('Suhar Nerd-', 'SuharNerd-') if 'Suhar-' in s else s.replace('Suhar', 'Suhar Nerd', 1)


def _rename(font, mono):
    for rec in font['name'].names:
        s = rec.toUnicode()
        n = s
        if rec.nameID in (1, 3, 4, 6, 16):
            n = _nm(s, mono)
        elif rec.nameID == 0:
            n = s + f'. Icons: Nerd Fonts {NERD_VERSION} (c) Ryan L McIntyre and the respective icon authors; see LICENSES.'
        if n != s:
            rec.string = n
    if 'CFF ' in font:
        cff = font['CFF '].cff
        td = cff.topDictIndex[0]
        cff.fontNames[0] = _nm(cff.fontNames[0], mono)
        for attr in ('FullName', 'FamilyName'):
            v = getattr(td, attr, None)
            if v:
                setattr(td, attr, _nm(v, mono))


def patch(path, mono):
    font = TTFont(path)
    data = _data()[mono]
    cmap = font.getBestCmap()
    order = list(font.getGlyphOrder())
    add = [(cp, v) for cp, v in sorted(data.items()) if cp not in cmap]
    is_cff = 'CFF ' in font
    hmtx = font['hmtx']
    names = []
    if is_cff:
        cff = font['CFF '].cff
        td = cff.topDictIndex[0]
        cs = td.CharStrings
        private = td.Private
        for cp, (val, adv) in add:
            gn = 'nf-%04X' % cp
            pen = T2CharStringPen(adv, None)
            r = RecordingPen()
            r.value = val
            r.replay(pen)
            ch = pen.getCharString(private, cff.GlobalSubrs)
            cs.charStringsIndex.append(ch)
            cs.charStrings[gn] = len(cs.charStringsIndex) - 1
            td.charset.append(gn)
            xs = [p[0] for op, a in val for p in a if p is not None]
            hmtx[gn] = (adv, min(xs) if xs else 0)
            names.append((cp, gn))
    else:
        glyf = font['glyf']
        for cp, (val, adv) in add:
            gn = 'nf-%04X' % cp
            pen = TTGlyphPen(None)
            r = RecordingPen()
            r.value = val
            r.replay(pen)
            g = pen.glyph()
            glyf[gn] = g
            g.recalcBounds(glyf)
            hmtx[gn] = (adv, getattr(g, 'xMin', 0))
            names.append((cp, gn))
    font.setGlyphOrder(order + [gn for _, gn in names])
    if not is_cff:
        font['glyf'].glyphOrder = font.getGlyphOrder()
    for t in font['cmap'].tables:
        if not t.isUnicode():
            continue
        for cp, gn in names:
            if t.format == 4 and cp > 0xFFFF:
                continue
            t.cmap[cp] = gn
    font['maxp'].numGlyphs = len(font.getGlyphOrder())
    if 'post' in font and font['post'].formatType == 2:
        font['post'].extraNames = []
    _rename(font, mono)
    d, b = os.path.split(path)
    nb = _nm(b, mono)
    out = os.path.join(d, nb)
    font.save(out)
    return out
