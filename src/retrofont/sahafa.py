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

ARABIC = {
    # ص: a long, high loop, a tooth, then the join or the bowl
    'sad.init': dict(spec=_sl(215, 650) + "; 225,k 118,k; 118,225 ~118,120 105,85 ~90,k 50,k 0,k", dx=435 - 475, dy=LT - 262),
    'sad.medi': dict(spec=_sl(215, 650) + "; 225,k 118,k; 118,225 ~118,120 105,85 ~90,k 50,k 0,k; 742,k 640,k", aw=742, dx=435 - 475, dy=LT - 262),
    'sad.isol': dict(spec=_sl(430, 865) + "; 440,k 340,k; 340,225 340,25 " + _bowl.format(x=340, m=165), dx=650 - 655, dy=LT - 262),
    'sad.fina': dict(spec=_sl(430, 865) + "; 440,k 340,k; 340,225 340,25 " + _bowl.format(x=340, m=165) + "; 957,k 855,k", aw=957, dx=650 - 655, dy=LT - 262),
    # ح: open head; when it joins forward the stroke falls back to the line in one curve
    'jeem.init': dict(spec="30,212 ~72,298 172,290 398,260!r; 393,260@1.22 ~310,150 170,k+18@1.15 ~95,k 0,k", dy=-30),
    'jeem.medi': dict(spec="490,k 0,k; 472,k+8@1.1 ~474,262 336,322 ~196,380 30,304!r", aw=490, dx=10, dy=8),
    'jeem.isol': dict(spec=_jh + "; " + _jb, dy=-28),
    'jeem.fina': dict(spec=_jh + "; " + _jb + "; 522,k 30,k", aw=522, dy=-28),
    # ي (and the other toothed letters): the tooth leans and bends into the join
    'beh.init': dict(spec=f"168,{TH} ~168,128 152,88 ~132,k 72,k 0,k", dy=0),
    'beh.medi': dict(spec=f"128,{TH} ~128,128 114,88 ~96,k 52,k 0,k; 252,k 100,k", aw=252, dy=0),
    'yeh.fina': dict(spec="472,k 432,k ~378,k 378,0 ~378,-72 190,-72 ~-22,-72 -22,18 ~-22,98 24,150", aw=472, dy=-17),
    'yeh.isol': dict(spec="500,212 ~500,298 420,298 ~336,298 336,214 ~336,132 396,82 ~442,46 442,4 ~442,-72 220,-72 ~-22,-72 -22,18 ~-22,98 24,150", dy=-17),
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
    'tah.init': dict(spec=_sl(55, 490) + f"; 88,k 88,{AH}; 150,k 0,k", dy=LT - 262, anch={'top': (88, AH + 6)}),
    'tah.medi': dict(spec=_sl(55, 490) + f"; 88,k 88,{AH}; 150,k 0,k; 580,k 470,k", aw=580, dy=LT - 262, anch={'top': (88, AH + 6)}),
    'tah.isol': dict(spec=_sl(35, 470) + f"; 68,k 68,{AH}", dy=LT - 262, anch={'top': (68, AH + 6)}),
    'tah.fina': dict(spec=_sl(35, 470) + f"; 68,k 68,{AH}; 560,k 450,k", aw=560, dy=LT - 262, anch={'top': (68, AH + 6)}),
    # ق و: the head as large as the other loops
    'qaf.isol': dict(spec=_loop(335, 262, 'k+26', LT) + f"; 466,188 466,-20 ~466,{DB} 230,{DB} ~-12,{DB} -12,15 ~-12,105 30,165", dx=5, dy=LT - 305),
    'qaf.fina': dict(spec=_loop(335, 262, 'k+26', LT) + f"; 466,188 466,-20 ~466,{DB} 230,{DB} ~-12,{DB} -12,15 ~-12,105 30,165; 592,k 452,k", aw=592, dx=5, dy=LT - 305),
    'waw.isol': dict(spec=_loop(160, 252, 'k+6', LT - 12) + f"; 286,176 286,20 ~286,{DB - 6} 86,{DB - 6} -22,{DB - 6}", dx=10, dy=LT - 12 - 290),
    'waw.fina': dict(spec=_loop(160, 252, 'k+6', LT - 12) + f"; 286,176 286,20 ~286,{DB - 6} 86,{DB - 6} -22,{DB - 6}; 376,k 256,k", aw=376, dx=10, dy=LT - 12 - 290),
    # ر ز: a short tail that sweeps under the line; د ذ: an open angle; ن: a wide, shallow bowl
    'reh.isol': dict(spec=f"196,262 ~214,120 196,30 ~168,{DB + 8} 20,{DB - 4} -44,{DB - 4}", dx=6, dy=0),
    'reh.fina': dict(spec=f"296,k 262,k ~206,k 198,-20 ~176,{DB + 8} 20,{DB - 4} -44,{DB - 4}", aw=296, dx=6, dy=0),
    'dal.isol': dict(spec="128,338 ~312,214 312,112 ~312,k 205,k 0,k", dx=4, dy=-10),
    'dal.fina': dict(spec="128,338 ~312,214 312,112 ~312,k 205,k 0,k; 392,k 256,k", aw=392, dx=4, dy=-10),
    'noon.isol': dict(spec=f"452,268 452,-24 ~452,{DB} 226,{DB} ~-12,{DB} -12,15 ~-12,105 30,165", dx=10, dy=0),
    'noon.fina': dict(spec=f"580,k 522,k ~452,k 452,-24 ~452,{DB} 226,{DB} ~-12,{DB} -12,15 ~-12,105 30,165", aw=580, dx=10, dy=0),
    # ع غ at the start of a word and alone: a wide, open head
    'ain.init': dict(spec="318,262 ~306,338 198,338 ~52,338 52,200 ~52,k 180,k; 318,k!r 0,k", dx=10, dy=-12),
    # لا: the lam upright, the alef leaning across it in one curve
    'lamalef.isol': dict(spec=f"322,{AH} 322,150 ~322,k 236,k ~152,k 130,140 ~92,330 -34,{AH + 4}", dy=AH - 600),
    'lamalef.fina': dict(spec=f"322,{AH} 322,150 ~322,k 236,k ~152,k 130,140 ~92,330 -34,{AH + 4}; 412,k 312,k", aw=412, dy=AH - 600),
    # ع in the middle and at the end of a word: a larger head, so that the counter stays open in small sizes
    'ain.medi': dict(spec="322,k 0,k; z ~6,322 ~316,322 ~161,k-98", aw=322, dx=6, dy=27),
    'ain.fina': dict(spec="346,k 122,k; z ~10,316 ~292,316 ~151,k-90; 156,k+20 ~0,10 0,-70 ~0,-172 200,-172 300,-172 ~372,-172 404,-126", aw=346, dx=6, dy=31),
}

