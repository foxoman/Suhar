"""Combining marks, precomposed Latin (Latin-1, Extended-A/B, Extended
Additional incl. Vietnamese), special letters and general punctuation."""
import unicodedata as ud
from .model import G, REG, gname, GlyphOut, MONO_W
from .latin import _COMMA

# ---- special letters ------------------------------------------------------
G(0x131, "0,0 0,X-5!14", 70, 70, mono="-130,x 20,x 20,b; -150,b 190,b")
G(0x237, "88,X-5!14 88,-78 ~88,d -8,d -36,d", -8, 70, mono="20,x 190,x 190,-70 ~190,d 70,d 0,d")
G('Æ', "0,0!h 380,C!h; 400,0 400,C; 380,c 772,c; 400,366 734,366; 400,b 782,b; 126,232 400,232", 2, 32)
G('Ø', "use:O; w.8 44,-34 548,C+34", 42, 42)
G('ø', "use:o; w.8 22,-44 374,X+44", 40, 40)
G('Ð', "use:D; -66,366 196,366", 20, 42, also=[0x110])
G('Þ', "0,0 0,C; z 0,166 0,540 262,540 ~466,540 466,353 ~466,166 262,166", 78, 36)
G('ß', "0,0 0,520 ~0,co 175,co ~335,co 335,548 ~335,405 190,405; 190,405 ~396,405 396,205 ~396,bo 222,bo 128,bo", 70, 38)
G('æ', "use:a; use:e|0.92,1,338,0", 42, 38)
G('œ', "use:o; use:e|0.95,1,372,0", 40, 38)
G('Œ', "use:O|0.8,1,0,0; 474,0 474,C; 474,c 846,c; 474,366 812,366; 474,b 856,b", 42, 32)
G('đ', "use:d; w.85 236,612 474,612", 40, 10)
G('ħ', "use:h; w.85 -64,612 160,612", 14, 68)
G('Ħ', "use:H; w.85 -44,548 516,548", 34, 34)
G('ł', "use:l; w.9 -86,292 86,424", 26, 18)
G('Ł', "use:L; w.9 -84,296 150,436", 18, 18)
G('ŧ', "use:t; w.85 -4,330 228,330", 14, 10)
G('Ŧ', "use:T; w.85 110,366 426,366", 20, 20)
G('ŋ', "0,0 0,X-5!14; 0,364@.72 ~0,xo 178,xo ~336,xo 336,336 336,-78 ~336,d 252,d 212,d", 70, 68)
G('Ŋ', "0,0 0,C; 0,500@.8 ~0,co 240,co ~472,co 472,470 472,-70 ~472,d 372,d 326,d", 78, 76)
G('ĸ', "0,0 0,X-5!14; 332,X!h 8,196; 124,304 346,0!h", 70, 0)
G('ſ', "96,0 96,566 ~96,c 226,c 248,c", 70, -6)
G('ƒ', "0,d ~96,d 110,-90 214,588 ~230,c 326,c 346,c; 56,x-60 300,x-60", 10, 0)
G('ə', "use:e|-1,-1,396,X", 38, 40, also=[0x1DD])
G('Ə', "use:e|-1.34,-1.346,560,C", 42, 44)
G('µ', "use:u; 0,X 0,D", 68, 70, also=[0x3BC])
G('ð', "use:o; 396,270 ~396,520 262,632 158,714!h; w.8 150,584 344,672", 40, 40)
G('þ', "0,D 0,C-6!14; 0,384@.72 ~0,xo 204,xo ~398,xo 398,260 ~398,bo 204,bo ~0,bo 0,146@.72", 70, 40)
G('ª', "use:a|0.62,0.62,0,C-330", 40, 40)
G('º', "use:o|0.62,0.62,0,C-330", 40, 40)

