"""Suhar Sahafa: a newspaper Naskh with a serif Latin, in two cuts (Text and Headline).

Proportions (font units, after the Arabic scale of 1.28):
    alef 715 = Latin cap height | loops 470 = Latin x-height | teeth about 375 | bowls to about -250
Pen: long axis at 62 degrees, ratio 1.6 : 1 (Suhar Naskh has 2.6 : 1), so the thin strokes stay sturdy on newsprint.
The Latin stem is as thick as the Arabic baseline stroke in every weight.

ARABIC holds the letters drawn for this family; every other letter is the Suhar Naskh skeleton put through `_armap`.
LATIN holds the redrawn Latin letters and SERIF the serifs added to the shared skeletons.
`python -m retrofont.sahafa OUT.ttf [weight] [text|headline]` compiles one unhinted test font.
"""
import math
from . import engine as E
from .model import Style, lerp

LT = 331          # centre line of a loop top   (final: 331 * 1.28 + k = about 470)
AH = 547          # alef height                 (final 700)
TH = 282          # tooth height
SH = 218          # tooth height of seen and sheen: clearly lower, so that سـ and ببـ are different words
DB = -140         # centre line of a bowl bottom
LATIN_X = 470     # x-height of the serif Latin

_bowl = f"~{{x}},{DB} {{m}},{DB} ~-12,{DB} -12,15 ~-12,105 30,165"          # round bowl, the end curls in
# the loop of ص: full and high on the right where the pen starts, narrowing towards the tooth on the left
_sloop = ("z {c}+40,%d ~{l}+30,%d-28 {l},(%d+k)/2-14 ~{l},k {l}+150,k {r}-95,k ~{r},k {r},k+96 ~{r}-30,%d {c}+40,%d" % (LT, LT, LT, LT, LT))


def _sl(l, r):
    return _sloop.format(l=l, r=r, c=l + 185)


def _loop(cx, w, y0, y1):
    a, b = cx - w / 2, cx + w / 2
    return f"z {cx},{y1} ~{a},{y1} {a},({y0}+{y1})/2 ~{a},{y0} {cx},{y0} ~{b},{y0} {b},({y0}+{y1})/2 ~{b},{y1}"


_jh = "25,222 ~70,304 180,294 430,262!r"                       # head of ح: a short rise, then a long flat sweep
_jb = "425,262 ~70,222 22,20 ~0,-165 232,-165 ~400,-165 505,-92"   # its bowl, left open towards the next word

def _teeth(x):
    """the first two teeth of seen: leaning strokes that bend into a round cup"""
    return (f"{446 + x},{SH + 6} ~{446 + x},140 {428 + x},92 ~{404 + x},k {366 + x},k ~{296 + x},k {296 + x},112 {296 + x},{SH}; "
            f"{296 + x},{SH} ~{296 + x},140 {280 + x},92 ~{258 + x},k {218 + x},k ~{146 + x},k {146 + x},112 {146 + x},{SH}")


def _kafi(x, bowl=False):
    """kaf joined forward (and the Persian kaf): a pointed arm, then the body"""
    body = (f"~{x + 292},k {x + 198},k 110,k ~-12,k -12,105 ~-12,170 26,214" if bowl else f"~{x + 292},k {x + 198},k 0,k")
    return f"{x + 300},{AH - 4} ~{x + 176},{AH - 56} {x + 72},362!r; {x + 72},362 ~{x + 292},286 {x + 292},146 " + body


_kafb = (f"500,{AH} 500,130 ~500,k 400,k 110,k ~-12,k -12,105 ~-12,170 26,214; w.62 334,318 ~334,360 272,360 ~198,360 198,294 "
         "~198,230 266,230 340,230!r; w.62 335,230 192,166")
_hdo = "z 335,384 ~70,370 45,186 ~35,k 175,k ~335,k 335,176; w.72 80,292 ~235,276 318,100"