# Latin: a sturdy serif.  b = half thickness of a horizontal; the top of the x-height is at 470.
_T, _B = "470-b+o", "b-o"
LATIN = {
    'n': f"0,0 0,470-b; 0,340@.8 ~0,{_T} 182,{_T} ~334,{_T} 334,330 334,0; -48-a,b 48+a,b; 334-48-a,b 334+48+a,b; -50-a,470-b 0,470-b; f -a+2,2*b -a-38,2*b -a+2,2*b+43; f a-2,2*b a+38,2*b a-2,2*b+43; f 334-a+2,2*b 334-a-38,2*b 334-a+2,2*b+43; f 334+a-2,2*b 334+a+38,2*b 334+a-2,2*b+43; f -a+2,470-2*b -a-40,470-2*b -a+2,470-2*b-45",
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
    if br:                                                        # a wedge between serif and stem
        up = y == 'b'
        e, d = (f"{y}+b", '+') if up else (f"{y}-b", '-')
        if l:
            s += f"; f {x}-a+2,{e} {x}-a-{round((l - 38) * 0.8)},{e} {x}-a+2,{e}{d}{round((l - 38) * 0.9)}"
        if r:
            s += f"; f {x}+a-2,{e} {x}+a+{round((r - 38) * 0.8)},{e} {x}+a-2,{e}{d}{round((r - 38) * 0.9)}"
    return s


_f = lambda x, l=84, r=84: _h(x, l, r, 'b')                       # foot
_c = lambda x, l=84, r=84: _h(x, l, r, 'c')                       # top of a capital
_x = lambda x, l=84, r=84: _h(x, l, r, 'X-b')                     # top at the x-height
SERIF = {
    'A': _h(0, 78, 78, 'b', False) + '; ' + _h(580, 78, 78, 'b', False),
    'B': _f(0, 84, 0) + '; ' + _c(0, 84, 0), 'D': _f(0, 84, 0) + '; ' + _c(0, 84, 0),
    'E': _f(0, 84, 0) + '; ' + _c(0, 84, 0) + "; 448,c 448,c-118; 458,b 458,b+128; 416,366+62 416,366-62",
    'F': _f(0, 84, 96) + '; ' + _c(0, 84, 0) + "; 438,c 438,c-118; 392,352+62 392,352-62",
    'H': _f(0) + '; ' + _f(472) + '; ' + _c(0) + '; ' + _c(472), 'I': _f(0, 92, 92) + '; ' + _c(0, 92, 92),
    'J': _c(330, 96, 80),
    'K': _f(0) + '; ' + _c(0) + '; ' + _h(488, 70, 70, 'c', False) + '; ' + _h(506, 76, 70, 'b', False),
    'L': _f(0, 84, 0) + '; ' + _c(0) + "; 418,b 418,b+138",
    'M': _f(0) + '; ' + _f(628) + '; ' + _c(0, 84, 0) + '; ' + _c(628, 0, 84),
    'N': _f(0) + '; ' + _c(0, 84, 0) + '; ' + _c(474),
    'P': _f(0, 84, 96) + '; ' + _c(0, 84, 0), 'R': _f(0) + '; ' + _c(0, 84, 0) + '; ' + _h(500, 50, 78, 'b', False),
    'T': _f(268) + "; 0,c 0,c-124; 536,c 536,c-124",
    'U': _c(0) + '; ' + _c(472), 'V': _h(0, 72, 72, 'c', False) + '; ' + _h(576, 72, 72, 'c', False),
    'W': _h(0, 72, 72, 'c', False) + '; ' + _h(824, 72, 72, 'c', False) + '; ' + _h(412, 60, 60, 'c', False),
    'X': ' ; '.join(_h(x_, 70, 70, y_, False) for x_, y_ in ((8, 'c'), (526, 'c'), (0, 'b'), (534, 'b'))),
    'Y': _h(0, 72, 72, 'c', False) + '; ' + _h(560, 72, 72, 'c', False) + '; ' + _f(280),
    'Z': "18,c 18,c-112; 510,b 510,b+112",
    'C': "530,548+40 530,548-78", 'G': "530,548+40 530,548-78; 480,342 640,342", 'S': "458,560+34 458,560-84; 22,138-34 22,138+90",
    'b': _c(0, 84, 0), 'd': _c(398, 84, 0) + '; ' + _f(398, 0, 88), 'h': _c(0, 84, 0) + '; ' + _f(0) + '; ' + _f(336),
    'i': _x(0, 84, 0) + '; ' + _f(0), 'j': _x(88, 84, 0), 'k': _c(0, 84, 0) + '; ' + _f(0) + '; ' + _h(338, 66, 62, 'X-b', False) + '; ' + _h(352, 62, 66, 'b', False),
    'm': _x(0, 84, 0) + '; ' + _f(0) + '; ' + _f(298) + '; ' + _f(596),
    'p': _x(0, 84, 0) + '; ' + _h(0, 84, 96, 'D+b'), 'q': _h(398, 84, 84, 'D+b'), 'r': _x(0, 84, 0) + '; ' + _f(0, 84, 104),
    'u': _x(0, 84, 0) + '; ' + _x(336, 84, 0) + '; ' + _f(336, 0, 88),
    'v': _h(0, 66, 66, 'X-b', False) + '; ' + _h(430, 66, 66, 'X-b', False), 'x': '; '.join(_h(x_, 66, 66, y_, False) for x_, y_ in ((6, 'X-b'), (414, 'X-b'), (0, 'b'), (420, 'b'))),
    'y': _h(0, 66, 66, 'X-b', False) + '; ' + _h(432, 66, 66, 'X-b', False), 'z': "12,x 12,x-96; 394,b 394,b+96",
    'f': _f(96, 84, 96), 'c': "340,410+30 340,410-70", 'one': _f(214), 'four': _f(296, 76, 76), 'seven': "0,c 0,c-112",
    'two': "394,b 394,b+104", 'five': "366,c 366,c-96",
    'uni0393': _f(0, 84, 96) + '; ' + _c(0, 84, 0) + "; 438,c 438,c-118", 'uni03A0': _f(0) + '; ' + _f(472) + '; ' + _c(0, 84, 0) + '; ' + _c(472, 0, 84),
    'uni039B': _h(0, 78, 78, 'b', False) + '; ' + _h(560, 78, 78, 'b', False), 'uni03A6': _f(290) + '; ' + _c(290), 'uni03A8': _f(290) + '; ' + _c(290),
    'dotlessi': _x(0, 84, 0) + '; ' + _f(0),
}
LATIN['l'] = ("0,0 0,C-b; -46-a,C-b 0,C-b; -46-a,b 46+a,b; f -a+2,2*b -a-37,2*b -a+2,2*b+41; f a-2,2*b a+37,2*b a-2,2*b+41; "
              "f -a+2,C-2*b -a-37,C-2*b -a+2,C-2*b-41")
LATSB = {'l': (70, 70)}


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


CUTS = ('text', 'headline')


def style(wght=400, cut='text', italic=False, compat=False):
    """Style of Suhar Sahafa.  cut: 'text' (wider, calmer) or 'headline' (tighter, sharper, deeper bowls)."""
    head = cut == 'headline'
    st = Style('Sans', wght, italic, 0.0, compat).set_naskh()
    t = st.t
    ta_ = t if t <= 1 else 1 + (t - 1) * 0.55
    ra_ = (lerp(44, 74, ta_) + lerp(38, 61, ta_)) / 2 * (st.r / ((lerp(44, 74, t) + lerp(38, 61, t)) / 2)) * 1.05
    st.arx *= 0.93                                                 # a newspaper column needs an economical letter
    if head:
        st.apen = E.Pen(ra_ * 1.30, ra_ * 0.62, 62.0)              # more contrast for large sizes
    else:
        st.apen = E.Pen(ra_ * 1.20, ra_ * 0.75, 62.0)              # moderate contrast, sturdy thins
    st.ra = st.apen.extent()[1]
    st.ns['k'] = st.ra
    st.ns['q'] = st.ra * lerp(1.0, 0.86, t)
    st.npar = dict(low=0.16, high=0.03, K=0.56, taper=0.62, top=0.6, foot=0.8, swing=0.0, ymap=_armap(st.ra), traps=0.42)
    if head:
        st.npar.update(low=0.20, taper=0.42, top=0.5, foot=0.66, deep=1.14, traps=0.3)
        st.arx *= 0.96
        st.sbs *= 0.88
        st.xs *= 0.95
        st.spacef = 0.92
    st.altspec = ARABIC
    # Latin: the stem as thick as the Arabic baseline stroke, horizontals thinner
    a, hb = st.ra, st.ra * (0.56 if head else 0.66)
    st.pen = E.Pen(a, hb)
    st.a, st.hb = a, hb
    st.dt = a * 1.16
    st.ns.update(a=a, hb=hb, b=hb, dt=st.dt, x=520 - hb, c=700 - hb, d=-200 + hb,
                 bo=hb - st.ns['o'], xo=520 - hb + st.ns['o'], co=700 - hb + st.ns['o'], do=-200 + hb - st.ns['o'])
    st.latalt = LATIN
    st.latserif = SERIF
    st.latsb = LATSB
    st.latsbf = lambda n: 0.62 if (n in SERIF or n in LATIN) and n not in ('c', 'e', 's', 'C', 'G', 'S') else 0.9
    st.latmap = _latmap
    st.xh = LATIN_X
    st.sahafa = cut
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
