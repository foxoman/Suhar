"""Hebrew (unpointed), polytonic Greek, Serbian/Macedonian and Kazakh Cyrillic."""
from .model import G, REG, gname
from . import latin_ext as LX
from .greek_cyrillic import small, same

# ---- polytonic Greek ------------------------------------------------------
LX.M(0x314, "use:comma|-0.85,0.85,0,X+110", LX.T)
LX.M(0x342, "w.8 -128,X+104 ~-62,X+218 0,X+142 ~62,X+66 128,X+180", LX.T)
LX.M(0x345, "w.6 0,-52 0,-150 ~0,-192 44,-192", LX.Bm)
for _cp in range(0x1F00, 0x2000):
    if gname(_cp) not in REG:
        LX._compose(_cp)

# ---- Serbian / Macedonian -------------------------------------------------
_B2 = "~{x},374 {x},(b+374)/2 ~{x},b"
G(0x409, "use:uni041B; 480,374 620,374 ~800,374 800,(b+374)/2 ~800,b 620,b 480,b", 20, 36)
G(0x40A, "0,0 0,C; 0,366 440,366; 440,C 440,b 600,b ~790,b 790,(b+374)/2 ~790,374 600,374 440,374", 78, 36)
G(0x40F, "0,C 0,b 472,b 472,C; 236,b 236,-124", 78, 78)
G(0x40B, "0,c 430,c; 150,c 150,0; 150,330@.8 ~150,440 300,440 ~470,440 470,300 470,0", 20, 76)
G(0x402, "0,c 430,c; 150,c 150,0; 150,330@.8 ~150,440 300,440 ~470,440 470,300 470,90 ~470,-60 380,-60 330,-60", 20, 60)
for cp, cap in [(0x459, 0x409), (0x45A, 0x40A), (0x45F, 0x40F)]:
    small(cp, cap)
same(0x45B, 'hbar')
G(0x452, "0,0 0,C-6!14; w.85 -64,612 160,612; 0,364@.72 ~0,xo 178,xo ~336,xo 336,336 336,-78 ~336,d 252,d 212,d", 14, 68)
for _cp in (0x403, 0x40C, 0x453, 0x45C, 0x400, 0x40D, 0x450, 0x45D):
    if gname(_cp) not in REG:
        LX._compose(_cp)
# ---- Kazakh ---------------------------------------------------------------
same(0x4D8, 'uni018F'); same(0x4D9, 'uni0259')
G(0x492, "use:uni0393; w.85 -64,366 240,366", 30, 20)
G(0x49A, "use:K; 496,b 566,b 566,-124", 78, 20)
G(0x4A2, "use:H; 472,b 546,b 546,-124", 78, 20)
same(0x4E8, 'uni0398')
same(0x4AE, 'Y')
G(0x4B0, "use:Y; w.85 130,230 430,230", 4, 4)
G(0x4BA, "0,0 0,C; 0,300@.8 ~0,420 200,420 ~440,420 440,280 440,0", 78, 76)
for cp, cap in [(0x493, 0x492), (0x49B, 0x49A), (0x4A3, 0x4A2)]:
    small(cp, cap)
G(0x4E9, "use:o; w.9 0,260 396,260", 40, 40)
G(0x4AF, "0,X!h 215,-6; 430,X!h 215,-6; 215,0 215,D", 6, 6)
G(0x4B1, "0,X!h 215,-6; 430,X!h 215,-6; 215,0 215,D; w.85 80,-60 350,-60", 6, 6)
same(0x4BB, 'h')

# ---- Hebrew (letters only, no niqqud) -------------------------------------
# Horizontal strokes are the heavy ones in Hebrew, so the pen is turned round.
T, B = "(570-1.14*hb)", "(1.14*hb)"
HP = dict(pen=(0.86, 1.14), script='hebr', slant=True, top='X')


def H(cp, spec, l=50, r=50):
    G(cp, spec.replace('T', T).replace('B', B), l, r, **HP)