# ---- Latin-1 punctuation and symbols --------------------------------------
G('¡', "use:exclam|1,-1,0,X", 92, 92)
G('¿', "use:question|-1,-1,378,X", 44, 44)
G('¢', "use:c; w.8 196,-104 196,X+104", tab=True)
G('£', "366,548 ~366,co 246,co ~120,co 120,548 120,b; -6,b 398,b; 14,352 300,352", tab=True)
G('¥', "use:Y|0.76,1,0,0; w.85 50,300 376,300; w.85 50,160 376,160", tab=True)
G('¤', "w.8 ring 200,350 132,132; w.8 26,176 98,248; w.8 374,176 302,248; w.8 26,524 98,452; w.8 374,524 302,452", 50, 50)
G('¦', "0,D 0,170; 0,330 0,C+50", 88, 88)
G('§', "352,560 ~352,C-28 190,C-28 ~30,C-28 30,560 ~30,470 190,430;"
       "z 190,430 ~380,380 380,290 ~380,205 190,160 ~0,205 0,290 ~0,380;"
       "190,160 ~350,115 350,30 ~350,-70 190,-70 ~30,-70 30,30", 50, 50)
G('©', "w.62 ring 370,350 345,355; use:C|0.5,0.5,232,175", 40, 40)
G('®', "w.62 ring 370,350 345,355; use:R|0.5,0.5,248,175", 40, 40)
G(0x2117, "w.62 ring 370,350 345,355; use:P|0.5,0.5,258,175", 40, 40)
G('™', "use:T|0.42,0.42,0,406; use:M|0.42,0.42,290,406", 30, 40)
G(0x2120, "use:S|0.42,0.42,0,406; use:M|0.42,0.42,270,406", 30, 40)
G(0x2039, "w.9 176,432 0,264 176,96", 50, 50)
G(0x203A, "w.9 0,432 176,264 0,96", 50, 50)
G('«', "w.9 176,432 0,264 176,96; w.9 376,432 200,264 376,96", 50, 50)
G('»', "w.9 0,432 176,264 0,96; w.9 200,432 376,264 200,96", 50, 50)
G('¬', "0,350 424,350 424,170", 62, 62)
G('°', "w.75 ring 112,C-124 102,104", 40, 40)
G('±', "0,430 424,430; 212,250 212,610; 0,108 424,108", 62, 62)
G('¹', "use:one|0.6,0.6,0,C-420", 20, 40)
G('²', "use:two|0.6,0.6,0,C-420", 40, 40)
G('³', "use:three|0.6,0.6,0,C-420", 40, 40)
G('¶', "f 306,C ~70,C 70,516 ~70,336 306,336; w.8 306,-130 306,C-20; w.8 450,-130 450,c; w.8 300,c+2 500,c+2", 40, 50)
G('·', "dot 0,264", 84, 84, also=[0x2219, 0x22C5])
G('×', "20,160 404,544; 20,544 404,160", 62, 62)
G('÷', "0,350 424,350; dot 212,560 .9; dot 212,140 .9", 62, 62)
G('¼', "use:one|0.56,0.56,0,308; w.8 170,-12!h 560,C+12!h; use:four|0.56,0.56,470,0", 30, 30)
G('½', "use:one|0.56,0.56,0,308; w.8 170,-12!h 560,C+12!h; use:two|0.56,0.56,490,0", 30, 30)
G('¾', "use:three|0.56,0.56,0,308; w.8 230,-12!h 620,C+12!h; use:four|0.56,0.56,530,0", 30, 30)
for _cp, _a, _b in [(0x2153, 'one', 'three'), (0x2154, 'two', 'three'), (0x2155, 'one', 'five'), (0x215B, 'one', 'eight'),
                    (0x215C, 'three', 'eight'), (0x215D, 'five', 'eight'), (0x215E, 'seven', 'eight')]:
    G(_cp, f"use:{_a}|0.56,0.56,0,308; w.8 170,-12!h 560,C+12!h; use:{_b}|0.56,0.56,480,0", 30, 30)
G(0x2044, "w.8 -110,-12!h 280,C+12!h", -100, -100, also=[0x2215])