ARABIC = {
    # ص: a long, high loop, a tooth, then the join or the bowl
    'sad.init': dict(spec=_sl(215, 650) + "; 225,k 118,k; 118,225 ~118,120 105,85 ~90,k 50,k 0,k", dx=435 - 475, dy=LT - 262),
    'sad.medi': dict(spec=_sl(215, 650) + "; 225,k 118,k; 118,225 ~118,120 105,85 ~90,k 50,k 0,k; 742,k 640,k", aw=742, dx=435 - 475, dy=LT - 262),
    'sad.isol': dict(spec=_sl(430, 865) + "; 440,k 340,k; 340,225 340,25 " + _bowl.format(x=340, m=165), dx=650 - 655, dy=LT - 262),
    'sad.fina': dict(spec=_sl(430, 865) + "; 440,k 340,k; 340,225 340,25 " + _bowl.format(x=340, m=165) + "; 957,k 855,k", aw=957, dx=650 - 655, dy=LT - 262),
    # ح: open head; when it joins forward the stroke falls back to the line in one curve
    'jeem.init': dict(spec="30,212 ~72,298 172,290 398,260!r; 393,260@1.22 ~310,150 170,k+18@1.15 ~95,k 0,k", dy=-30),
    'jeem.medi': dict(spec="490,k 0,k; 472,k+8@1.1 ~474,262 336,322 ~196,380 30,304!r", aw=490, dx=10, dy=8),
    'jeem.isol': dict(spec=_jh + "; " + _jb, dy=-28, bdy=28),
    'jeem.fina': dict(spec=_jh + "; " + _jb + "; 522,k 30,k", aw=522, dy=-28, bdy=28),
    # ي (and the other toothed letters): the tooth leans and bends into the join
    'beh.init': dict(spec=f"168,{TH + 34} ~168,128 152,88 ~132,k 72,k 0,k", dy=4),
    'behr.init': dict(spec=f"140,{TH + 34} ~140,128 126,88 ~108,k 60,k 0,k", dy=4),
    'behr.medi': dict(spec=f"108,{TH - 18} ~108,128 96,88 ~80,k 42,k 0,k; 215,k 85,k", aw=215, dy=-40),
    'rehr.fina': dict(spec=f"258,k 238,k ~212,k 204,-18 ~178,{DB - 2} 30,{DB - 14} -58,{DB + 4}", aw=258, dx=6, dy=0),
    'beh.medi': dict(spec=f"128,{TH - 8} ~128,128 114,88 ~96,k 52,k 0,k; 252,k 100,k", aw=252, dy=-38),
    'yeh.fina': dict(spec="472,k 432,k ~378,k 378,0 ~378,-72 190,-72 ~-22,-72 -22,18 ~-22,98 24,150", aw=472, dy=-17, bdy=-14),
    'yeh.isol': dict(spec="500,212 ~500,298 420,298 ~336,298 336,214 ~336,132 396,82 ~442,46 442,4 ~442,-72 220,-72 ~-22,-72 -22,18 ~-22,98 24,150", dy=-17, bdy=-14),
    # ف: a round, open loop standing on the line
    'feh.init': dict(spec=_loop(190, 275, 'k', LT) + "; 190,k 0,k", dx=15, dy=LT - 262 - 46),
    'feh.medi': dict(spec=_loop(195, 275, 'k', LT) + "; 372,k 0,k", aw=372, dx=20, dy=LT - 262 - 46),
    'feh.isol': dict(spec=_loop(475, 275, 'k', LT) + "; 475,k 110,k ~-6,k -6,105 ~-6,190 30,246", dx=20, dy=LT - 262 - 46),
    'feh.fina': dict(spec=_loop(475, 275, 'k', LT) + "; 475,k 110,k ~-6,k -6,105 ~-6,190 30,246; 680,k 605,k", aw=680, dx=20, dy=LT - 262 - 46),
    # ه ة
    'heh.isol': dict(spec="z 232,352 ~22,300 22,166 ~22,k 170,k ~322,k 322,180 ~316,290 232,352", dx=38, dy=50),
    'heh.fina': dict(spec="z 176,338 ~18,262 18,150 ~18,k 136,k ~262,k 262,160 ~256,262 176,338; 348,k 242,k", aw=348, dx=24, dy=318 + 46 - (2 * 46 + 235)),
    'heh.init': dict(spec="z 322,362 ~76,352 50,186 ~40,k 176,k ~322,k 322,176; w.72 86,282 ~226,266 306,100; 176,k 0,k", dy=-55),
    'heh.medi': dict(spec="342,k 0,k; z ~44,304 ~298,304 ~171,k-118; z ~40,-152 ~302,-152 ~171,k+92", aw=342, dy=-60),
    # م: an open loop; the tail falls straight
    'meem.init': dict(spec=_loop(236, 236, -38, 214) + "; 150,k 0,k", dy=0),
    'meem.medi': dict(spec=_loop(190, 234, -116, 'k+30') + "; 382,k 0,k", aw=382, dy=0),
    'meem.isol': dict(spec=_loop(236, 226, 'k', 242) + "; 240,k 100,k ~20,k 20,-52 20,-218", dy=0),
    'meem.fina': dict(spec=_loop(236, 226, 'k', 242) + "; 240,k 100,k ~20,k 20,-52 20,-218; 442,k 332,k", aw=442, dy=0),
    # ا ل
    'alef.isol': dict(spec=f"0,0 0,{AH}", dy=AH - 600),
    'alef.fina': dict(spec=f"152,k 82,k ~6,k 0,k+78 0,{AH}", aw=152, dy=AH - 600),
    'lam.init': dict(spec=f"150,{AH} 150,128 ~150,k 66,k 0,k", dy=AH - 600),
    'lam.medi': dict(spec=f"150,{AH} 150,128 ~150,k 66,k 0,k; 242,k 120,k", aw=242, dy=AH - 600),
    'lam.isol': dict(spec=f"330,{AH} 330,12 " + _bowl.format(x=330, m=160), dy=0),
    'lam.fina': dict(spec=f"330,{AH} 330,12 " + _bowl.format(x=330, m=160) + "; 422,k 330,k", aw=422, dy=0),
    # ط: the loop of ص with a stem on its left end
    'tah.init': dict(spec=_sl(55, 490) + f"; 88,k+34 88,{AH}; 150,k 0,k", dy=LT - 262, anch={'top': (88, AH + 6)}),
    'tah.medi': dict(spec=_sl(55, 490) + f"; 88,k+34 88,{AH}; 150,k 0,k; 580,k 470,k", aw=580, dy=LT - 262, anch={'top': (88, AH + 6)}),
    'tah.isol': dict(spec=_sl(35, 470) + f"; 68,k+34 68,{AH}", dy=LT - 262, anch={'top': (68, AH + 6)}),
    'tah.fina': dict(spec=_sl(35, 470) + f"; 68,k+34 68,{AH}; 560,k 450,k", aw=560, dy=LT - 262, anch={'top': (68, AH + 6)}),
    # ق و: the head as large as the other loops
    'qaf.isol': dict(spec=_loop(335, 262, 'k+26', LT) + f"; 466,188 466,-20 ~466,{DB} 230,{DB} ~-12,{DB} -12,15 ~-12,105 30,165", dx=5, dy=LT - 305),
    'qaf.fina': dict(spec=_loop(335, 262, 'k+26', LT) + f"; 466,188 466,-20 ~466,{DB} 230,{DB} ~-12,{DB} -12,15 ~-12,105 30,165; 592,k 452,k", aw=592, dx=5, dy=LT - 305),
    'waw.isol': dict(spec=_loop(160, 252, 'k+6', LT - 12) + f"; 286,176 286,20 ~286,{DB - 6} 86,{DB - 6} -22,{DB - 6}", dx=10, dy=LT - 12 - 290),
    'waw.fina': dict(spec=_loop(160, 252, 'k+6', LT - 12) + f"; 286,176 286,20 ~286,{DB - 6} 86,{DB - 6} -22,{DB - 6}; 376,k 256,k", aw=376, dx=10, dy=LT - 12 - 290),
    # ر ز: a short tail that sweeps under the line; د ذ: an open angle; ن: a wide, shallow bowl
    'reh.isol': dict(spec=f"190,268@1.1 ~236,150 206,36 ~172,{DB - 2} 30,{DB - 14} -58,{DB + 4}", dx=6, dy=0),
    'reh.fina': dict(spec=f"296,k 262,k ~214,k 204,-18 ~178,{DB - 2} 30,{DB - 14} -58,{DB + 4}", aw=296, dx=6, dy=0),
    'dal.isol': dict(spec="128,338 ~312,214 312,112 ~312,k 205,k 0,k", dx=4, dy=-10),
    'dal.fina': dict(spec="128,338 ~312,214 312,112 ~312,k 205,k 0,k; 392,k 205,k", aw=392, dx=4, dy=-10),
    'noon.isol': dict(spec=f"452,268 452,-24 ~452,{DB} 226,{DB} ~-12,{DB} -12,15 ~-12,105 30,165", dx=10, dy=0),
    'noon.fina': dict(spec=f"580,k 522,k ~452,k 452,-24 ~452,{DB} 226,{DB} ~-12,{DB} -12,15 ~-12,105 30,165", aw=580, dx=10, dy=0),
    # ع غ at the start of a word and alone: a wide, open head
    'ain.init': dict(spec="318,262 ~306,338 198,338 ~52,338 52,200 ~52,k 180,k; 318,k!r 0,k", dx=10, dy=-12),
    # لا: the lam upright, the alef leaning across it in one curve
    'lamalef.isol': dict(spec=f"322,{AH} 322,150 ~322,k 236,k ~152,k 130,140 ~92,330 -34,{AH + 4}", dy=AH - 600),
    'lamalef.fina': dict(spec=f"322,{AH} 322,150 ~322,k 236,k ~152,k 130,140 ~92,330 -34,{AH + 4}; 412,k 312,k", aw=412, dy=AH - 600),
    # ع in the middle and at the end of a word: a larger head, so that the counter stays open in small sizes
    'ain.medi': dict(spec="322,k 0,k; z 14,312 ~161,288 308,312 163,k+4", aw=322, dx=6, dy=27),
    'ain.fina': dict(spec="346,k 122,k; z 18,308 ~151,284 284,308 153,k+4; 156,k+20 ~0,10 0,-70 ~0,-172 200,-172 300,-172 ~372,-172 404,-126", aw=346, dx=6, dy=31),
    # ---- the rest of the alphabet, drawn in the Sahafa proportions ----
    'alefshort.isol': dict(spec="0,0 0,438", dy=-42),
    'alefshort.fina': dict(spec="150,k 70,k ~0,k 0,k+70 0,438", aw=150, dy=-42),
    'beh.isol': dict(spec=f"560,{TH - 12} 560,128 ~560,k 450,k 110,k ~-12,k -12,105 ~-12,170 26,214", dy=0),
    'beh.fina': dict(spec=f"560,{TH - 12} 560,128 ~560,k 450,k 110,k ~-12,k -12,105 ~-12,170 26,214; 640,k 450,k", aw=640, dy=0),
    'barree.isol': dict(spec="350,236 ~44,246 44,108 ~44,-18 210,-18 620,-18", dy=-8),
    'barree.fina': dict(spec="300,k 210,k ~40,k 40,-60 ~40,-150 210,-150 640,-150", aw=300, dy=0, bdy=15),
    'seen.init': dict(spec=_teeth(0) + f"; 146,{SH} ~146,120 132,84 ~114,k 70,k 0,k", dy=SH - 290 + 6),
    'seen.medi': dict(spec=_teeth(0) + f"; 146,{SH} ~146,120 132,84 ~114,k 70,k 0,k; 540,k 420,k", aw=540, dy=SH - 290 + 6),
    'seen.isol': dict(spec=_teeth(300) + f"; 446,{SH} 446,25 " + _bowl.format(x=446, m=218), dy=SH - 290 + 6, bdy=10),
    'seen.fina': dict(spec=_teeth(300) + f"; 446,{SH} 446,25 " + _bowl.format(x=446, m=218) + "; 840,k 690,k", aw=840, dy=SH - 290 + 6, bdy=10),
    'ain.isol': dict(spec="372,268 ~368,346 250,346 ~120,346 120,226 ~120,108 265,102 408,98!r; 403,98 ~30,68 12,-36 ~0,-176 240,-176 ~408,-176 498,-104", dy=-6, bdy=10),
    'kaf.isol': dict(spec=_kafb, dy=AH - 600),
    'kaf.fina': dict(spec=_kafb + "; 590,k 400,k", aw=590, dy=AH - 600),
    'kaf.init': dict(spec=_kafi(0), dy=AH - 600),
    'kaf.medi': dict(spec=_kafi(0) + "; 380,k 270,k", aw=380, dy=AH - 600),
    'keheh.isol': dict(spec=_kafi(300, True), dy=AH - 600),
    'keheh.fina': dict(spec=_kafi(300, True) + "; 690,k 500,k", aw=690, dy=AH - 600),
    'gaf.isol': dict(spec=_kafi(300, True) + f"; w.9 598,{AH + 118} 404,{AH - 36}", dy=AH - 600 - 5),
    'gaf.fina': dict(spec=_kafi(300, True) + f"; 690,k 500,k; w.9 598,{AH + 118} 404,{AH - 36}", aw=690, dy=AH - 600 - 5),
    'gaf.init': dict(spec=_kafi(0) + f"; w.9 298,{AH + 118} 104,{AH - 36}", dy=AH - 600 - 5),
    'gaf.medi': dict(spec=_kafi(0) + f"; 380,k 270,k; w.9 298,{AH + 118} 104,{AH - 36}", aw=380, dy=AH - 600 - 5),
    'swashkaf.isol': dict(spec="960,476!h 430,366!r; 430,366 ~850,330 850,146 ~850,k 740,k 110,k ~-12,k -12,105 ~-12,170 26,214", dy=-46),
    'swashkaf.fina': dict(spec="960,476!h 430,366!r; 430,366 ~850,330 850,146 ~850,k 740,k 110,k ~-12,k -12,105 ~-12,170 26,214; 950,k 740,k", aw=950, dy=-46),
    'swashkaf.init': dict(spec="640,476!h 75,366!r; 75,366 ~500,330 500,146 ~500,k 400,k 0,k", dy=-46),
    'swashkaf.medi': dict(spec="640,476!h 75,366!r; 75,366 ~500,330 500,146 ~500,k 400,k 0,k; 600,k 480,k", aw=600, dy=-46),
    'hehdo.isol': dict(spec=_hdo, dy=-36),
    'hehdo.init': dict(spec=_hdo + "; 175,k 0,k", dy=-36),
    'hehdo.medi': dict(spec=_hdo + "; 420,k 0,k", aw=420, dy=-36),
    'hehdo.fina': dict(spec=_hdo + "; 420,k 175,k", aw=420, dy=-36),
    'hehgoal.isol': dict(spec="z 160,316 ~14,316 14,176 ~14,k 160,k ~306,k 306,176 ~306,316", dy=16),
    'hehgoal.fina': dict(spec="300,k 220,k ~130,k 130,124 ~130,224 62,224 ~0,224 0,152 ~0,92 65,60", aw=300, dy=-11),
    'hehgoal.init': dict(spec="180,312 180,128 ~180,k 90,k 0,k; w.8 178,-50 ~178,-140 105,-140 58,-140", dy=-22, bdy=10),
    'hehgoal.medi': dict(spec="130,308 130,128 ~130,k 50,k 0,k; 250,k 100,k; w.8 128,-50 ~128,-140 55,-140 8,-140", aw=250, dy=-22, bdy=10),
    'hamza.isol': dict(spec="w.9 200,282 ~200,330 120,330 ~35,330 35,248 ~35,168 125,168 215,168!r; w.9 210,168 20,88", dy=-18),
    'tatweel.medi': dict(spec="250,k 0,k", aw=250, dy=0),
    'behtall.medi': dict(spec="130,402 ~130,128 116,88 ~98,k 52,k 0,k; 250,k 100,k", aw=250, dy=-28),
    'kafl.init': dict(spec=f"258,{AH - 4} ~151,{AH - 56} 62,362!r; 62,362 ~251,286 251,146 ~251,k 170,k 0,k", dy=AH - 600),
    'kafl.medi': dict(spec=f"258,{AH - 4} ~151,{AH - 56} 62,362!r; 62,362 ~251,286 251,146 ~251,k 170,k 0,k; 336,k 232,k", aw=336, dy=AH - 600),
    # other forms, offered as stylistic sets: the round ain, a curved alef, hah with a head and a return stroke
    'ainr.medi': dict(spec="322,k 0,k; z ~6,322 ~316,322 ~161,k-98", aw=322, dx=6, dy=27),
    'ainr.fina': dict(spec="346,k 122,k; z ~10,316 ~292,316 ~151,k-90; 156,k+20 ~0,10 0,-70 ~0,-172 200,-172 300,-172 ~372,-172 404,-126", aw=346, dx=6, dy=31, bdy=13),
    'alefc.isol': dict(spec=f"-30,-6 ~14,10 12,110 ~10,{AH - 130} -22,{AH}", dy=AH - 600),
    'alefc.fina': dict(spec=f"152,k 82,k ~8,k 8,k+86 ~8,{AH - 130} -22,{AH}", aw=152, dy=AH - 600),
    'jeemh.medi': dict(spec="455,k 0,k; 30,212 ~72,298 172,290 398,260!r; 393,260@1.22 ~300,140 150,k+12@1.15 60,k", aw=455, dy=-30),
    # a tooth standing on ج ح خ, and the ج ح خ it stands on
    'behj.init': dict(spec="180,462 180,340 ~180,256 90,256 0,256", dy=-30, bdy=-12),
    'jeemj.fina': dict(spec="522,256 425,256; " + _jh + "; " + _jb, aw=522, dy=-28, bdy=28),
    'jeemj.medi': dict(spec="460,256 372,256; 30,212 ~72,298 172,290 398,260!r; 393,260@1.22 ~310,150 170,k+18@1.15 ~95,k 0,k", aw=460, dy=-30),
}