H(0x5D0, "40,570!h 390,0!h; 390,570 390,470 ~390,360 290,330; 50,0 50,150 ~50,250 150,270")
H(0x5D1, "20,T 300,T ~370,T 370,T-80 370,B; 0,B 440,B")
H(0x5D2, "90,T 220,T ~290,T 290,T-70 290,0; 290,190 80,0!h")
H(0x5D3, "0,T 410,T; 330,T 330,0")
H(0x5D4, "0,T 320,T ~390,T 390,T-80 390,0; 50,360 50,0")
H(0x5D5, "20,T 90,T ~150,T 150,T-70 150,0")
H(0x5D6, "0,T 270,T; 150,T ~110,300 130,0")
H(0x5D7, "40,0 40,T 320,T ~390,T 390,T-80 390,0")
H(0x5D8, "40,570 40,110 ~40,B 150,B 290,B ~400,B 400,110 400,420 ~400,T 300,T ~210,T 210,440")
H(0x5D9, "20,T 90,T ~150,T 150,T-70 150,330")
H(0x5DA, "20,T 250,T ~330,T 330,T-80 330,D")
H(0x5DB, "20,T 270,T ~390,T 390,T-120 390,120 ~390,B 270,B 20,B")
H(0x5DC, "50,760 50,T 290,T ~390,T 390,440 ~390,180 170,0!h")
H(0x5DD, "z 40,B 40,T 320,T ~390,T 390,T-80 390,B")
H(0x5DE, "120,0!h 50,570!h; 70,500 ~140,T 250,T ~390,T 390,T-130 390,B 200,B")
H(0x5DF, "30,T 100,T ~160,T 160,T-70 160,D")
H(0x5E0, "110,T 200,T ~270,T 270,T-70 270,B 50,B")
H(0x5E1, "z 40,T 330,T ~400,T 400,300 ~400,B 215,B ~40,B 40,300")
H(0x5E2, "90,570 150,130; 380,570 380,280 ~380,B 220,B 0,B")
H(0x5E3, "30,T 250,T ~330,T 330,T-80 330,D; 60,T 60,340 190,340")
H(0x5E4, "20,T 270,T ~390,T 390,T-120 390,120 ~390,B 270,B 20,B; 60,T 60,340 200,340")
H(0x5E5, "210,D 210,280; 40,570 210,290; 380,570 380,430 ~380,290 210,280")
H(0x5E6, "40,570!h 350,B; 380,570 380,440 ~380,320 250,300; 0,B 410,B")
H(0x5E7, "20,T 290,T ~390,T 390,T-110 ~390,230 240,130; 60,380 60,D")
H(0x5E8, "0,T 290,T ~370,T 370,T-80 370,0")
H(0x5E9, "30,570 30,130 ~30,B 150,B 290,B ~410,B 410,130 410,570; 220,570 220,330 ~220,230 120,200")
H(0x5EA, "40,T 310,T ~390,T 390,T-80 390,0; 110,T 110,90 ~110,B 50,B 0,B")
G(0x5BE, "0,T 250,T".replace('T', T), 40, 40, **HP)
G(0x5F3, "w.9 60,570 0,400", 52, 52, **HP)
G(0x5F4, "w.9 60,570 0,400; w.9 220,570 160,400", 52, 52, **HP)


# accented letters follow their base into stylistic set 1
for _n, _d in list(REG.items()):
    if _d.comp and _d.comp[0] in ('y', 'g', 'Q', 'J') and not _n.endswith('.ss01'):
        G(_n + '.ss01', None, comp=(_d.comp[0] + '.ss01', _d.comp[1]))

from .latin import SMALLCAPS
for _n, _d in list(REG.items()):
    if _d.comp and _d.comp[0] in SMALLCAPS and '.' not in _n:
        G(_n + '.sc', None, comp=(SMALLCAPS[_d.comp[0]], _d.comp[1]))
        SMALLCAPS[_n] = _n + '.sc'


# ---- Hebrew points (niqqud).  Below-marks hang from the default bottom anchor; dagesh, holam and the
# shin/sin dots use anchors computed from each letter's width. ----
_HB = {'_bottom': (0, 0), 'bottom': (0, -260)}
for _cp, _sp in ((0x5B0, "dot 0,-85 .62; dot 0,-185 .62"), (0x5B4, "dot 0,-95 .62"), (0x5B5, "dot -62,-95 .62; dot 62,-95 .62"),
                 (0x5B6, "dot -62,-85 .62; dot 62,-85 .62; dot 0,-185 .62"), (0x5B7, "w.62 -95,-95 95,-95"),
                 (0x5B8, "w.62 -95,-75 95,-75; w.62 0,-75 0,-185"), (0x5C7, "w.62 -95,-75 95,-75; w.62 0,-75 0,-185"),
                 (0x5BB, "dot -85,-75 .62; dot 0,-135 .62; dot 85,-195 .62"), (0x5BD, "w.55 0,-65 0,-195"),
                 (0x5B1, "dot -150,-85 .58; dot -40,-85 .58; dot -95,-180 .58; dot 110,-85 .58; dot 110,-180 .58"),
                 (0x5B2, "w.58 -160,-95 -20,-95; dot 110,-85 .58; dot 110,-180 .58"),
                 (0x5B3, "w.58 -160,-75 -20,-75; w.58 -90,-75 -90,-180; dot 110,-85 .58; dot 110,-180 .58")):
    LX.M(_cp, _sp, _HB, script='hebr')
LX.M(0x5BC, "dot 0,0 .6", {'_hdagesh': (0, 0)}, script='hebr')
LX.M(0x5B9, "dot 0,0 .62", {'_hholam': (0, 0)}, script='hebr')
LX.M(0x5C1, "dot 0,0 .62", {'_hshin': (0, 0)}, script='hebr')
LX.M(0x5C2, "dot 0,0 .62", {'_hholam': (0, 0)}, script='hebr')
import re as _re
for _cp in range(0x5D0, 0x5EB):
    _d = REG.get('uni%04X' % _cp)
    if _d is None or not _d.spec:
        continue
    _xs = [float(m) for m in _re.findall(r'(?:^|[ ~;])(-?\d+(?:\.\d+)?),', _d.spec)]
    _w = max(_xs) if _xs else 400
    _dx = {0x5D5: 60, 0x5D9: 60, 0x5DF: 60, 0x5D6: 40}.get(_cp, _w * 0.48)        # narrow letters carry the dagesh to the left
    _d.anchors = dict(_d.anchors or {}, hdagesh=(_dx if _cp not in (0x5D5, 0x5D9, 0x5DF, 0x5D6) else -60, 290),
                      hholam=(10, 665), hshin=(_w - 10, 665))