# ---- general punctuation --------------------------------------------------
G(0x2010, "0,264 252,264", 40, 40, also=[0x2011, 0xAD])
G(0x2013, "0,264 500,264", 0, 0, also=[0x2012])
G(0x2014, "0,264 1000,264", 0, 0, also=[0x2015])
G(0x2212, "0,350 424,350", 62, 62)
G(0x2016, "0,D 0,C+50; 190,D 190,C+50", 88, 88)
G(0x2017, "0,-112 560,-112; 0,-260 560,-260", 0, 0)
G(0x2019, "use:comma|1,1,0,C-2*dt", 70, 70, also=[0x2BC])
G(0x2018, "use:comma|-1,-1,0,C-1.7*dt", 70, 70)
G(0x201A, "use:comma", 70, 70)
G(0x201B, "use:comma|-1,1,0,C-2*dt", 70, 70)
G(0x201D, "use:comma|1,1,0,C-2*dt; use:comma|1,1,3.6*dt,C-2*dt", 70, 70)
G(0x201C, "use:comma|-1,-1,0,C-1.7*dt; use:comma|-1,-1,3.6*dt,C-1.7*dt", 70, 70)
G(0x201E, "use:comma; use:comma|1,1,3.6*dt,0", 70, 70)
G(0x2020, "190,-150 190,C; 20,500 360,500", 50, 50)
G(0x2021, "190,-150 190,C; 20,500 360,500; 20,50 360,50", 50, 50)
G(0x2022, "oval 0,350 122,122", 80, 80)
G(0x2023, "f 0,490 250,350 0,210", 80, 60)
G(0x25E6, "w.7 ring 0,350 110,110", 80, 80)
G(0x2026, "dot 0,dt; dot 333,dt; dot 666,dt", 84, 84)
G(0x2025, "dot 0,dt; dot 333,dt", 84, 84)
G(0x2024, "dot 0,dt", 84, 84)
G(0x2027, "dot 0,264", 84, 84)
G(0x2030, "w.85 ring 128,524 104,152; w.85 ring 566,176 104,152; w.85 ring 836,176 104,152; w.9 176,-12!h 518,C+12!h", 40, 40)
G(0x2032, "w.9 60,C 0,C-236", 52, 52)
G(0x2033, "w.9 60,C 0,C-236; w.9 220,C 160,C-236", 52, 52)
G(0x2034, "w.9 60,C 0,C-236; w.9 220,C 160,C-236; w.9 380,C 320,C-236", 52, 52)
G(0x203C, "0,C 0,222; dot 0,dt; 230,C 230,222; dot 230,dt", 92, 92)
G(0x203E, "0,C+90 560,C+90", 0, 0)
G(0x2047, "use:question; use:question|1,1,440,0", 44, 44)
G(0x2048, "use:question; 540,C 540,222; dot 540,dt", 44, 92)
G(0x2049, "0,C 0,222; dot 0,dt; use:question|1,1,150,0", 92, 44)
G(0x203D, "use:question; 190,C-60 190,214", 44, 44)
G(0x2052, "w.9 0,-12!h 300,C+12!h; dot 20,C-140 .9; dot 280,140 .9", 40, 40)
G(0x203B, "w.85 20,90 520,590; w.85 20,590 520,90; dot 270,590 .8; dot 270,90 .8; dot 20,340 .8; dot 520,340 .8", 50, 50)


def _blank(width):
    def fn(st, d):
        if d.uni and d.uni[0] == 0xA0 and not st.mono:        # the no-break space is as wide as the space
            return GlyphOut(d.name, d.uni, [], round(width * getattr(st, 'spacef', 1.0) + st.sba))
        return GlyphOut(d.name, d.uni, [], MONO_W if (st.mono and width) else width)
    return fn


for cp, w in [(0xA0, 278), (0x2002, 500), (0x2003, 1000), (0x2004, 333), (0x2005, 250), (0x2006, 167),
              (0x2007, 556), (0x2008, 278), (0x2009, 200), (0x200A, 100), (0x202F, 200), (0x205F, 222),
              (0x2000, 500), (0x2001, 1000), (0x3000, 1000)]:
    G(cp, None, fn=_blank(w))
G('zerowidth', None, fn=_blank(0), cat='none',
  uni=[0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2060, 0x2061,
       0x2062, 0x2063, 0x2064, 0x2066, 0x2067, 0x2068, 0x2069, 0xFEFF, 0x61C, 0x34F])

# ---- super / subscripts ---------------------------------------------------
_DN = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
for i, n in enumerate(_DN):
    if i not in (1, 2, 3):
        G(0x2070 + i, f"use:{n}|0.6,0.6,0,C-420", 40, 40)
    G(0x2080 + i, f"use:{n}|0.6,0.6,0,-140", 40, 40)