# Latin: a sturdy serif.  b = half thickness of a horizontal; the top of the x-height is at 470.
_T, _B = "470-b+o", "b-o"
LATIN = {
    'n': f"0,0 0,470-b; 0,340@.8 ~0,{_T} 182,{_T} ~334,{_T} 334,330 334,0; -48-a,b 48+a,b; 334-48-a,b 334+48+a,b; -50-a,470-b 0,470-b; f -a+2,2*b -a-46,2*b ~-a-9,2*b+12 -a+2,2*b+60; f a-2,2*b a+46,2*b ~a+9,2*b+12 a-2,2*b+60; f 334-a+2,2*b 334-a-46,2*b ~334-a-9,2*b+12 334-a+2,2*b+60; f 334+a-2,2*b 334+a+46,2*b ~334+a+9,2*b+12 334+a-2,2*b+60; f -a+2,470-2*b -a-48,470-2*b ~-a-10,470-2*b-13 -a+2,470-2*b-63",
    'a': (f"336,0 336,300 ~336,{_T} 182,{_T} ~78,{_T} 40,372; oval 58,362 46,42; 336,272@.9 178,272 ~4,272 4,136 ~4,{_B} 160,{_B} "
          f"~336,{_B} 336,150@.72; 336,b 336+68+a,b"),
    'e': f"6,246 398,246 ~398,{_T} 204,{_T} ~4,{_T} 4,236 ~4,{_B} 212,{_B} ~338,{_B} 392,98",
    's': f"344,368@1.25 ~322,{_T} 190,{_T} ~32,{_T} 32,352 ~32,268 190,238 ~356,206 356,116 ~356,{_B} 186,{_B} ~46,{_B} 20,108@1.25",
    'g': (f"z 190,{_T} ~8,{_T} 8,246 ~8,22 190,22 ~372,22 372,246 ~372,{_T}; 372,470-b 372,-62 ~372,-205 192,-205 ~62,-205 26,-128; "
          f"372,470-b 372+50+a,470-b"),
    'w': "0,470-b 102,74 ~118,b-4 134,74 218,352 ~232,404 246,352 330,74 ~346,b-4 362,74 464,470-b; -26-a,470-b 26+a,470-b; 464-26-a,470-b 464+26+a,470-b",
}


