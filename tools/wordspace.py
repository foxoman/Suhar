"""Word spacing check: the optical gap between two Arabic words (the mean of the gap in the band from the baseline to
the loop height and the gap between the full outlines, so that a tail under the line counts for half), for every word-final letter against a set of word-initial letters; and the Latin gap between two words.
    python3 tools/wordspace.py FONT.ttf [...]        prints one line per font; --worst lists the extreme pairs"""
import math
import sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
import pathops

FINALS = "ابتثجحخدذرزسشصضطظعغفقكلمنهويةىء"
INITS = "ابجسصطعفكلمهود"
LAT_F, LAT_I = "enasdtrylohkgf.,", "atswhocbinmfpdl"


AR_TAN, LAT_TAN = -math.tan(math.radians(9.0)), math.tan(math.radians(11.0))     # the slants of the italics


def band_bounds(gs, name, y0, y1, cache, tan=0.0):
    """bounds of the part of a glyph between y0 and y1; in an italic the outline is first set upright again, because a
    gap between slanted letters is seen along the slant"""
    key = (name, y0, y1)
    if key not in cache:
        pen = DecomposingRecordingPen(gs)
        gs[name].draw(pen)
        p = pathops.Path()
        if tan:
            from fontTools.pens.transformPen import TransformPen
            pen.replay(TransformPen(p.getPen(), (1, 0, -tan, 1, 0, 0)))
        else:
            pen.replay(p.getPen())
        r = pathops.Path()
        rp = r.getPen()
        rp.moveTo((-5000, y0)); rp.lineTo((5000, y0)); rp.lineTo((5000, y1)); rp.lineTo((-5000, y1)); rp.closePath()
        try:
            b = pathops.op(p, r, pathops.PathOp.INTERSECTION, fix_winding=True).bounds
        except Exception:
            b = p.bounds
        cache[key] = b if b and b[2] > b[0] else None
    return cache[key]


def gaps(path, finals, inits, rtl, y0, y1):
    font = TTFont(path)
    gs, order = font.getGlyphSet(), font.getGlyphOrder()
    face = hb.Face(open(path, 'rb').read())
    f = hb.Font(face)
    out = []
    cache = {}
    tan = (AR_TAN if rtl else LAT_TAN) if font['post'].italicAngle else 0.0
    bbf = lambda gs_, n_, a_, b_: band_bounds(gs_, n_, a_, b_, cache, tan)
    for a in finals:
        for b in inits:
            buf = hb.Buffer()
            buf.add_str(("ن" + a + " " + b + "ن") if rtl else ("n" + a + " " + b + "n"))
            buf.guess_segment_properties()
            hb.shape(f, buf)
            x, items = 0, []
            for i, p in zip(buf.glyph_infos, buf.glyph_positions):
                items.append((order[i.codepoint], x + p.x_offset, i.cluster))
                x += p.x_advance
            sp = next((k for k, it in enumerate(items) if it[2] == 2), None)
            if sp is None or sp == 0 or sp == len(items) - 1:
                continue
            L, R = items[sp - 1], items[sp + 1]
            k = sp - 1
            while bbf(gs, items[k][0], y0, y1) is None and k > 0:
                k -= 1
            L = items[k]
            k = sp + 1
            while bbf(gs, items[k][0], y0, y1) is None and k < len(items) - 1:
                k += 1
            R = items[k]
            bl, br = bbf(gs, L[0], y0, y1), bbf(gs, R[0], y0, y1)
            if bl is None or br is None:
                continue
            fl, fr = bbf(gs, L[0], -1000, 2000), bbf(gs, R[0], -1000, 2000)
            g1 = (R[1] + br[0]) - (L[1] + bl[2])
            g2 = (R[1] + fr[0]) - (L[1] + fl[2])
            out.append(((g1 + g2) / 2, a + " " + b))
    return out, font


def stats(v):
    n = len(v)
    m = sum(v) / n
    return m, (sum((x - m) ** 2 for x in v) / n) ** 0.5, min(v), max(v)


if __name__ == '__main__':
    worst = '--worst' in sys.argv
    print(f"{'font':44s} {'space':>5s} | Arabic gap mean  sd   min  max | Latin gap mean  sd   min  max")
    for p in [a for a in sys.argv[1:] if not a.startswith('--')]:
        ar, font = gaps(p, FINALS, INITS, True, 0, 420)
        la, _ = gaps(p, LAT_F, LAT_I, False, 0, 470)
        sp = font['hmtx']['space'][0]
        ma, sa, na, xa = stats([g for g, _ in ar])
        ml, sl, nl, xl = stats([g for g, _ in la])
        print(f"{p.split('/')[-1][:44]:44s} {sp:5d} | {ma:15.0f} {sa:3.0f} {na:5.0f} {xa:4.0f} | {ml:14.0f} {sl:3.0f} {nl:5.0f} {xl:4.0f}")
        if worst:
            ar.sort()
            print("    tightest:", [(round(g), t) for g, t in ar[:6]], "\n    widest:  ", [(round(g), t) for g, t in ar[-6:]])