for cp, n, sc in [(0x207A, 'plus', .6), (0x207B, 'uni2212', .6), (0x207C, 'equal', .6), (0x207D, 'parenleft', .6),
                  (0x207E, 'parenright', .6), (0x207F, 'n', .66), (0x2071, 'i', .66)]:
    G(cp, f"use:{n}|{sc},{sc},0,C-{round(700*sc if n in ('parenleft','parenright') else (520*sc if len(n)==1 else 500*sc))}", 40, 40)
    if cp < 0x207F:
        G(cp + 0x10, f"use:{n}|{sc},{sc},0,-140", 40, 40)
for cp, n in [(0x2090, 'a'), (0x2091, 'e'), (0x2092, 'o'), (0x2093, 'x'), (0x2095, 'h'), (0x2096, 'k'),
              (0x2097, 'l'), (0x2098, 'm'), (0x2099, 'n'), (0x209A, 'p'), (0x209B, 's'), (0x209C, 't')]:
    G(cp, f"use:{n}|0.66,0.66,0,-140", 40, 40)

# ---- combining marks (drawn for lower case; _top at x-height) --------------
T = {'_top': (0, 'X'), 'top': (0, 'X+250')}
Bm = {'_bottom': (0, 0), 'bottom': (0, -230)}
MARKS = {}


def M(cp, spec, anchors, sp=None, **kw):
    d = G(cp, spec, 0, 0, cat='mark', anchors=anchors, **kw)
    MARKS[cp] = d.name
    if sp:
        G(sp if isinstance(sp, int) else ord(sp), None, comp=('accentbase', [d.name]), also=kw.get('sp_also'))
    return d


G('accentbase', None, fn=lambda st, d: _accentbase(st, d), cat='none')


def _accentbase(st, d):
    adv = MONO_W if st.mono else 340
    g = GlyphOut(d.name, [], [], adv)
    sk = st.skew
    g.anchors = {'top': sk(adv / 2, 520), 'bottom': sk(adv / 2, 0), 'ogonek': sk(adv / 2, 0)}
    return g


M(0x300, "w.85 -82,X+212 34,X+84", T, '`')
M(0x301, "w.85 82,X+212 -34,X+84", T, '´')
M(0x302, "w.8 -116,X+84 0,X+200 116,X+84", T, 0x2C6)
M(0x303, "w.8 -128,X+104 ~-62,X+218 0,X+142 ~62,X+66 128,X+180", T, 0x2DC)
M(0x304, "w.85 -112,X+138 112,X+138", T, '¯')
M(0x306, "w.8 -106,X+204 ~-106,X+92 0,X+92 ~106,X+92 106,X+204", T, 0x2D8)
M(0x307, "dot 0,C-dt .92", T, 0x2D9)
M(0x308, "dot -90,C-dt .86; dot 90,C-dt .86", T, '¨')
M(0x309, "w.7 -48,X+178 ~-48,X+222 4,X+222 ~56,X+222 56,X+180 ~56,X+138 4,X+128 4,X+86", T)
M(0x30A, "w.7 ring 0,X+150 62,62", T, 0x2DA)
M(0x30B, "w.8 -18,X+212 -98,X+84; w.8 128,X+212 48,X+84", T, 0x2DD)
M(0x30C, "w.8 -116,X+200 0,X+84 116,X+200", T, 0x2C7)
M(0x30F, "w.8 18,X+84 98,X+212; w.8 -128,X+212 -48,X+84", T)
M(0x311, "w.8 -106,X+92 ~-106,X+204 0,X+204 ~106,X+204 106,X+92", T)
M(0x312, "use:comma|-0.85,-0.85,0,X+120", T)
M(0x313, "use:comma|0.85,0.85,0,X+110", T)
M(0x31B, "w.7 -6,-34 ~62,-22 62,62", {'_horn': (0, 0)})
M(0x323, "dot 0,-72-dt .92", Bm)
M(0x324, "dot -90,-72-dt .86; dot 90,-72-dt .86", Bm)
M(0x326, "use:comma|0.85,0.85,0,-70-2*dt*0.85", Bm)
M(0x327, "w.7 10,6 -6,-66; w.7 -16,-66 20,-66 ~76,-66 76,-120 ~76,-176 14,-176 -52,-176", {'_bottom': (0, 0)}, '¸')
M(0x328, "w.7 0,12 ~-74,-58 -74,-112 ~-74,-172 -12,-172 32,-172", {'_ogonek': (0, 0)}, 0x2DB)
M(0x331, "w.85 -112,-118 112,-118", Bm)
M(0x32E, "w.8 -106,-70 ~-106,-182 0,-182 ~106,-182 106,-70", Bm)
M(0x32D, "w.8 -116,-196 0,-80 116,-196", Bm)
M(0x330, "w.8 -128,-180 ~-62,-66 0,-142 ~62,-218 128,-104", Bm)
G('caronalt', "w.9 40,C 0,C-200", 0, 0, cat='mark', anchors={'_topright': (0, 'C')})