# Serifs for the letters that keep the Suhar skeleton (coordinates of the skeleton, before the x-height is lowered).
# A serif reaches a fixed distance beyond the edge of the stem (half width a), so it survives in the bold weights.
def _h(x, l, r, y, br=True):
    a0 = f"{x}-{l - 38}-a" if l else f"{x}"
    a1 = f"{x}+{r - 38}+a" if r else f"{x}"
    s = f"{a0},{y} {a1},{y}"
    if br:                                                        # a curved bracket between serif and stem
        up = y == 'b'
        e, d = (f"{y}+b", '+') if up else (f"{y}-b", '-')
        for sg, n in (('-', l), ('+', r)):
            if n:
                w, h = round((n - 38) * 0.95), round((n - 38) * 1.3)
                s += (f"; f {x}{sg}a{'+' if sg == '-' else '-'}2,{e} {x}{sg}a{sg}{w},{e} ~{x}{sg}a{sg}{round(w * 0.2)},{e}{d}{round(h * 0.2)} "
                      f"{x}{sg}a{'+' if sg == '-' else '-'}2,{e}{d}{h}")
    return s


_f = lambda x, l=84, r=84: _h(x, l, r, 'b')                       # foot
_c = lambda x, l=84, r=84: _h(x, l, r, 'c')                       # top of a capital
_x = lambda x, l=84, r=84: _h(x, l, r, 'X-b')                     # top at the x-height
SERIF = {
    'A': _h(0, 78, 78, 'b', True) + '; ' + _h(580, 78, 78, 'b', True),
    'B': _f(0, 84, 0) + '; ' + _c(0, 84, 0), 'D': _f(0, 84, 0) + '; ' + _c(0, 84, 0),
    'E': _f(0, 84, 0) + '; ' + _c(0, 84, 0) + "; 448,c 448,c-118; 458,b 458,b+128; 416,366+62 416,366-62",
    'F': _f(0, 84, 96) + '; ' + _c(0, 84, 0) + "; 438,c 438,c-118; 392,352+62 392,352-62",
    'H': _f(0) + '; ' + _f(472) + '; ' + _c(0) + '; ' + _c(472), 'I': _f(0, 92, 92) + '; ' + _c(0, 92, 92),
    'J': _c(330, 96, 80),
    'K': _f(0) + '; ' + _c(0) + '; ' + _h(488, 70, 70, 'c', True) + '; ' + _h(506, 76, 70, 'b', True),
    'L': _f(0, 84, 0) + '; ' + _c(0) + "; 418,b 418,b+138",
    'M': _f(0) + '; ' + _f(628) + '; ' + _c(0, 84, 0) + '; ' + _c(628, 0, 84),
    'N': _f(0) + '; ' + _c(0, 84, 0) + '; ' + _c(474),
    'P': _f(0, 84, 96) + '; ' + _c(0, 84, 0), 'R': _f(0) + '; ' + _c(0, 84, 0) + '; ' + _h(500, 50, 78, 'b', True),
    'T': _f(268) + "; 0,c 0,c-124; 536,c 536,c-124",
    'U': _c(0) + '; ' + _c(472), 'V': _h(0, 72, 72, 'c', True) + '; ' + _h(576, 72, 72, 'c', True),
    'W': _h(0, 72, 72, 'c', True) + '; ' + _h(824, 72, 72, 'c', True) + '; ' + _h(412, 60, 60, 'c', True),
    'X': ' ; '.join(_h(x_, 70, 70, y_, True) for x_, y_ in ((8, 'c'), (526, 'c'), (0, 'b'), (534, 'b'))),
    'Y': _h(0, 72, 72, 'c', True) + '; ' + _h(560, 72, 72, 'c', True) + '; ' + _f(280),
    'Z': "18,c 18,c-112; 510,b 510,b+112",
    'C': "530,548+40 530,548-78", 'G': "530,548+40 530,548-78; 480,342 640,342", 'S': "458,560+34 458,560-84; 22,138-34 22,138+90",
    'b': _c(0, 84, 0), 'd': _c(398, 84, 0) + '; ' + _f(398, 0, 88), 'h': _c(0, 84, 0) + '; ' + _f(0) + '; ' + _f(336),
    'i': _x(0, 84, 0) + '; ' + _f(0), 'j': _x(88, 84, 0), 'k': _c(0, 84, 0) + '; ' + _f(0) + '; ' + _h(338, 66, 62, 'X-b', True) + '; ' + _h(352, 62, 66, 'b', True),
    'm': _x(0, 84, 0) + '; ' + _f(0) + '; ' + _f(298) + '; ' + _f(596),
    'p': _x(0, 84, 0) + '; ' + _h(0, 84, 96, 'D+b'), 'q': _h(398, 84, 84, 'D+b'), 'r': _x(0, 84, 0) + '; ' + _f(0, 84, 104),
    'u': _x(0, 84, 0) + '; ' + _x(336, 84, 0) + '; ' + _f(336, 0, 88),
    'v': _h(0, 66, 66, 'X-b', True) + '; ' + _h(430, 66, 66, 'X-b', True), 'x': '; '.join(_h(x_, 66, 66, y_, True) for x_, y_ in ((6, 'X-b'), (414, 'X-b'), (0, 'b'), (420, 'b'))),
    'y': _h(0, 66, 66, 'X-b', True) + '; ' + _h(432, 66, 66, 'X-b', True), 'z': "12,x 12,x-96; 394,b 394,b+96",
    'thorn': _c(0, 84, 0) + '; ' + _h(0, 84, 96, 'D+b'), 'germandbls': _f(0, 84, 0),
    'f': _f(96, 84, 96), 'c': "340,410+30 340,410-70", 'one': _f(214), 'four': _f(296, 76, 76), 'seven': "0,c 0,c-112",
    'two': "394,b 394,b+104", 'five': "366,c 366,c-96", 'three': "26,572+34 26,572-84; 8,140-34 8,140+84", 'six': "358,578+36 358,578-76",
    'uni0393': _f(0, 84, 96) + '; ' + _c(0, 84, 0) + "; 438,c 438,c-118", 'uni03A0': _f(0) + '; ' + _f(472) + '; ' + _c(0, 84, 0) + '; ' + _c(472, 0, 84),
    'uni039B': _h(0, 78, 78, 'b', True) + '; ' + _h(560, 78, 78, 'b', True), 'uni03A6': _f(290) + '; ' + _c(290), 'uni03A8': _f(290) + '; ' + _c(290),
    'dotlessi': _x(0, 84, 0) + '; ' + _f(0),
}
LATIN['l'] = ("0,0 0,C-b; -46-a,C-b 0,C-b; -46-a,b 46+a,b; f -a+2,2*b -a-44,2*b ~-a-9,2*b+11 -a+2,2*b+57; f a-2,2*b a+44,2*b ~a+9,2*b+11 a-2,2*b+57; "
              "f -a+2,C-2*b -a-44,C-2*b ~-a-9,C-2*b-11 -a+2,C-2*b-57")
LATSB = {'l': (70, 70)}

# Italic: no slabs at the feet; the last stem of a letter leaves the line in a curved stroke, a is the one-storey form.
_e = lambda x: f"{x},92 ~{x},b {x}+58,b {x}+66+a,b+24"            # exit stroke (skeleton coordinates)
SERIF_IT = {
    'a': _e(398), 'd': _c(398, 84, 0) + '; ' + _e(398), 'h': _c(0, 84, 0) + '; ' + _e(336), 'i': _x(0, 84, 0) + '; ' + _e(0),
    'dotlessi': _x(0, 84, 0) + '; ' + _e(0), 'm': _x(0, 84, 0) + '; ' + _e(596), 'u': _x(0, 84, 0) + '; ' + _x(336, 84, 0) + '; ' + _e(336),
    'k': _c(0, 84, 0), 'r': _x(0, 84, 0), 'f': '', 'v': '', 'x': '', 'y': '', 'z': '',
}
LATIN_IT = {
    'n': f"0,0 0,470-b; 0,340@.8 ~0,{_T} 182,{_T} ~334,{_T} 334,330 334,88 ~334,b 392,b 400+a,b+24; -50-a,470-b 0,470-b; f -a+2,470-2*b -a-48,470-2*b ~-a-10,470-2*b-13 -a+2,470-2*b-63",
    'l': "0,88 0,C-b; -46-a,C-b 0,C-b; 0,92 ~0,b 58,b 66+a,b+24; f -a+2,C-2*b -a-44,C-2*b ~-a-9,C-2*b-11 -a+2,C-2*b-57",
    'w': "0,470-b 102,74 ~118,b-4 134,74 218,352 ~232,404 246,352 330,74 ~346,b-4 362,74 464,470-b",
    'f': "96,-120 96,566 ~96,c 226,c 248,c; 0,470-b 238,470-b; 96,-116 ~96,D+b 30,D+b -24,D+b",
}