# anchors on bases that need them
_OG = {'a': 338, 'e': 300, 'i': 0, 'u': 336, 'A': 540, 'E': 430, 'I': 0, 'U': 330, 'o': 250, 'O': 360,
       'dotlessi': 0}
for k, x in _OG.items():
    d = REG[k]
    d.anchors = dict(d.anchors or {}, ogonek=(x, 0))
for k, (x, y) in {'o': (372, 'X-60'), 'u': (336, 'X-30'), 'O': (552, 'C-80'), 'U': (472, 'C-30')}.items():
    d = REG[k]
    d.anchors = dict(d.anchors or {}, horn=(x, y))
for k, x in {'d': 398 + 150, 'l': 190, 't': 250, 'L': 220}.items():
    d = REG[k]
    d.anchors = dict(d.anchors or {}, topright=(x, 'C'))

# ---- precomposed letters via canonical decomposition ----------------------
_LATVIAN = {0x122, 0x136, 0x137, 0x13B, 0x13C, 0x145, 0x146, 0x156, 0x157}
_CARON_ALT = {0x10F, 0x13D, 0x13E, 0x165}
_SOFT = {'i': 'dotlessi', 'j': 'uni0237'}
_ABOVE = {0x300, 0x301, 0x302, 0x303, 0x304, 0x306, 0x307, 0x308, 0x309, 0x30A, 0x30B, 0x30C, 0x30F, 0x311,
          0x312, 0x313}


def _compose(cp):
    dec = ud.normalize('NFD', chr(cp))
    if len(dec) < 2:
        return False
    base = gname(ord(dec[0]))
    marks = [ord(c) for c in dec[1:]]
    if base not in REG or REG[base].comp:
        return False
    if cp in _LATVIAN:
        marks = [0x326]
    if cp == 0x123:
        marks = [0x312]
    if cp in _CARON_ALT:
        G(cp, None, comp=(base, ['caronalt']))
        return True
    if any(m not in MARKS for m in marks):
        return False
    if dec[0] in _SOFT and any(m in _ABOVE for m in marks):
        base = _SOFT[dec[0]]
    # canonical order puts below marks first; keep that
    G(cp, None, comp=(base, [MARKS[m] for m in marks]))
    return True


for _cp in list(range(0xC0, 0x250)) + list(range(0x1E00, 0x1F00)):
    if gname(_cp) not in REG and ud.category(chr(_cp)).startswith('L'):
        _compose(_cp)

# ---- modifier letters used in transliteration of Arabic and Hebrew (ʿ ʾ ʻ ʹ ʺ ˈ) ----
G(0x2BF, "w.8 150,C+10 ~10,C+10 10,C-95 ~10,C-200 150,C-200", 60, 50)          # left half ring: ʿayn
G(0x2BE, "w.8 10,C+10 ~150,C+10 150,C-95 ~150,C-200 10,C-200", 50, 60)          # right half ring: hamza
G(0x2BB, "use:comma|-1,-1,0,C-1.7*dt", 70, 70)
G(0x2B9, "w.9 70,C 0,C-200", 60, 60)
G(0x2BA, "w.9 70,C 0,C-200; w.9 220,C 150,C-200", 60, 60)
G(0x2C8, "w.9 0,C 0,C-200", 70, 70)