def _post(k, loop=308.0, alef=585.0):
    """Body-text proportions: the loops a little lower and the stems taller, so that tall and short letters differ more
    and a word has a clearer outline.  Final heights: loops about 445, alef about 765."""
    def f(y):
        if y <= k:
            return y
        if y <= LT:
            return k + (y - k) * (loop - k) / (LT - k)
        return loop + (y - LT) * (alef - loop) / (AH - LT)
    return f


def _latmap(y):
    """lower case: x-height 470 instead of 520, ascenders still at the cap height"""
    if y <= 0 or y >= 700:
        return y
    return y * 470 / 520 if y <= 520 else 470 + (y - 520) * 230 / 180


def _armap(k):
    """Arabic letters without a drawing of their own: lower teeth and stems, slightly shallower bowls"""
    m1 = k + (335 - k) * (TH - k) / (290 - k)

    def f(y):
        if y <= 0:
            return y * (DB / -150.0)
        if y <= k:
            return y
        if y <= 335:
            return k + (y - k) * (TH - k) / (290 - k)
        return m1 + (y - 335) * (AH - m1) / 265.0
    return f


def _ligatures():
    """the ligatures and alternates of Suhar Naskh, redrawn: (their skeleton, the Sahafa skeleton)"""
    from . import arabic as A
    mm = A.RASM['meem.medi']['spec']
    my = _loop(190, 234, -116, 'k+30')
    return [
        (A._lm, f"310,{AH} 310,130 ~310,k 230,k 110,k; " + _loop(110, 238, 'k', 254) + "; 115,k 30,k ~-50,k -50,-45 -50,-205"),
        ("190,600 190,k; " + mm.replace('380,k 0,k', '300,k 0,k'), f"190,{AH} 190,k; " + my + "; 300,k 0,k"),
        ("190,600 190,k; " + mm, f"190,{AH} 190,k; " + my + "; 380,k 0,k"),
        ("400,600 400,350 ~400,292 330,292; " + A._jh, f"402,{AH} 402,262; " + _jh + "; " + _jb),
        (A.loop(450, 220, 'k', 232), _loop(450, 250, 'k', 296)), ("2*k+232+20+q", "2*k+296+20+q"),
        (A._ret, "150,k 70,k ~-20,k -20,-74 ~-20,-176 130,-176 430,-176"),
    ]


CUTS = ('text', 'headline', 'typewriter')


def style(wght=400, cut='text', italic=False, compat=False, opsz=0.0, grade=0.0, contrast=0.0):
    """Style of Suhar Sahafa.  cut: 'text' (wider, calmer) or 'headline' (tighter, sharper, deeper bowls)."""
    head = cut == 'headline'
    typ = cut == 'typewriter'
    st = Style('Sans', wght, italic, opsz, compat, grade=grade).set_naskh()
    st.markgap = 0.0
    t = st.t
    ta_ = t if t <= 1 else 1 + (t - 1) * 0.55
    ra_ = (lerp(44, 74, ta_) + lerp(38, 61, ta_)) / 2 * (st.r / ((lerp(44, 74, t) + lerp(38, 61, t)) / 2)) * lerp(1.12, 1.05, min(max(t, 0.0), 1.0)) * (lerp(1.22, 1.0, min(max(t, 0.0), 1.0)) if typ else 1.0)
    st.arx *= 0.885                                                # a newspaper column needs an economical letter
    if head:
        pa, pb = 1.30, 0.62                                        # more contrast for large sizes
    else:
        pa, pb = 1.20, 0.75                                        # moderate contrast, sturdy thins
    if typ:
        pa, pb = 1.0, 0.94                                         # a typewriter strikes one weight of line
    ok_ = abs(opsz)
    if opsz < 0:                                                   # caption: thicker thin strokes
        pa, pb = pa - 0.05 * ok_, pb + 0.08 * ok_
    elif opsz > 0:                                                 # display: finer
        pa, pb = pa + 0.06 * ok_, pb - 0.09 * ok_
    pa, pb = pa + 0.04 * contrast, pb - 0.11 * contrast           # contrast axis
    st.apen = E.Pen(ra_ * pa, ra_ * pb, 62.0)
    st.ra = st.apen.extent()[1]
    st.ns['k'] = st.ra
    st.ns['q'] = st.ra * lerp(1.06, 0.9, t) * (1 + (0.14 if opsz < 0 else -0.04) * ok_)
    st.npar = dict(low=0.16, high=0.03, K=0.56, taper=0.62, top=0.6, foot=0.8, swing=0.0, ymap=_armap(st.ra), traps=0.42, deep=1.10, post=_post(st.ra))
    if typ:
        st.npar.update(taper=1.0, top=1.0, foot=1.0, traps=0.0, fillet=0.5)
        st.sbs *= 1.1
    if head:
        st.npar.update(low=0.20, taper=0.42, top=0.5, foot=0.66, deep=1.18, traps=0.0, fillet=0.34)
        st.arx *= 0.96
        st.sbs *= 0.88
        st.xs *= 0.95
        st.spacef = 0.92
    if opsz < 0:                                                   # caption: wider letters, deeper traps, marks further out
        st.arx *= 1 + 0.03 * ok_
        st.npar['traps'] *= 1 + 0.5 * ok_
        st.markgap = 24.0 * ok_
    elif opsz > 0:
        st.npar['traps'] *= 1 - 0.6 * ok_
        st.npar['fillet'] = max(st.npar.get('fillet', 0.0), 0.3 * ok_)
        st.npar['taper'] *= 1 - 0.2 * ok_
    st.altspec = ARABIC
    st.altsub = _ligatures()
    # Latin: the stem as thick as the Arabic baseline stroke, horizontals thinner
    a, hb = st.ra, st.ra * (0.56 if head else 0.92 if typ else 0.66) * (1 - 0.14 * contrast)
    st.pen = E.Pen(a, hb)
    st.a, st.hb = a, hb
    st.dt = a * 1.16
    st.ns.update(a=a, hb=hb, b=hb, dt=st.dt, x=520 - hb, c=700 - hb, d=-200 + hb,
                 bo=hb - st.ns['o'], xo=520 - hb + st.ns['o'], co=700 - hb + st.ns['o'], do=-200 + hb - st.ns['o'])
    st.latalt = LATIN
    st.latserif = SERIF
    if italic:
        st.latalt = {**{n: v for n, v in LATIN.items() if n != 'a'}, **LATIN_IT}
        st.latserif = {n: v for n, v in {**SERIF, **SERIF_IT}.items() if v}
    st.latsb = LATSB
    st.latsbf = lambda n: 0.62 if (n in SERIF or n in LATIN) and n not in ('c', 'e', 's', 'C', 'G', 'S') else 0.9
    st.latmap = _latmap
    st.xh = LATIN_X
    st.sahafa = cut
    st.grade = grade
    st.contrast = contrast
    return st


def build_test(path, wght=400, cut='text', italic=False):
    """compile a test font"""
    import ufo2ft
    from . import build as B
    for m in ('latin_ext', 'arabic', 'terminal', 'symbols', 'greek_cyrillic', 'more_scripts'):
        __import__('retrofont.' + m)
    st = style(wght, cut, italic)
    ufo, gl = B.make(st, 'Sahafa')
    f = ufo2ft.compileTTF(ufo, removeOverlaps=True)
    f.save(path)
    return f


if __name__ == '__main__':
    import sys
    build_test(sys.argv[1] if len(sys.argv) > 1 else 'SuharSahafa-Test.ttf', int(sys.argv[2]) if len(sys.argv) > 2 else 400,
               sys.argv[3] if len(sys.argv) > 3 else 'text', len(sys.argv) > 4)
