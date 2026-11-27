"""Arabic script: Arabic, Persian, Urdu letters in four contextual forms,
lam-alef ligatures, tashkeel, Quranic annotation marks, digits, punctuation,
word ligatures (U+FDF0..FDFD) and presentation-form code points.

Design: a low-contrast, simplified "UI Naskh" drawn with a round pen so it
matches the Latin at small sizes.  Every joined form ends its baseline stroke
exactly at x=0 (left join) and x=aw (right join), so words connect seamlessly
at any weight.  Variables: k = baseline stroke centre (stroke sits on the
baseline), q = half diagonal of a dot."""
import math
import unicodedata as ud
from . import engine as E
import re
from .model import G, REG, GlyphOut, Style, MONO_W, lerp

INFO = {}          # glyph name -> dict
# Arabic italics lean to the left, the direction of writing (set to +0.194 for a rightward slant)
AR_ITALIC_TAN = -math.tan(math.radians(9.0))
# Arabic is drawn on its own grid and enlarged so its body matches the Latin x-height in mixed text
AR_SCALE = 1.28
MONO_WIDEN = 1.4          # widest horizontal stretch of a narrow letter in the Mono cell
AR_SCALE_MONO = 1.20      # in the fixed cell a smaller body leaves room for the joins


def _fmt(v):
    return ('%g' % v) if isinstance(v, (int, float)) else str(v)


def _diamond(x, y, s=1.0):
    x, y = _fmt(x), _fmt(y)
    qq = 'q*%g' % s
    return f"f ({x})-{qq},({y}) ({x}),({y})+{qq} ({x})+{qq},({y}) ({x}),({y})-{qq}"


def dots(code, x, y):
    """code like '2a' / '3b'; (x, y) = point on the ink edge the cluster sits on"""
    n, where = int(code[0]), code[1]
    up = where == 'a'
    sg = '+' if up else '-'
    gap = 20 if up else 12
    y0 = f"({_fmt(y)}){sg}{gap}{sg}q"
    out = []
    if n == 1:
        out.append(_diamond(x, y0))
    elif n == 2:
        out += [_diamond(f"{_fmt(x)}-1.12*q", y0), _diamond(f"{_fmt(x)}+1.12*q", y0)]
    else:
        out += [_diamond(f"{_fmt(x)}-1.12*q", y0, .9), _diamond(f"{_fmt(x)}+1.12*q", y0, .9),
                _diamond(x, f"{y0}{sg}1.6*q", .9)]
    ext = {1: f'{gap}+2*q', 2: f'{gap}+2*q', 3: f'{gap}+3.5*q'}[n]
    return ';'.join(out), f"({_fmt(y)}){sg}({ext})"


# Skeletons drawn for the one-cell Mono: the wide letters with closer teeth, a shorter loop and a narrower bowl,
# so they need far less squeezing than the proportional drawings.
_mb = "~{x},-150 {m},-150 ~0,-150 0,40 0,215"
MSPEC = {
    'seen.isol': "520,290 520,125 ~520,k 465,k ~410,k 410,125 410,290;410,290 410,125 ~410,k 355,k ~300,k 300,125 300,290; 300,290 300,40 " + _mb.format(x=300, m=150),
    'seen.fina': "520,290 520,125 ~520,k 465,k ~410,k 410,125 410,290;410,290 410,125 ~410,k 355,k ~300,k 300,125 300,290; 300,290 300,40 " + _mb.format(x=300, m=150) + "; 600,k 500,k",
    'seen.init': "330,290 330,125 ~330,k 275,k ~220,k 220,125 220,290;220,290 220,125 ~220,k 165,k ~110,k 110,125 110,290; 110,290 110,125 ~110,k 50,k 0,k",
    'seen.medi': "330,290 330,125 ~330,k 275,k ~220,k 220,125 220,290;220,290 220,125 ~220,k 165,k ~110,k 110,125 110,290; 110,290 110,125 ~110,k 50,k 0,k; 420,k 310,k",
    'sad.isol': "z 420,205 ~300,205 300,(205+k)/2 ~300,k 400,k 540,k ~610,k 610,k+48 ~580,205 420,205; 300,k 250,k; 250,215 250,40 " + _mb.format(x=250, m=125),
    'sad.fina': "z 420,205 ~300,205 300,(205+k)/2 ~300,k 400,k 540,k ~610,k 610,k+48 ~580,205 420,205; 300,k 250,k; 250,215 250,40 " + _mb.format(x=250, m=125) + "; 690,k 590,k",
    'sad.init': "z 290,205 ~150,205 150,(205+k)/2 ~150,k 250,k 420,k ~490,k 490,k+48 ~465,205 290,205; 160,k 90,k; 90,215 90,125 ~90,k 45,k 0,k",
    'sad.medi': "z 290,205 ~150,205 150,(205+k)/2 ~150,k 250,k 420,k ~490,k 490,k+48 ~465,205 290,205; 160,k 90,k; 90,215 90,125 ~90,k 45,k 0,k; 570,k 470,k",
}
MAW = {'seen.fina': 600, 'seen.medi': 420, 'sad.fina': 690, 'sad.medi': 570}          # right-join x of the Mono drawings
MANCH = {'seen.isol': 410, 'seen.fina': 410, 'seen.init': 220, 'seen.medi': 220, 'sad.isol': 455, 'sad.fina': 455, 'sad.init': 320, 'sad.medi': 320}

NASKH_LOW, NASKH_HIGH = 0.30, 0.055
NASKH_SLOPE = 0.04        # Suhar Naskh Display: joined letters descend to the left by this much (cursive attachment)

# Skeletons drawn for the Naskh families (the letters that carry most of the character of the hand).
_NJ = "425,262 ~30,205 12,-10 ~0,-195 240,-195 ~410,-195 500,-115"
NSPEC = {
    'jeem.isol': "30,238 ~95,332 205,312 430,262!r; " + _NJ,
    'jeem.fina': "30,238 ~95,332 205,312 430,262!r; " + _NJ + "; 520,k 30,k",
    'jeem.init': "20,245 ~85,335 190,315 375,275!r; 370,275 ~255,k+30 110,k 0,k",
    'jeem.medi': "430,k 0,k; 20,245 ~85,335 190,315 375,275!r; 370,275 ~255,k+30 110,k 60,k",
    'ain.isol': "365,275 ~365,352 250,352 ~125,352 125,232 ~125,112 265,105 405,100!r; 400,100 ~30,70 12,-40 ~0,-195 240,-195 ~410,-195 500,-115",
    'heh.isol': "z 205,340 ~25,300 25,150 ~25,k 160,k ~305,k 305,180",
    'lamalef.isol': "330,600 330,170 ~330,k 235,k ~150,k 150,105 ~150,190 235,225; -45,606 ~40,330 150,105",
    'lamalef.fina': "330,600 330,170 ~330,k 235,k ~150,k 150,105 ~150,190 235,225; -45,606 ~40,330 150,105; 420,k 320,k",
    'kaf.init': "305,598 ~175,540 70,385!r; 70,385 ~295,300 295,150 ~295,k 200,k 0,k",
    'kaf.medi': "305,598 ~175,540 70,385!r; 70,385 ~295,300 295,150 ~295,k 200,k 0,k; 380,k 270,k",
    'meem.isol': "z 230,k+215 ~125,k+215 125,k+107 ~125,k 230,k ~335,k 335,k+107 ~335,k+215; 235,k 100,k ~15,k 15,-60 15,-250",
    'meem.fina': "z 230,k+215 ~125,k+215 125,k+107 ~125,k 230,k ~335,k 335,k+107 ~335,k+215; 235,k 100,k ~15,k 15,-60 15,-250; 430,k 320,k",
    'yeh.isol': "505,255 ~505,345 420,345 ~335,345 335,250 ~335,150 395,95 ~440,55 440,15 ~440,-58 215,-58 ~-45,-58 -45,35 ~-45,115 5,150",
    'yeh.fina': "470,k 440,k ~385,k 385,5 ~385,-58 180,-58 ~-45,-58 -45,35 ~-45,115 5,150",
}
_BOWL = re.compile(r"~([\d.]+),-150 ([\d.]+),-150 ~0,-150 0,(-?\d+) 0,(\d+)")
_LOOP = re.compile(r"z (\S+),(\S+) ~(\S+),\2 \3,(\S+) ~\3,(\S+) \1,\5 ~(\S+),\5 \6,\4 ~\6,\2")
_NBOAT = "110,k ~-6,k -6,112 ~-6,205 32,268"


def naskh_spec(spec, inf):
    """the skeleton a Naskh family draws for this glyph"""
    key = inf.get('rkey')
    if key in NSPEC and key in RASM and spec.startswith(RASM[key]['spec']):
        spec = NSPEC[key] + spec[len(RASM[key]['spec']):]
    # bowls end in an inward curl instead of a straight upright
    spec = _BOWL.sub(lambda m: f"~{m.group(1)},-168 {m.group(2)},-168 ~-14,-168 -14,{m.group(3)} "
                               f"~-14,{int(m.group(4)) - 62} 40,{m.group(4)}", spec)
    spec = spec.replace(BOAT, _NBOAT)
    if key and key.split('.')[0] in ('feh', 'qaf', 'waw', 'heh'):          # loops come to a point at the top right
        spec = _LOOP.sub(r"z \1,\2 ~\3,\2 \3,\4 ~\3,\5 \1,\5 ~\6,\5 \6,\4", spec)
    return spec


def nwarp(y, k, low=None, high=None):
    """Suhar Naskh: horizontal displacement of a skeleton point.  Below the baseline strokes sweep to the left
    (tails become diagonal, bowls deepen on the left); above it uprights lean slightly to the right."""
    low = NASKH_LOW if low is None else low
    high = NASKH_HIGH if high is None else high
    return low * y if y < 0 else high * max(0.0, y - k)


def ar_fn(st: Style, d):
    inf = INFO[d.name]
    pen = st.apen
    spec = inf['spec']
    msp = None                                # (Mono body, rest of the spec, x shift of the rest)
    _rk = inf.get('rkey')
    if st.mono and _rk in MSPEC and spec.startswith(RASM[_rk]['spec']) and inf.get('cells', 1) == 1:
        _da = RASM[_rk].get('da', RASM[_rk]['top'])[0]
        msp = (MSPEC[_rk], spec[len(RASM[_rk]['spec']):].lstrip(';'), MANCH[_rk] - _da)
    _named = False                            # a family may replace parts of a ligature or alternate: [(old, new)]
    for _o, _n in (getattr(st, 'altsub', None) or ()) if not st.mono else ():
        if _o in spec:
            spec = spec.replace(_o, _n)
            _named = True
    mark = inf.get('mark')
    jl, jr, aw = inf.get('jl'), inf.get('jr'), inf.get('aw')
    if msp and _rk in MAW:
        aw = MAW[_rk]
    msp_dy = 0.0
    _alt = getattr(st, 'altspec', None)       # a family with its own letter bodies: {rasm.form: {spec, aw, dx, dy}}
    if _alt and _rk in _alt and spec.startswith(RASM[_rk]['spec']) and not st.mono:
        _a = _alt[_rk]
        msp = (_a['spec'], spec[len(RASM[_rk]['spec']):].lstrip(';'), _a.get('dx', 0.0))
        msp_dy = _a.get('dy', 0.0)
        if 'aw' in _a:
            aw = _a['aw']
    npar = getattr(st, 'npar', None) or {}    # pen-treatment parameters; the defaults are those of Suhar Naskh
    _anch = (_alt[_rk].get('anch') if (msp and _alt and _rk in _alt and not st.mono) else None) or {}
    _ym = npar.get('ymap') if not (mark or inf.get('tab')) and ('jl' in inf or 'jr' in inf) else None
    _deep = npar.get('deep', 1.0)
    ymsp = False                              # proportions of the family applied to a shared skeleton
    if _ym and not msp and _rk in RASM and spec.startswith(RASM[_rk]['spec']):
        msp = (naskh_spec(RASM[_rk]['spec'], inf), spec[len(RASM[_rk]['spec']):].lstrip(';'), 0.0)
        ymsp = True
    _ymall = bool(_ym) and not msp
    _ymshape = _ymall and not _named
    _bdy = _alt[_rk].get('bdy', 0.0) if (msp and not ymsp and _alt and _rk in _alt and not st.mono) else None
    l = inf.get('l', 45) * st.sbs + st.sba
    r = inf.get('r', 45) * st.sbs + st.sba
    f = 1.0 if mark else st.arx
    if not st.mono:
        f *= inf.get('stretch', 1.0)          # justification alternates: a longer body, the same pen
    f0 = f

    SC = 1.0 if (mark or inf.get('tab')) else (AR_SCALE_MONO if st.mono else AR_SCALE)
    if not inf.get('tab'):
        SC *= getattr(st, 'arboost', 1.0)      # pixel fonts for very small sizes draw Arabic larger
    ta = AR_ITALIC_TAN if st.italic else 0.0
    ky = 0.0 if mark else st.ns['k'] * SC
    if aw is not None and not mark:
        aw_s = aw * SC

    letter = not mark and not inf.get('tab') and ('jl' in inf or 'jr' in inf)
    # Display: letters that join forward are drawn sloping down to the left about their left join
    slope = NASKH_SLOPE if getattr(st, 'display', False) and letter and inf.get('jl') and not st.mono else 0.0

    def build(f, slanted=False):
        nk = getattr(st, 'naskh', False)
        sp_ = naskh_spec(spec, inf) if nk and spec and letter else spec
        if msp:
            _ns = dict(st.ns, K=npar.get('K', 0.57)) if nk else st.ns
            shapes = E.parse(msp[0], _ns, lambda n: REG[n].spec)
            rest = E.parse(msp[1], st.ns, lambda n: REG[n].spec) if msp[1].strip() else []
            for s in rest:
                s.transform(lambda x, y: (x + msp[2], y + msp_dy))
            _nrest = len(rest)
            if ymsp:
                for s in shapes:
                    s.transform(lambda x, y: (x, _ym(y)))
                for s in rest:
                    _ys = [n.y for n in s.nodes]
                    _cy = (min(_ys) + max(_ys)) / 2
                    _d = _ym(_cy) - _cy
                    s.transform(lambda x, y: (x, y + _d))
            shapes += rest
        else:
            shapes = E.parse(sp_, dict(st.ns, K=0.57) if nk else st.ns, lambda n: REG[n].spec) if sp_ else []
            if _ymshape:
                for s in shapes:
                    s.transform(lambda x, y: (x, _ym(y)))
        if _deep != 1.0 and not mark and not inf.get('tab'):
            for s in shapes:
                s.transform(lambda x, y: (x, y * _deep if y < 0 else y))
        kk = st.ns['k']
        for s in shapes:
            for nd in s.nodes:
                if abs(nd.y - kk) < 1e-6 and not nd.cc:
                    if jl and abs(nd.x) < 1e-6:
                        nd.x = -8 / (f * SC)
                        nd.cap = 'v'
                    elif jr and aw is not None and abs(nd.x - aw) < 1e-6:
                        nd.x = aw + 8 / (f * SC)
                        nd.cap = 'v'
        if nk and not mark and not inf.get('tab'):
            for s in (shapes[:len(shapes) - _nrest] if msp and _nrest else shapes):   # pointed terminals: the pen is lifted at the free end of a stroke
                if s.kind != 'stroke' or s.closed:
                    continue
                if len(s.nodes) == 2:             # a plain upright (alef, the stem of tah): thinner towards the foot
                    lo = min(s.nodes, key=lambda n: n.y)
                    hi = max(s.nodes, key=lambda n: n.y)
                    if hi.y - lo.y > 300 and abs(hi.x - lo.x) < 30 and lo.cap != 'v':
                        lo.w *= npar.get('foot', 0.62)
                    continue
                n0 = s.nodes[0]
                if n0.cap is None and n0.y > kk + 120 and not n0.cc:      # tops of teeth and stems start fine
                    n0.w *= npar.get('top', 0.6)
                nd = s.nodes[-1]
                if nd.cap == 'v' or nd.cap == 'h' and abs(nd.y) < 1:
                    continue
                nd.w *= npar.get('taper', 0.42)
                if len(s.nodes) > 3 and s.nodes[-2].cc is False:
                    s.nodes[-2].w *= 0.8
        if nk and letter:
            for s in shapes:
                s.transform(lambda x, y: (x + nwarp(y, kk, npar.get('low', NASKH_LOW), npar.get('high', NASKH_HIGH)), y))
            if slope:
                for s in shapes:
                    s.transform(lambda x, y: (x, y + slope * x))
            _sw = npar.get('swing', 0.0)          # the line between two joins sags a little, as a hand-drawn join does
            if _sw and (jl or jr):
                _xs = [nd.x for s in shapes for nd in s.nodes]
                _x0, _x1 = (0.0 if jl else min(_xs)), (aw if (jr and aw is not None) else max(_xs))
                if _x1 - _x0 > 60:
                    def _swing(x, y):
                        u = min(1.0, max(0.0, (x - _x0) / (_x1 - _x0)))
                        return x, y - _sw * 4 * u * (1 - u) * max(0.0, 1 - max(0.0, y - kk) / 110.0) * (1.0 if y > -40 else 0.0)
                    for s in shapes:
                        s.transform(_swing)
        fx = f * SC
        fy = SC
        if fx != 1.0 or fy != 1.0:
            for s in shapes:
                s.transform(lambda x, y: (x * fx, y * fy))
        if slanted and ta:
            for s in shapes:
                s.transform(lambda x, y: (x + (y - ky) * ta, y))
        cs = E.outline(shapes, pen)
        return shapes, cs, E.bounds(cs)

    shapes, cs, bb = build(f)
    if bb is None:
        return GlyphOut(d.name, d.uni, [], inf.get('adv', 0))

    def place(bb, f):
        if mark:
            return 0.0, 0
        if inf.get('adv') is not None and not st.mono:
            adv = inf['adv'] if not inf.get('tab') else round(lerp(556, 572, st.t) + 2 * st.sba)
            return (adv - (bb[2] - bb[0])) / 2 - bb[0], adv
        dx = 0.0 if jl else l - bb[0]
        adv = (aw * SC * f + dx) if jr else (bb[2] + dx + r)
        return dx, adv

    dx, adv = place(bb, f)
    extra = []
    CW = MONO_W * inf.get('cells', 1)
    if st.mono and not mark:
        for _ in range(5):
            if adv <= CW + 0.5:
                break
            f *= max(0.3, (CW - 2 * st.ra * (0 if (jl and jr) else 1)) / (adv - 2 * st.ra * (0 if (jl and jr) else 1)))
            shapes, cs, bb = build(f)
            dx, adv = place(bb, f)
        if adv < CW - 60 and not inf.get('tab') and inf.get('adv') is None:
            # narrow letters are widened towards the cell (the pen keeps the stroke weight) before any kashida is added
            e = 2 * st.ra * (0 if (jl and jr) else 1)
            g_ = min(MONO_WIDEN, (CW - 30 - e) / max(adv - e, 1.0))
            if g_ > 1.03:
                f *= g_
                shapes, cs, bb = build(f)
                dx, adv = place(bb, f)
                if adv > CW:
                    f *= (CW - e) / (adv - e)
                    shapes, cs, bb = build(f)
                    dx, adv = place(bb, f)
        pad = CW - adv
        if jl and jr:
            sh = pad / 2
        elif jl:
            sh = pad * 0.5
        elif jr:
            sh = pad * 0.5
        else:
            sh = pad / 2
        k = st.ns['k'] * SC
        left_join = dx + sh
        right_join = aw * SC * f + sh + (0 if jl else dx) if jr else None
        if jl:
            extra.append(E.Shape('stroke', [E.Node(0, k), E.Node(left_join + 3, k)]))
        if jr:
            extra.append(E.Shape('stroke', [E.Node(right_join - 3, k), E.Node(CW, k)]))
        dx += sh
        adv = CW
    dx = round(dx)
    if ta:                      # italic: same placement as the upright, outline sheared about the baseline
        cs = build(f, True)[1]
    cs = E.shift(cs, dx)
    if extra:
        cs = cs + E.outline(extra, pen)
    _tr = npar.get('traps')                   # ink traps: static fonts only (they need the overlaps removed)
    if _tr and letter and not st.compat and not st.mono:
        _k = st.ns['k'] * SC
        cs = E.ink_traps(E.union(cs), _tr * _k, _tr * _k * 0.8, _k * 1.2, 440.0)
    g = GlyphOut(d.name, d.uni, cs, round(adv))
    g.ink = (bb[0] + dx, bb[1], bb[2] + dx, bb[3])
    for an, (ax, ay) in (inf.get('anchors') or {}).items():
        sc = SC
        x0_, y0_ = E._ev(_fmt(ax), st.ns), E._ev(_fmt(ay), st.ns)
        if an in _anch:
            x0_, y0_ = E._ev(_fmt(_anch[an][0]), st.ns), E._ev(_fmt(_anch[an][1]), st.ns)
        elif msp:
            x0_ += msp[2]
            y0_ += (_bdy if (_bdy is not None and (an.startswith('bot') or an == 'db')) else msp_dy)
        if (ymsp or _ymall) and not an.startswith('_'):
            y0_ = _ym(y0_)
        if _deep != 1.0 and y0_ < 0 and not mark:
            y0_ *= _deep
        if getattr(st, 'naskh', False) and letter:
            x0_ += nwarp(y0_, st.ns['k'], npar.get('low'), npar.get('high'))
            y0_ += slope * x0_
        x = x0_ * (1 if an.startswith('_') else f) * sc + (0 if mark else dx)
        y = y0_ * sc
        _mg = getattr(st, 'markgap', 0.0)         # small optical sizes: marks stand further from the letter
        if _mg and not mark and not inf.get('tab'):
            y += _mg if an.startswith('top') else (-_mg if an.startswith('bot') else 0.0)
        g.anchors[an] = (x + (y - ky) * ta, y)
    if getattr(st, 'display', False) and letter and not st.mono and (jl or jr) and d.name != 'uni0640':
        if jl:
            g.anchors['exit'] = (0, 0)
        if jr:
            g.anchors['entry'] = (round(adv), round(slope * inf.get('aw', 0) * SC) if jl else 0)
    return g


def AR(name, spec, uni=None, cat='base', **inf):
    inf['spec'] = spec
    INFO[name] = inf
    d = G(name, spec, fn=ar_fn, uni=uni or [], cat=cat, script='arab', slant=False)
    return d


# ---------------------------------------------------------------------------
# rasm (letter skeletons without dots)
# ---------------------------------------------------------------------------
def loop(cx, w=250, y0='k', h=262):
    a, b = cx - w / 2, cx + w / 2
    return (f"z {cx},{y0}+{h} ~{a},{y0}+{h} {a},{y0}+{h/2} ~{a},{y0} {cx},{y0} "
            f"~{b},{y0} {b},{y0}+{h/2} ~{b},{y0}+{h}")


def cup(x1, x2, h=290):
    m = (x1 + x2) / 2
    return f"{x1},{h} {x1},125 ~{x1},k {m},k ~{x2},k {x2},125 {x2},{h}"


def sloop(x0, x1, h=262):
    """the long flat loop of sad / tah: rounded on the left, tapering to the right"""
    w = x1 - x0
    return (f"z {x0 + 0.34 * w},{h} ~{x0},{h} {x0},({h}+k)/2 ~{x0},k {x0 + 0.3 * w},k {x1 - 0.2 * w},k "
            f"~{x1},k {x1},k+{0.3 * (h - 40):.0f} ~{x1 - 0.12 * w},{h} {x0 + 0.34 * w},{h}")


BOAT = "110,k ~0,k 0,120 0,250"
BOWL = "~{x},-150 {m},-150 ~0,-150 0,40 0,215"
JBOWL = "~0,-185 240,-185 380,-185 ~460,-185 495,-135"
EYES = "z 335,420 ~70,405 45,200 ~35,k 175,k ~335,k 335,190; w.72 80,318 ~235,300 318,105"
KMARK = "w.6 330,335 ~330,375 270,375 ~200,375 200,310 ~200,245 265,245 335,245!r; w.6 330,245 190,180"

RASM = {}


def R(key, spec, **kw):
    """kw: aw (right join x), jl, top=(x, yedge), bot=(x, yedge), da, db, din, l, r"""
    form = key.split('.')[1]
    kw.setdefault('jl', form in ('init', 'medi'))
    kw.setdefault('jr', form in ('medi', 'fina'))
    kw['spec'] = spec
    RASM[key] = kw


R('alef.isol', "0,0 0,600", l=54, r=60, top=(0, 606), bot=(0, 0))
R('alefshort.isol', "0,0 0,480", l=54, r=60, top=(0, 486), bot=(0, 0))
R('alefshort.fina', "150,k 70,k ~0,k 0,k+70 0,480", aw=150, l=54, top=(0, 486), bot=(40, 0))
R('alef.fina', "150,k 70,k ~0,k 0,k+70 0,600", aw=150, l=54, top=(0, 606), bot=(40, 0))
_beh = f"560,275 560,130 ~560,k 450,k {BOAT}"
R('beh.isol', _beh, top=(280, 250), bot=(280, 0), da=(280, '2*k'), db=(280, 0))
R('beh.fina', _beh + "; 640,k 540,k", aw=640, top=(280, 250), bot=(280, 0), da=(280, '2*k'), db=(280, 0))
R('beh.init', "180,335 180,130 ~180,k 90,k 0,k", top=(170, 335), bot=(150, 0), da=(172, 335), db=(150, 0))
R('beh.medi', "130,330 130,130 ~130,k 50,k 0,k; 250,k 100,k", aw=250, top=(125, 330), bot=(125, 0),
  da=(125, 330), db=(125, 0))
_noon = "430,-30 ~430,-150 215,-150 ~0,-150 0,60 0,240"
R('noon.isol', "430,290 " + _noon, top=(215, 270), bot=(215, '-150-k'), da=(215, 85))
R('noon.fina', "560,k 500,k ~430,k " + _noon, aw=560, top=(215, 270), bot=(215, '-150-k'), da=(215, 85))
_ybowl = "~0,-115 130,-115 400,-115 ~470,-115 500,-88"
R('yeh.isol', "505,255 ~505,345 420,345 ~335,345 335,250 ~335,150 395,95 ~440,55 440,20 ~440,-55 220,-55 ~0,-55 0,40 0,130",
  top=(420, '345+k'), bot=(220, '-55-k'), db=(220, '-55-k'), da=(220, 60))
R('yeh.fina', "470,k 440,k ~380,k 380,10 ~380,-55 190,-55 ~0,-55 0,40 0,130", aw=470, top=(300, '2*k'), bot=(190, '-55-k'),
  db=(190, '-55-k'), da=(190, 60))
R('barree.isol', "350,245 ~40,255 40,110 ~40,-20 210,-20 620,-20", r=30, top=(200, '255+k'), bot=(330, '-20-k'),
  da=(200, '250+k'))
R('barree.fina', "300,k 210,k ~40,k 40,-65 ~40,-165 210,-165 640,-165", aw=300, top=(180, '2*k'),
  bot=(330, '-165-k'), da=(180, '2*k'))
_jh = "5,292 430,292!r; 425,292 ~0,180 0,-25 " + JBOWL
R('jeem.isol', _jh, top=(215, '292+k'), bot=(240, '-185-k'), da=(215, '292+k'), din=(262, -45))
R('jeem.fina', _jh + "; 520,k 30,k", aw=520, top=(215, '292+k'), bot=(240, '-185-k'), da=(215, '292+k'),
  din=(262, -45))
R('jeem.init', "10,295 370,295!r; 365,295 ~255,k 110,k 0,k", top=(190, '295+k'), bot=(190, 0),
  da=(190, '295+k'), db=(190, 0))
R('jeem.medi', "430,k 0,k; 10,295 370,295!r; 365,295 ~255,k 110,k 60,k", aw=430, top=(190, '295+k'),
  bot=(190, 0), da=(190, '295+k'), db=(190, 0))
_dal = "140,350 ~300,200 300,110 ~300,k 200,k 0,k"
R('dal.isol', _dal, top=(170, 365), bot=(170, 0), da=(170, 350))
R('dal.fina', _dal + "; 380,k 250,k", aw=380, top=(170, 365), bot=(170, 0), da=(170, 350))
_reh = "~190,-150 10,-150 -40,-150"
R('reh.isol', "190,265 190,30 " + _reh, l=12, top=(180, 280), bot=(90, '-150-k'), da=(180, 270))
R('reh.fina', "290,k 260,k ~190,k 190,-30 " + _reh, aw=290, l=12, top=(180, '2*k+10'), bot=(90, '-150-k'),
  da=(185, '2*k'))
_waw = "z 150,290 ~30,290 30,170 ~30,k+10 150,k+10 ~270,k+10 270,170 ~270,290; 270,170 270,20 ~270,-150 70,-150 -20,-150"
R('waw.isol', _waw, l=12, top=(150, '290+k'), bot=(120, '-150-k'), da=(150, '290+k'))
R('waw.fina', _waw + "; 360,k 240,k", aw=360, l=12, top=(150, '290+k'), bot=(120, '-150-k'), da=(150, '290+k'))
_feh = loop(455) + f"; 455,k {BOAT}"
R('feh.isol', _feh, top=(455, '2*k+262'), bot=(250, 0), da=(455, '2*k+262'), db=(250, 0))
R('feh.fina', _feh + "; 650,k 540,k", aw=650, top=(455, '2*k+262'), bot=(250, 0), da=(455, '2*k+262'), db=(250, 0))
R('feh.init', loop(180) + "; 180,k 0,k", top=(175, '2*k+262'), bot=(160, 0), da=(175, '2*k+262'), db=(160, 0))
R('feh.medi', loop(175) + "; 350,k 0,k", aw=350, top=(175, '2*k+262'), bot=(175, 0), da=(175, '2*k+262'),
  db=(175, 0))
_qaf = "z 330,305 ~225,305 225,195 ~225,85 330,85 ~435,85 435,195 ~435,305; 435,195 435,-20 ~435,-150 215,-150 ~0,-150 0,40 0,225"
R('qaf.isol', _qaf, top=(330, '305+k'), bot=(215, '-150-k'), da=(330, '305+k'))
R('qaf.fina', _qaf + "; 560,k 420,k", aw=560, top=(330, '305+k'), bot=(215, '-150-k'), da=(330, '305+k'))
_seen = cup(740, 590) + ';' + cup(590, 440) + "; 440,290 440,40 ~440,-150 220,-150 ~0,-150 0,40 0,215"
R('seen.isol', _seen, top=(590, 305), bot=(220, '-150-k'), da=(590, 290), db=(590, 0))
R('seen.fina', _seen + "; 840,k 720,k", aw=840, top=(590, 305), bot=(220, '-150-k'), da=(590, 290), db=(590, 0))
_seeni = cup(440, 290) + ';' + cup(290, 140) + "; 140,290 140,125 ~140,k 60,k 0,k"
R('seen.init', _seeni, top=(290, 305), bot=(290, 0), da=(290, 290), db=(290, 0))
R('seen.medi', _seeni + "; 540,k 420,k", aw=540, top=(290, 305), bot=(290, 0), da=(290, 290), db=(290, 0))
_sad = sloop(430, 880) + "; 430,k 340,k; 340,215 340,40 ~340,-150 170,-150 ~0,-150 0,40 0,215"
R('sad.isol', _sad, top=(655, '262+k'), bot=(170, '-150-k'), da=(655, '262+k'))
R('sad.fina', _sad + "; 970,k 860,k", aw=970, top=(655, '262+k'), bot=(170, '-150-k'), da=(655, '262+k'))
_sadi = sloop(250, 700) + "; 260,k 130,k; 140,215 140,125 ~140,k 60,k 0,k"
R('sad.init', _sadi, top=(475, '262+k'), bot=(400, 0), da=(475, '262+k'))
R('sad.medi', _sadi + "; 790,k 680,k", aw=790, top=(475, '262+k'), bot=(400, 0), da=(475, '262+k'))
R('tah.isol', sloop(40, 470) + "; 105,k 105,600", top=(105, 606), bot=(250, 0), da=(300, '262+k'))
R('tah.fina', sloop(40, 470) + "; 105,k 105,600; 560,k 450,k", aw=560, top=(105, 606), bot=(250, 0),
  da=(300, '262+k'))
R('tah.init', sloop(60, 490) + "; 125,k 125,600; 150,k 0,k", top=(125, 606), bot=(270, 0), da=(320, '262+k'))
R('tah.medi', sloop(60, 490) + "; 125,k 125,600; 150,k 0,k; 580,k 470,k", aw=580, top=(125, 606), bot=(270, 0),
  da=(320, '262+k'))
R('ain.isol', "360,285 ~360,350 250,350 ~130,350 130,230 ~130,105 260,105 400,105!r; 395,105 ~0,60 0,-60 " + JBOWL,
  top=(250, '350+k'), bot=(240, '-185-k'), da=(250, '350+k'))
R('ain.init', "290,285 ~290,350 190,350 ~60,350 60,210 ~60,k 170,k; 300,k!r 0,k", top=(180, '350+k'),
  bot=(150, 0), da=(180, '350+k'))
R('ain.medi', "310,k 0,k; z ~15,295 ~295,295 ~155,k-85", aw=310, top=(155, '295+k'), bot=(155, 0),
  da=(155, '295+k'))
R('ain.fina', "330,k 120,k; z ~25,285 ~265,285 ~145,k-75; 150,k+20 ~0,10 0,-70 ~0,-185 200,-185 300,-185 ~370,-185 400,-135",
  aw=330, top=(145, '285+k'), bot=(200, '-185-k'), da=(145, '285+k'))
_kaf = f"500,600 500,130 ~500,k 400,k {BOAT}; {KMARK}"
R('kaf.isol', _kaf, top=(500, 606), bot=(250, 0))
R('kaf.fina', _kaf + "; 590,k 480,k", aw=590, top=(500, 606), bot=(250, 0))
_kafi = "300,600!h 75,380!r; 75,380 ~295,300 295,150 ~295,k 200,k 0,k"
R('kaf.init', _kafi, top=(190, 606), bot=(150, 0))
R('kaf.medi', _kafi + "; 380,k 270,k", aw=380, top=(190, 606), bot=(150, 0))
_keh = f"600,600!h 375,380!r; 375,380 ~595,300 595,150 ~595,k 500,k {BOAT}"
_swk = f"960,520!h 430,400!r; 430,400 ~850,360 850,150 ~850,k 740,k {BOAT}"
R('swashkaf.isol', _swk, top=(650, 560), bot=(400, 0))
R('swashkaf.fina', _swk + "; 950,k 830,k", aw=950, top=(650, 560), bot=(400, 0))
_swki = "640,520!h 75,400!r; 75,400 ~500,360 500,150 ~500,k 400,k 0,k"
R('swashkaf.init', _swki, top=(330, 560), bot=(250, 0))
R('swashkaf.medi', _swki + "; 600,k 480,k", aw=600, top=(330, 560), bot=(250, 0))
R('keheh.isol', _keh, top=(490, 606), bot=(250, 0))
R('keheh.fina', _keh + "; 690,k 580,k", aw=690, top=(490, 606), bot=(250, 0))
_g1, _g2 = "; w.9 300,735!h 105,560", "; w.9 600,735!h 405,560"
R('gaf.isol', _keh + _g2, top=(490, 745), bot=(250, 0))
R('gaf.fina', _keh + "; 690,k 580,k" + _g2, aw=690, top=(490, 745), bot=(250, 0))
R('gaf.init', _kafi + _g1, top=(190, 745), bot=(150, 0))
R('gaf.medi', _kafi + "; 380,k 270,k" + _g1, aw=380, top=(190, 745), bot=(150, 0))
_lam = "330,600 330,20 ~330,-150 165,-150 ~0,-150 0,-10 0,170"
R('lam.isol', _lam, r=52, top=(330, 606), bot=(165, '-150-k'))
R('lam.fina', _lam + "; 420,k 330,k", aw=420, top=(330, 606), bot=(165, '-150-k'))
R('lam.init', "150,600 150,130 ~150,k 60,k 0,k", r=52, top=(150, 606), bot=(120, 0))
R('lam.medi', "150,600 150,130 ~150,k 60,k 0,k; 240,k 120,k", aw=240, top=(150, 606), bot=(120, 0))
_meem = loop(230, 210, 'k', 215) + "; 235,k 95,k ~10,k 10,-45 10,-215"
R('meem.isol', _meem, top=(230, '2*k+215'), bot=(120, 0))
R('meem.fina', _meem + "; 430,k 320,k", aw=430, top=(230, '2*k+215'), bot=(120, 0))
R('meem.init', loop(235, 235, '-80', 270) + "; 235,k 0,k", top=(235, '190+k'), bot=(235, '-80-k'))
R('meem.medi', loop(190, 225, 'k-205', 205) + "; 380,k 0,k", aw=380, top=(190, '2*k'), bot=(190, '-205'))
R('heh.isol', "z 160,300 ~20,300 20,170 ~20,k 160,k ~300,k 300,170 ~300,300", top=(160, '300+k'), bot=(160, 0),
  da=(160, '300+k'))
R('heh.fina', loop(125, 220, 'k', 235) + "; 235,k+100 235,365; 330,k 120,k", aw=330, top=(125, '2*k+235'),
  bot=(120, 0), da=(115, '2*k+235'))
R('heh.init', EYES + "; 175,k 0,k", top=(200, '420+k'), bot=(170, 0), da=(200, '420+k'))
R('heh.medi', "340,k 0,k; z ~40,365 ~300,365 ~170,k-150; z ~35,-170 ~305,-170 ~170,k+110", aw=340,
  top=(170, '365+k'), bot=(170, '-170-k'), da=(170, '365+k'))
R('hehdo.isol', EYES, top=(200, '420+k'), bot=(170, 0), da=(200, '420+k'))
R('hehdo.init', EYES + "; 175,k 0,k", top=(200, '420+k'), bot=(170, 0), da=(200, '420+k'))
R('hehdo.medi', EYES + "; 420,k 0,k", aw=420, top=(200, '420+k'), bot=(170, 0), da=(200, '420+k'))
R('hehdo.fina', EYES + "; 420,k 175,k", aw=420, top=(200, '420+k'), bot=(170, 0), da=(200, '420+k'))
R('hehgoal.isol', RASM['heh.isol']['spec'], top=(160, '300+k'), bot=(160, 0), da=(160, '300+k'))
R('hehgoal.fina', "300,k 220,k ~130,k 130,130 ~130,235 62,235 ~0,235 0,160 ~0,95 65,62", aw=300,
  top=(70, '235+k'), bot=(100, 0), da=(70, '235+k'))
_hook = "; w.8 178,-52 ~178,-150 105,-150 58,-150"
R('hehgoal.init', RASM['beh.init']['spec'] + _hook, top=(170, 290), bot=(120, '-150-k'), da=(172, 290))
R('hehgoal.medi', RASM['beh.medi']['spec'] + _hook.replace('178', '128').replace('105', '55').replace('58', '8'),
  aw=250, top=(125, 285), bot=(70, '-150-k'), da=(125, 285))
_la = "330,600 330,150 ~330,k 245,k ~165,k 140,150 -45,606"
R('lamalef.isol', _la, r=52, top=(-45, 606), bot=(200, 0))
R('lamalef.fina', _la + "; 420,k 320,k", aw=420, top=(-45, 606), bot=(200, 0))
R('hamza.isol', "w.9 200,300 ~200,350 120,350 ~35,350 35,265 ~35,180 125,180 215,180!r; w.9 210,180 20,95",
  l=42, r=42, top=(120, '350+k'), bot=(120, 60))
R('tatweel.medi', "250,k 0,k", aw=250, top=(125, '2*k'), bot=(125, 0))

# small signs used as dots-like attachments
HAMZA_S = "use:uni0621|0.55,0.55,{x},{y}"
TAH_S = "w.45 ring ({x})+100,({y})+42 62,44;w.45 ({x})+52,({y})+4 ({x})+52,({y})+175"

# ---------------------------------------------------------------------------
# letters:  cp: (isol/fina rasm, init/medi rasm or None, dot code)
# ---------------------------------------------------------------------------
LETTERS = {
    0x621: ('hamza', None, None),
    0x622: ('alefshort', None, 'ma'), 0x623: ('alefshort', None, 'ha'), 0x624: ('waw', None, 'ha'),
    0x625: ('alef', None, 'hb'), 0x626: ('yeh', 'beh', 'ha'), 0x627: ('alef', None, None),
    0x628: ('beh', 'beh', '1b'), 0x629: ('heh', None, '2a'), 0x62A: ('beh', 'beh', '2a'),
    0x62B: ('beh', 'beh', '3a'), 0x62C: ('jeem', 'jeem', '1i'), 0x62D: ('jeem', 'jeem', None),
    0x62E: ('jeem', 'jeem', '1a'), 0x62F: ('dal', None, None), 0x630: ('dal', None, '1a'),
    0x631: ('reh', None, None), 0x632: ('reh', None, '1a'), 0x633: ('seen', 'seen', None),
    0x634: ('seen', 'seen', '3a'), 0x635: ('sad', 'sad', None), 0x636: ('sad', 'sad', '1a'),
    0x637: ('tah', 'tah', None), 0x638: ('tah', 'tah', '1a'), 0x639: ('ain', 'ain', None),
    0x63A: ('ain', 'ain', '1a'), 0x641: ('feh', 'feh', '1a'), 0x642: ('qaf', 'feh', '2a'),
    0x643: ('kaf', 'kaf', None), 0x644: ('lam', 'lam', None), 0x645: ('meem', 'meem', None),
    0x646: ('noon', 'beh', '1a'), 0x647: ('heh', 'heh', None), 0x648: ('waw', None, None),
    0x649: ('yeh', 'beh', None), 0x64A: ('yeh', 'beh', '2b'),
    0x671: ('alefshort', None, 'wa'), 0x679: ('beh', 'beh', 'ta'), 0x67E: ('beh', 'beh', '3b'),
    0x686: ('jeem', 'jeem', '3i'), 0x688: ('dal', None, 'ta'), 0x691: ('reh', None, 'ta'),
    0x698: ('reh', None, '3a'), 0x6A4: ('feh', 'feh', '3a'), 0x6A9: ('keheh', 'kaf', None),
    0x6AF: ('gaf', 'gaf', None), 0x6BA: ('noon', 'beh', 'ng'), 0x6BE: ('hehdo', 'hehdo', None),
    0x6C0: ('heh', None, 'ha'), 0x6C1: ('hehgoal', 'hehgoal', None), 0x6C2: ('hehgoal', None, 'ha'),
    0x6C3: ('hehgoal', None, '2a'), 0x6CC: ('yeh', 'beh', 'fy'), 0x6D2: ('barree', None, None),
    0x6D3: ('barree', None, 'ha'), 0x6D5: ('heh', None, None), 0x66E: ('beh', 'beh', None),
    0x66F: ('qaf', 'feh', None), 0x6A1: ('feh', 'feh', None),
    # Kurdish (Sorani), Jawi
    0x6B5: ('lam', 'lam', 'va'), 0x695: ('reh', None, 'vb'), 0x6C6: ('waw', None, 'va'), 0x6CE: ('yeh', 'beh', 'va'),
    0x6A0: ('ain', 'ain', '3a'), 0x6BD: ('noon', 'beh', '3a'), 0x6AD: ('kaf', 'kaf', '3a'),
    # Pashto
    0x67C: ('beh', 'beh', '2a+nrb'), 0x681: ('jeem', 'jeem', 'ha'), 0x685: ('jeem', 'jeem', '3a'), 0x689: ('dal', None, 'nrb'),
    0x693: ('reh', None, 'nrb'), 0x696: ('reh', None, '1a+n1b'), 0x69A: ('seen', 'seen', '1a+n1b'), 0x6AB: ('keheh', 'kaf', 'nrb'),
    0x6BC: ('noon', 'beh', '1a+nrb'), 0x6D0: ('yeh', 'beh', 'nx2b'), 0x6CD: ('yeh', None, 'nyt'),
    # Uyghur, Kazakh, Kyrgyz
    0x6C7: ('waw', None, 'nua'), 0x6C8: ('waw', None, 'nla'), 0x6CB: ('waw', None, '3a'),
    # Sindhi
    0x67A: ('beh', 'beh', 'nx2a'), 0x67B: ('beh', 'beh', 'nx2b'), 0x67D: ('beh', 'beh', 'nx3a'), 0x67F: ('beh', 'beh', 'n4a'),
    0x680: ('beh', 'beh', 'n4b'), 0x683: ('jeem', 'jeem', 'n2i'), 0x684: ('jeem', 'jeem', 'nx2i'), 0x687: ('jeem', 'jeem', 'n4i'),
    0x68A: ('dal', None, 'n1b'), 0x68C: ('dal', None, '2a'), 0x68D: ('dal', None, 'n2b'), 0x68E: ('dal', None, '3a'),
    0x68F: ('dal', None, 'nx3a'), 0x699: ('reh', None, 'n4a'), 0x6A6: ('feh', 'feh', 'n4a'), 0x6AA: ('swashkaf', 'swashkaf', None),
    0x6B1: ('gaf', 'gaf', '2a'), 0x6B3: ('gaf', 'gaf', 'nx2b'), 0x6BB: ('noon', 'beh', 'ta'),
    # Maghribi and other additions that use existing parts
    0x6A2: ('feh', 'feh', 'n1b'), 0x6A7: ('qaf', 'feh', '1a'), 0x6A8: ('qaf', 'feh', '3a'), 0x697: ('reh', None, '2a'),
    0x6CA: ('waw', None, '2a'), 0x6CF: ('waw', None, '1a'), 0x69B: ('seen', 'seen', 'n3b'), 0x6B6: ('lam', 'lam', '1a'),
    0x6B7: ('lam', 'lam', '3a'), 0x6D1: ('yeh', 'beh', 'n3b'),
}


def cluster(kind, x, yc):
    """dot cluster centred on (x, yc) -> (spec, half height expression)"""
    x, yc = f"({_fmt(x)})", f"({_fmt(yc)})"
    if kind == '1':
        return _diamond(x, yc), 'q'
    if kind == '2':
        return ';'.join([_diamond(f"{x}-1.12*q", yc), _diamond(f"{x}+1.12*q", yc)]), 'q'
    if kind == 'x2':
        return ';'.join([_diamond(x, f"{yc}+1.05*q", .9), _diamond(x, f"{yc}-1.05*q", .9)]), '1.95*q'
    if kind in ('3', 'x3'):
        sg = '+' if kind == '3' else '-'
        og = '-' if kind == '3' else '+'
        return ';'.join([_diamond(f"{x}-1.12*q", f"{yc}{og}0.8*q", .9), _diamond(f"{x}+1.12*q", f"{yc}{og}0.8*q", .9),
                         _diamond(x, f"{yc}{sg}0.8*q", .9)]), '1.7*q'
    if kind == '4':
        return ';'.join(_diamond(f"{x}{a}1.12*q", f"{yc}{b}1.0*q", .9) for a in '-+' for b in '-+'), '1.9*q'
    raise ValueError(kind)


def _extra(code, rs, rasm, spec, top, bot):
    """additional attachments (codes starting with n) -> spec, top, bot"""
    tx, ty = top
    bx, by = bot
    c = code[1:]
    if c in ('ra', 'rb'):
        x, y = rs.get('db', rs.get('bot', (bx, 0)))
        if rasm == 'reh':
            x, y = 60, -150
        if rasm in ('keheh', 'kaf'):
            x, y = (rs.get('bot', (150, 0))[0], 0)
        xe, ye = f"({_fmt(x)})", f"({_fmt(y)})"
        spec += f";w.4 ring {xe},{ye}-k-56 62,62"
        return spec, (tx, ty), (x, f"{ye}-k-148")
    if c == 'ua':
        x, y = rs.get('da', rs['top'])
        xe, ye = f"({_fmt(x)})", f"({_fmt(y)})"
        spec += (f";w.5 z {xe}+5,{ye}+215 ~{xe}-45,{ye}+215 {xe}-45,{ye}+170 ~{xe}-45,{ye}+125 {xe}+5,{ye}+125 ~{xe}+55,{ye}+125 {xe}+55,{ye}+170 ~{xe}+55,{ye}+215;"
                 f"w.5 {xe}+55,{ye}+170 ~{xe}+55,{ye}+70 {xe}-70,{ye}+50")
        return spec, (x, f"{ye}+235"), (bx, by)
    if c == 'la':
        x, y = rs.get('da', rs['top'])
        xe, ye = f"({_fmt(x)})", f"({_fmt(y)})"
        spec += f";w.6 {xe},{ye}+55 {xe},{ye}+235"
        return spec, (x, f"{ye}+250"), (bx, by)
    if c == 'yt':
        spec += ";w.85 30,-20 ~-20,-120 -120,-150"
        return spec, (tx, ty), (bx, by)
    kind, where = c[:-1], c[-1]
    if where == 'i':
        if 'din' in rs:
            x, y = rs['din']
            sp, hh = cluster(kind, x, y)
            return spec + ';' + sp, (tx, ty), (bx, by)
        where = 'b'
    if where == 'a':
        x, y = rs.get('da', rs['top'])
        ye = f"({_fmt(y)})"
        sp, hh = cluster(kind, x, f"{ye}+20+{hh_(kind)}")
        return spec + ';' + sp, (x, f"{ye}+20+2*{hh}"), (bx, by)
    x, y = rs.get('db', rs.get('bot', (bx, by)))
    if (x, y) == (bx, by) or 'db' not in rs:
        x, y = bx, by
    ye = f"({_fmt(y)})"
    sp, hh = cluster(kind, x, f"{ye}-12-{hh_(kind)}")
    return spec + ';' + sp, (tx, ty), (x, f"{ye}-12-2*{hh}")


def hh_(kind):
    return cluster(kind, 0, 0)[1]
RIGHT_JOINING = {cp for cp, v in LETTERS.items() if v[1] is None and v[0] != 'hamza'}
NON_JOINING = {0x621}


def _letter(cp, form, rasm_override=None, suffix=''):
    isolfina, initmedi, code = LETTERS[cp]
    extras = []
    if code and ('+' in code or code.startswith('n') and code != 'ng'):
        parts = code.split('+')
        extras = [c for c in parts if c.startswith('n') and c != 'ng']
        code = next((c for c in parts if c not in extras), None)
    rasm = rasm_override or (isolfina if form in ('isol', 'fina') else initmedi)
    key = f"{rasm}.{form}"
    rs = dict(RASM[key])
    spec = rs['spec']
    tx, ty = rs['top']
    bx, by = rs.get('bot', (tx, 0))
    code2 = code
    if code == 'fy':
        code2 = None if form in ('isol', 'fina') else '2b'
    if code == 'ng':
        code2 = None
    if code2 in ('1i', '3i'):
        if 'din' in rs:
            x, y = rs['din']
            if code2 == '1i':
                spec += ';' + _diamond(x, y)
            else:
                spec += ';' + ';'.join([_diamond(f"{x}-1.12*q", f"{y}+0.5*q", .9), _diamond(f"{x}+1.12*q", f"{y}+0.5*q", .9),
                                        _diamond(x, f"{y}-1.25*q", .9)])
        else:
            x, y = rs['db']
            s, ext = dots(code2[0] + 'b', x, y)
            spec += ';' + s
            bx, by = x, ext
    elif code2 and code2[0] in '123':
        up = code2[1] == 'a'
        x, y = rs.get('da', rs['top']) if up else rs.get('db', (bx, by))
        s, ext = dots(code2, x, y)
        spec += ';' + s
        if up:
            tx, ty = x, f"max({_fmt(ty)},{ext})" if abs(E._ev(_fmt(x), {'k': 43, 'q': 52}) - E._ev(_fmt(tx), {'k': 43, 'q': 52})) < 200 else ty
            if rasm in ('tah', 'kaf', 'lam'):
                tx, ty = rs['top']
        else:
            bx, by = x, ext
    elif code2 in ('ha', 'ta', 'ma', 'wa'):
        x, y = rs.get('da', rs['top'])
        if rasm == 'alef':
            x, y = 0, 606
        if rasm == 'alefshort':
            x, y = 0, 486
        ye = f"({_fmt(y)})"
        if code2 == 'ha':
            spec += ';' + HAMZA_S.format(x=f"({_fmt(x)})-65", y=f"{ye}-25")
            ext = f"{ye}+178"
        elif code2 == 'ta':
            spec += ';' + TAH_S.format(x=f"({_fmt(x)})-80", y=f"{ye}+18")
            ext = f"{ye}+280"
        elif code2 == 'ma':
            spec += f";w.62 ({_fmt(x)})-150,{ye}+75 ~({_fmt(x)})-75,{ye}+175 ({_fmt(x)}),{ye}+105 ~({_fmt(x)})+75,{ye}+35 ({_fmt(x)})+150,{ye}+135"
            ext = f"{ye}+190"
        else:
            spec += (f";w.55 z ({_fmt(x)})-5,{ye}+170 ~({_fmt(x)})-75,{ye}+170 ({_fmt(x)})-75,{ye}+115 ~({_fmt(x)})-75,{ye}+62 ({_fmt(x)})-5,{ye}+62"
                     f" ~({_fmt(x)})+70,{ye}+62 ({_fmt(x)})+70,{ye}+115 ~({_fmt(x)})+70,{ye}+170;w.55 ({_fmt(x)})+65,{ye}+62 ({_fmt(x)})-115,{ye}+62")
            ext = f"{ye}+200"
        tx, ty = x, ext
    elif code2 == 'va':
        x, y = rs.get('da', rs['top'])
        if rasm in ('lam', 'kaf'):
            x, y = rs['top']
        xe, ye = f"({_fmt(x)})", f"({_fmt(y)})"
        spec += f";w.6 {xe}-72,{ye}+150 {xe},{ye}+58 {xe}+72,{ye}+150"
        tx, ty = x, f"{ye}+170"
    elif code2 == 'vb':
        x, y = rs.get('bot', (bx, by))
        xe, ye = f"({_fmt(x)})+40", f"({_fmt(y)})"
        spec += f";w.6 {xe}-72,{ye}-30 {xe},{ye}-122 {xe}+72,{ye}-30"
        bx, by = x, f"{ye}-140"
    elif code2 == 'hb':
        spec += ';' + HAMZA_S.format(x="-65", y="-235")
        bx, by = 0, -215
    for _c in extras:
        spec, (tx, ty), (bx, by) = _extra(_c, rs, rasm, spec, (tx, ty), (bx, by))
    name = ('uni%04X' % cp) + ('' if form == 'isol' else '.' + form) + suffix
    inf = {k: rs[k] for k in ('aw', 'jl', 'jr', 'l', 'r') if k in rs}
    inf['anchors'] = {'top': (tx, f"({_fmt(ty)})+48"), 'bottom': (bx, f"({_fmt(by)})-30")}
    inf['rkey'] = f"{rasm}.{form}"
    return name, spec, inf


FORMS = {}       # cp -> {form: glyph name}
for _cp, (_if, _im, _code) in LETTERS.items():
    FORMS[_cp] = {}
    for _form in ('isol', 'fina', 'init', 'medi'):
        if _form in ('init', 'medi') and _im is None:
            continue
        if _form == 'fina' and _if == 'hamza':
            continue
        _n, _s, _inf = _letter(_cp, _form)
        AR(_n, _s, uni=[_cp] if _form == 'isol' else [], **_inf)
        FORMS[_cp][_form] = _n

# ---- Mono: optional two-cell forms of the wide letters (ss05) ------------------------------------
WIDE2 = {}
for _cp, (_if, _im, _code) in LETTERS.items():
    if _if in ('seen', 'sad'):
        for _form in ('isol', 'fina', 'init', 'medi'):
            _n, _s, _inf = _letter(_cp, _form, suffix='.w2')
            AR(_n, _s, cells=2, **_inf)
            WIDE2[FORMS[_cp][_form]] = _n

# ---- contextual tall teeth (calt): in a run of teeth every second one is raised --------------
R('behtall.medi', "130,430 130,130 ~130,k 50,k 0,k; 250,k 100,k", aw=250, top=(125, 430), bot=(125, 0),
  da=(125, 430), db=(125, 0))
TEETH = {'init': [], 'medi': [], 'tall': []}
for _cp, (_if, _im, _code) in LETTERS.items():
    if _im == 'beh':
        _nm, _s, _inf = _letter(_cp, 'medi', 'behtall', '.tall')
        AR(_nm, _s, **_inf)
        TEETH['init'].append(FORMS[_cp]['init'])
        TEETH['medi'].append(FORMS[_cp]['medi'])
        TEETH['tall'].append(_nm)

# ---- neighbour forms (calt in the Naskh families): a tooth before final reh / zain is narrower and the reh starts
#      at once, without a flat join; a tooth before final noon / yeh is raised (TEETH['tall']) ----
R('behr.init', "150,335 150,130 ~150,k 75,k 0,k", top=(140, 335), bot=(120, 0), da=(142, 335), db=(120, 0))
R('behr.medi', "110,330 110,130 ~110,k 40,k 0,k; 215,k 85,k", aw=215, top=(105, 330), bot=(105, 0), da=(105, 330), db=(105, 0))
R('rehr.fina', "250,k 232,k ~190,k 190,-30 ~190,-150 10,-150 -40,-150", **{k_: v_ for k_, v_ in RASM['reh.fina'].items() if k_ not in ('spec', 'aw')}, aw=250)
BEHR, REHR, TALL_BEFORE = {}, {}, []
for _cp, (_if, _im, _code) in LETTERS.items():
    if _im == 'beh':
        for _f in ('init', 'medi'):
            if _f in FORMS.get(_cp, {}):
                _nm, _s, _inf = _letter(_cp, _f, 'behr', '.r')
                AR(_nm, _s, **_inf)
                BEHR[FORMS[_cp][_f]] = _nm
    if _if == 'reh' and 'fina' in FORMS.get(_cp, {}):
        _nm, _s, _inf = _letter(_cp, 'fina', 'rehr', '.r')
        AR(_nm, _s, **_inf)
        REHR[FORMS[_cp]['fina']] = _nm
    if _if in ('noon', 'yeh') and 'fina' in FORMS.get(_cp, {}):
        TALL_BEFORE.append(FORMS[_cp]['fina'])

# ---- justification alternates (jalt): final and isolated letters with a long flat body, stretched by 40 % ----
JALT = {}
for _cp, (_if, _im, _code) in LETTERS.items():
    if _if in ('beh', 'feh', 'kaf', 'keheh', 'gaf'):
        for _f in ('isol', 'fina'):
            _b = FORMS.get(_cp, {}).get(_f)
            if _b and _b in INFO and 'adv' not in INFO[_b]:
                AR(_b + '.jalt', INFO[_b]['spec'], **{**{k_: v_ for k_, v_ in INFO[_b].items() if k_ != 'spec'}, 'stretch': 1.4})
                JALT[_b] = _b + '.jalt'

# ---- khanjar tails (ss01): reh and waw end in an upturned hook ----------------------------------
SS01 = {}
_TAILS = [("~190,-150 10,-150 -40,-150", "~185,-110 70,-160 ~-40,-205 -150,-185@0.4"),
          ("~270,-150 70,-150 -20,-150", "~265,-110 140,-160 ~30,-205 -90,-185@0.4")]
for _nm in list(INFO):
    _inf = INFO[_nm]
    for _old, _new in _TAILS:
        if _inf['spec'] and _old in _inf['spec'] and not _inf.get('mark') and 'use:' not in _inf['spec'].split(_old)[0][-1:]:
            if _nm.startswith('uni06') and (len(_nm) == 7 or _nm.endswith('.fina')):
                _i2 = {k: v for k, v in _inf.items() if k not in ('spec', 'reg')}
                AR(_nm + '.ss01', _inf['spec'].replace(_old, _new), **_i2)
                SS01[_nm] = _nm + '.ss01'

# ---- compact ligatures (dlig): lam-meem, lam-hah/jeem/khah, feh-yeh -----------------------------
DLIG = []        # (first glyph, second glyph, ligature)
_hw, _hh = "(95+0.9*k)", "(190+1.4*k)"
_lm = (f"310,600 310,130 ~310,k 230,k 110,k; z 110,k+{_hh} ~110-{_hw},k+{_hh} 110-{_hw},k+{_hh}/2 ~110-{_hw},k 110,k "
       f"~110+{_hw},k 110+{_hw},k+{_hh}/2 ~110+{_hw},k+{_hh}; 115,k 30,k ~-50,k -50,-45 -50,-225")
for _form, _lamf, _conn, _aw in (('isol', 'init', '', None), ('fina', 'medi', "; 400,k 290,k", 400)):
    _kw = dict(aw=_aw, jr=True) if _aw else {}
    AR('lam_meem' + ('' if _form == 'isol' else '.fina'), _lm + _conn, cat='ligature', r=62,
       anchors={'top_1': (310, '606+40'), 'top_2': (110, '2*k+250+1.4*k+40'), 'bottom_1': (310, -30), 'bottom_2': (60, -30)}, **_kw)
    DLIG.append((FORMS[0x644][_lamf], FORMS[0x645]['fina'], 'lam_meem' + ('' if _form == 'isol' else '.fina')))
    for _h, _dot in ((0x62D, ''), (0x62C, ';' + _diamond(262, -45)), (0x62E, ';' + _diamond(215, '292+k+20+q'))):
        _nm = 'lam_%04X' % _h + ('' if _form == 'isol' else '.fina')
        _sp = "400,600 400,350 ~400,292 330,292; " + _jh + _dot + ("; 520,k 30,k" if _aw else '')
        _kw2 = dict(aw=520, jr=True) if _aw else {}
        AR(_nm, _sp, cat='ligature', r=40,
           anchors={'top_1': (400, '606+40'), 'top_2': (215, '292+k+%d' % (40 if _h != 0x62E else 170)),
                    'bottom_1': (420, -30), 'bottom_2': (240, '-185-k-30')}, **_kw2)
        DLIG.append((FORMS[0x644][_lamf], FORMS[_h]['fina'], _nm))
_fy = (loop(450, 220, 'k', 232) + "; 470,k 440,k ~380,k 380,10 ~380,-55 190,-55 ~0,-55 0,40 0,130;"
       + _diamond(450, '2*k+232+20+q') + ';' + dots('2b', 190, '-55-k')[0])
AR('feh_yeh', _fy, cat='ligature', anchors={'top_1': (450, '2*k+232+2*q+60'), 'top_2': (60, 170), 'bottom_1': (450, -30),
                                             'bottom_2': (190, '-55-k-2*q-40')})
DLIG.append((FORMS[0x641]['init'], FORMS[0x64A]['fina'], 'feh_yeh'))

# lam standing on a medial meem (the first two letters of لمح لمس لمع ...)
_mm = RASM['meem.medi']['spec']
AR('lam_meem.init', "190,600 190,k; " + _mm.replace('380,k 0,k', '300,k 0,k'), cat='ligature', aw=300, jl=True, jr=False, r=62,
   anchors={'top_1': (190, '606+40'), 'top_2': (60, '2*k+40'), 'bottom_1': (240, -30), 'bottom_2': (190, '-205-k-30')})
AR('lam_meem.medi', "190,600 190,k; " + _mm, cat='ligature', aw=380, jl=True, jr=True,
   anchors={'top_1': (190, '606+40'), 'top_2': (60, '2*k+40'), 'bottom_1': (300, -30), 'bottom_2': (190, '-205-k-30')})
DLIG.append((FORMS[0x644]['init'], FORMS[0x645]['medi'], 'lam_meem.init'))
DLIG.append((FORMS[0x644]['medi'], FORMS[0x645]['medi'], 'lam_meem.medi'))

# ---- a toothed letter standing on the head of jeem, hah, khah (نج تح نخ): the tooth is raised to the head ----
R('behj.init', "180,500 180,363 ~180,268 90,268 0,268", top=(170, 500), bot=(150, 150), da=(172, 500), db=(150, 150))
R('jeemj.fina', "520,268 425,268; 30,238 ~95,332 205,312 430,268!r; 425,268 ~30,205 12,-10 ~0,-195 240,-195 ~410,-195 500,-115",
  aw=520, top=(215, '300+k'), bot=(240, '-195-k'), da=(215, '300+k'), din=(262, -45))
R('jeemj.medi', "460,268 370,268; 20,245 ~85,335 190,315 375,268!r; 370,268 ~255,k+30 110,k 0,k", aw=460, top=(190, '300+k'),
  bot=(190, 0), da=(190, '300+k'), db=(190, 0))
STACK_TOOTH, STACK_JEEM = {}, {}
for _cp, (_if, _im, _code) in LETTERS.items():
    if _im == 'beh' and _code in ('1a', '2a', '3a', '1b', '2b', '3b', 'fy') and 'init' in FORMS.get(_cp, {}):
        _n, _s, _inf = _letter(_cp, 'init', rasm_override='behj', suffix='.j')
        AR(_n, _s, **_inf)
        STACK_TOOTH[FORMS[_cp]['init']] = _n
    if _if == 'jeem' and _im == 'jeem':
        for _form in ('fina', 'medi'):
            _n, _s, _inf = _letter(_cp, _form, rasm_override='jeemj', suffix='.j')
            AR(_n, _s, **_inf)
            STACK_JEEM[FORMS[_cp][_form]] = _n

# ---- returning yeh: after a letter with nothing under the line, final yeh sweeps back to the right (في على إلى) ----
_ret = "150,k 70,k ~-20,k -20,-80 ~-20,-190 130,-190 430,-190"
RET = {}
for _cp, _dots in ((0x64A, ';' + ';'.join([_diamond("140-1.12*q", -82), _diamond("140+1.12*q", -82)])), (0x649, ''), (0x6CC, '')):
    if _cp in FORMS and 'fina' in FORMS[_cp]:
        _nm = FORMS[_cp]['fina'] + '.ret'
        AR(_nm, _ret + _dots, aw=150, jl=False, jr=True, anchors={'top': (60, '2*k+48'), 'bottom': (200, '-190-k-30')})
        RET[FORMS[_cp]['fina']] = _nm
RET_PREV = []
for _cp, (_if, _im, _code) in LETTERS.items():
    if _im in ('beh', 'feh', 'lam', 'kaf', 'ain', 'seen', 'sad', 'tah', 'jeem', 'keheh', 'gaf') and not (
            _code and (_code.endswith('b') or _code in ('fy', '1i', '3i') or 'b' in _code.split('+')[-1])):
        for _f in ('init', 'medi'):
            if _f in FORMS[_cp]:
                RET_PREV.append(FORMS[_cp][_f])

_n = RASM['tatweel.medi']
AR('uni0640', _n['spec'], uni=[0x640], aw=250, jl=True, jr=True,
   anchors={'top': (125, '2*k+22'), 'bottom': (125, -22)})

# lam-alef ligatures
LIGA = {}
for _alef, _extra in [(0x627, None), (0x622, 'ma'), (0x623, 'ha'), (0x625, 'hb'), (0x671, 'wa')]:
    for _form in ('isol', 'fina'):
        rs = RASM['lamalef.' + _form]
        spec = rs['spec']
        if _extra in ('ha', 'ma', 'wa'):
            spec = spec.replace('-45,606', '-30,500')
        t2y = '606'
        b2y = '0'
        if _extra == 'ha':
            spec += ';' + HAMZA_S.format(x="-30-65", y="500-25")
            t2y = '500+178'
        elif _extra == 'ma':
            spec += ";w.62 -180,575 ~-105,675 -30,605 ~45,535 120,635"
            t2y = '500+190'
        elif _extra == 'wa':
            spec += ";w.55 z -35,670 ~-105,670 -105,615 ~-105,562 -35,562 ~40,562 40,615 ~40,670;w.55 35,562 -145,562"
            t2y = '500+200'
        elif _extra == 'hb':
            spec += ';' + HAMZA_S.format(x="170-65", y="-235")
            b2y = '-215'
        name = 'uni0644%04X' % _alef + ('' if _form == 'isol' else '.fina')
        inf = {k: rs[k] for k in ('aw', 'jl', 'jr', 'l', 'r') if k in rs}
        inf['anchors'] = {'top_1': (330, '606+40'), 'top_2': (-45, f"{t2y}+40"),
                          'bottom_1': (300, -22), 'bottom_2': (170, f"{b2y}-22")}
        inf['rkey'] = 'lamalef.' + _form
        AR(name, spec, cat='ligature', **inf)
        LIGA[(_alef, _form)] = name

# ---------------------------------------------------------------------------
# marks
# ---------------------------------------------------------------------------
def MK(cp, spec, top=None, bottom=None):
    an = {}
    if top is not None:
        an['_top'] = (0, 0)
        an['top'] = (0, top)
    if bottom is not None:
        an['_bottom'] = (0, 0)
        an['bottom'] = (0, bottom)
    return AR('uni%04X' % cp, spec, uni=[cp], cat='mark', mark=True, anchors=an)


_DAMMA = "w.55 z 20,195 ~-42,195 -42,138 ~-42,85 20,85 ~82,85 82,138 ~82,195; w.55 82,138 82,92 ~82,25 -10,25 -72,25"
MK(0x64E, "w.62 -95,42 95,112", top=165)
MK(0x650, "w.62 -95,-112 95,-42", bottom=-165)
MK(0x64F, _DAMMA, top=240)
MK(0x64B, "w.6 -95,35 95,95; w.6 -95,135 95,195", top=245)
MK(0x64D, "w.6 -95,-195 95,-115; w.6 -95,-95 95,-35", bottom=-245)
MK(0x64C, _DAMMA.replace('20,', '-30,').replace('-42,', '-92,').replace('82,', '32,').replace('-10,', '-60,').replace('-72,', '-122,')
   + "; w.55 150,175 150,95 ~150,28 85,28", top=240)
MK(0x652, "w.55 ring 0,118 62,62", top=225)
MK(0x651, "w.55 100,170 100,88 ~100,45 50,45 ~0,45 0,88 0,152; w.55 0,152 0,88 ~0,45 -50,45 ~-100,45 -100,88 -100,145",
   top=205)
MK(0x653, "w.62 -150,62 ~-75,162 0,92 ~75,22 150,122", top=175)
MK(0x654, "use:uni0621|0.55,0.55,-65,-25", top=200)
MK(0x655, "use:uni0621|0.55,0.55,-65,-215", bottom=-215)
MK(0x670, "w.6 0,28 0,235", top=265)
MK(0x656, "w.6 0,-235 0,-28", bottom=-265)
MK(0x657, "use:uni064F|-1,-1,0,265", top=265)
MK(0x658, "w.55 -72,165 -72,105 ~-72,42 0,42 ~72,42 72,105 72,165; " + _diamond(0, 150, .6), top=215)
MK(0x615, "w.45 ring 20,60 62,44;w.45 -28,22 -28,193", top=215)
MK(0x6E1, "w.6 -100,150 60,150!r; w.6 56,150 ~0,45 -60,45 -110,45", top=215)
MK(0x6DA, "use:uni062C|0.36,0.36,-90,150", top=300)
MK(0x6DC, "use:uni0633.init|0.36,0.36,-85,30", top=160)
MK(0x6E3, "use:uni0633.init|0.36,0.36,-85,-140", bottom=-165)
MK(0x6E2, "use:uni0645|0.4,0.4,-75,130", top=290)
MK(0x6ED, "use:uni0645|0.4,0.4,-75,-140", bottom=-270)
MK(0x6D8, "use:uni0645.init|0.42,0.42,-45,70", top=200)
MK(0x6E8, "use:uni0646|0.36,0.36,-85,110", top=250)
MK(0x6E7, "use:uni0649|0.34,0.34,-95,85", top=240)
MK(0x6D9, "use:uni06440627|0.36,0.36,-58,20", top=300)
MK(0x6E4, "w.62 -150,62 ~-75,162 0,92 ~75,22 150,122", top=175)
MK(0x6DF, "w.5 ring 0,110 55,62", top=205)
MK(0x6E0, "w.5 z -42,45 42,45 42,190 -42,190", top=225)
MK(0x6DB, ';'.join([_diamond(-58, 70, .55), _diamond(58, 70, .55), _diamond(0, 160, .55)]), top=220)
MK(0x6EB, "w.5 z -62,105 0,165 62,105 0,45", top=200)
MK(0x6EA, "w.5 z -62,-105 0,-45 62,-105 0,-165", bottom=-200)
MK(0x6EC, "oval 0,105 50,50", top=185)

# small spacing letters
AR('uni06E5', "use:uni0648|0.5,0.5,20,-40", uni=[0x6E5], l=20, r=20)
AR('uni06E6', "use:uni0649|0.45,0.45,0,-60", uni=[0x6E6], l=20, r=20)

# ---------------------------------------------------------------------------
# digits (Arabic-Indic and Extended Arabic-Indic), tabular
# ---------------------------------------------------------------------------
_STEM = "55,660!h 120,0!h"
DIG = {
    0: _diamond(0, 290, 1.15),
    1: "40,660!h 112,0!h",
    2: _STEM + "; 60,640 ~92,482 202,482 ~322,482 338,655",
    3: _STEM + "; 60,640 ~78,505 150,505 ~212,505 222,625; 222,625 ~232,505 302,505 ~372,505 384,655",
    4: "330,632 ~60,632 60,497 ~60,366 270,366; 270,366 ~50,366 50,196 ~50,k 340,k",
    5: "z 200,575 ~30,575 30,300 ~30,k 200,k ~370,k 370,300 ~370,575",
    6: "45,618 330,642 308,0!h",
    7: "30,660!h 195,0!h; 360,660!h 195,0!h",
    8: "30,0!h 195,660!h; 360,0!h 195,660!h",
    9: "z 190,655 ~60,655 60,508 ~60,365 190,365 ~320,365 320,508 ~320,655; 320,520 308,0!h",
}
PDIG = dict(DIG)
PDIG[4] = "70,660 112,0!h; 335,645 ~112,645 112,538 ~112,432 322,432"
PDIG[5] = "z 200,600 ~30,600 30,270 ~30,k 125,k ~200,k 200,150 ~200,k 275,k ~370,k 370,270 ~370,600"
PDIG[6] = "82,545 ~82,655 196,655 ~312,655 312,530 ~312,330 72,0!h"
for _i in range(10):
    AR('uni%04X' % (0x660 + _i), DIG[_i], uni=[0x660 + _i], adv=556, tab=True,
       anchors={'top': (195, 700), 'bottom': (195, -22)})
    AR('uni%04X' % (0x6F0 + _i), PDIG[_i], uni=[0x6F0 + _i], adv=556, tab=True,
       anchors={'top': (195, 700), 'bottom': (195, -22)})

AR('uni06F6.urdu', DIG[6], adv=556, tab=True, anchors={'top': (195, 700), 'bottom': (195, -22)})
AR('uni06F7.urdu', "325,655 58,165 ~30,k 115,k 345,k", adv=556, tab=True, anchors={'top': (195, 700), 'bottom': (195, -22)})

# ---------------------------------------------------------------------------
# punctuation and symbols
# ---------------------------------------------------------------------------
G(0x60C, "use:comma|-1,-1,0,2*dt", 84, 84, script='arab', slant=False)
G(0x61B, "use:comma|-1,-1,0,X-1.7*dt+0*dt; dot 0,dt", 84, 84, script='arab', slant=False)
G(0x61F, "use:question|-1,1,378,0", 44, 44, script='arab', slant=False)
G(0x6D4, "0,k 190,k", 60, 60, script='arab', slant=False)
G(0x66B, "150,150 150,40 ~150,-110 20,-110 -20,-110", 50, 60, script='arab', slant=False)
G(0x66C, "use:comma|1,1,0,C-2*dt", 70, 70, script='arab', slant=False)
G(0x66A, _diamond(60, 590, 1.0) + ';' + _diamond(430, 90, 1.0) + "; w.9 80,-12!h 410,C+12!h", 40, 40,
  script='arab', slant=False)
G(0x66D, "f 220,640 280,430 500,430 322,300 390,90 220,220 50,90 118,300 -60,430 160,430", 50, 50,
  script='arab', slant=False)
G(0x6DE, "w.55 z 60,60 560,60 560,560 60,560; w.55 z 310,-44 664,310 310,664 -44,310; w.5 ring 310,310 105,105",
  50, 50, script='arab', slant=False)
G(0x6E9, "w.6 70,0 70,400 ~70,560 255,700 ~440,560 440,400 440,0; w.6 0,k 510,k; w.5 180,k 180,330 ~180,420 255,480 ~330,420 330,330 330,k",
  40, 40, script='arab', slant=False)
G(0x6DD, "w.55 ring 480,300 440,440; w.4 ring 480,300 345,345", 40, 40, script='arab', slant=False)
G(0xFD3E, "w.8 200,760 ~0,570 0,270 ~0,-30 200,-220; " + _diamond(-10, 270, 1.0) + "; w.6 215,640 ~90,500 90,270 ~90,40 215,-100",
  50, 10, script='arab', slant=False)
G(0xFD3F, "w.8 0,760 ~200,570 200,270 ~200,-30 0,-220; " + _diamond(210, 270, 1.0) + "; w.6 -15,640 ~110,500 110,270 ~110,40 -15,-100",
  10, 50, script='arab', slant=False)
G(0x262A, "w.9 430,560 ~330,650 220,650 ~0,650 0,350 ~0,50 220,50 ~330,50 430,140;"
          "f 420,470 452,385 542,385 470,330 497,244 420,296 343,244 370,330 298,385 388,385", 50, 50, slant=False)

# ---------------------------------------------------------------------------
# word composition (for U+FDF0.. ligatures and small Quranic signs)
# ---------------------------------------------------------------------------
_REGSTYLE = None


def _metrics(name):
    """regular-weight (dx, advance) of a glyph, used to set words"""
    global _REGSTYLE
    inf = INFO[name]
    if 'reg' not in inf:
        if _REGSTYLE is None:
            _REGSTYLE = Style()
        st = _REGSTYLE
        shapes = E.parse(inf['spec'], st.ns, lambda n: REG[n].spec)
        bb = E.bounds(E.outline(shapes, st.apen))
        dx = 0.0 if inf.get('jl') else inf.get('l', 45) - bb[0]
        adv = (inf['aw'] + dx) if inf.get('jr') else (bb[2] + dx + inf.get('r', 45))
        inf['reg'] = (dx, adv)
    return inf['reg']


def shape_word(word):
    """logical string -> list of glyph names (with lam-alef ligation)"""
    cps = [ord(c) for c in word]
    out = []
    i = 0
    n = len(cps)

    def joins_left(cp):   # can connect to the following letter
        return cp in LETTERS and cp not in RIGHT_JOINING and cp not in NON_JOINING

    while i < n:
        cp = cps[i]
        prev = cps[i - 1] if i > 0 else None
        nxt = cps[i + 1] if i + 1 < n else None
        jr = prev is not None and joins_left(prev) and cp not in NON_JOINING
        jl = nxt is not None and joins_left(cp) and nxt not in NON_JOINING
        if cp == 0x644 and nxt in (0x627, 0x622, 0x623, 0x625, 0x671):
            out.append(LIGA[(nxt, 'fina' if jr else 'isol')])
            i += 2
            continue
        form = {(False, False): 'isol', (True, False): 'fina', (False, True): 'init', (True, True): 'medi'}[(jr, jl)]
        out.append(FORMS[cp][form])
        i += 1
    return out


def set_line(text, s, x_right, y):
    """place words right-to-left ending at x_right; returns (spec, x_left)"""
    items = []
    cur = x_right
    for wi, word in enumerate(text.split(' ')):
        if wi:
            cur -= 230 * s
        for name in shape_word(word):
            dx, adv = _metrics(name)
            cur -= adv * s
            items.append(f"use:{name}|{s},{s},{cur + dx * s:.1f},{y}")
    return ';'.join(items), cur


def line_width(text, s):
    _, left = set_line(text, s, 0, 0)
    return -left


def WORD(cp, lines, s, y0=0, lead=560, extra=None, name=None):
    widths = [line_width(t, s) for t in lines]
    W = max(widths)
    parts = []
    for i, t in enumerate(lines):
        y = y0 + (len(lines) - 1 - i) * lead * s
        sp, _ = set_line(t, s, W - (W - widths[i]) / 2, y)
        parts.append(sp)
    spec = ';'.join(parts)
    if extra:
        spec += ';' + extra(W)
    AR(name or ('uni%04X' % cp), spec, uni=[cp], l=45, r=45, cat='base',
       anchors={'top': (W / 2, 640), 'bottom': (W / 2, -22)})


def _allah_marks(W, s=1.0, x=None, y=0):
    # shadda + superscript alef over the second lam
    x = W - 150 - 240 - 420 + 150 + 15 if x is None else x
    return (f"w.5 {x+70},{y+790} {x+70},{y+745} ~{x+70},{y+715} {x+35},{y+715} ~{x},{y+715} {x},{y+745} {x},{y+780};"
            f"w.5 {x},{y+780} {x},{y+745} ~{x},{y+715} {x-35},{y+715} ~{x-70},{y+715} {x-70},{y+745} {x-70},{y+775};"
            f"w.55 {x},{y+805} {x},{y+870}")


WORD(0xFDF2, ["الله"], 1.0, extra=lambda W: _allah_marks(W, x=W - _metrics('uni0627')[1] - 420 - 240 + 150, y=-94))
WORD(0xFDF0, ["صلے"], 0.8)
WORD(0xFDF1, ["قلے"], 0.8)
WORD(0xFDF3, ["اكبر"], 0.8)
WORD(0xFDF4, ["محمد"], 0.8)
WORD(0xFDF5, ["صلعم"], 0.8)
WORD(0xFDF6, ["رسول"], 0.8)
WORD(0xFDF7, ["عليه"], 0.8)
WORD(0xFDF8, ["وسلم"], 0.8)
WORD(0xFDF9, ["صلى"], 0.8)
WORD(0xFDFC, ["ريال"], 0.8)
WORD(0xFDFA, ["صلى الله", "عليه وسلم"], 0.42, y0=60, lead=820)
WORD(0xFDFB, ["جل", "جلاله"], 0.42, y0=60, lead=820)
WORD(0xFDFD, ["بسم الله", "الرحمن الرحيم"], 0.42, y0=60, lead=820)
MK(0x6D6, set_line("صلى", 0.3, 150, 60)[0], top=320)
MK(0x6D7, set_line("قلى", 0.3, 150, 60)[0], top=320)

# honorific signs (small abbreviations set above the name they follow)
MK(0x610, set_line("صلعم", 0.24, 170, 70)[0], top=300)
MK(0x611, set_line("عم", 0.3, 110, 80)[0], top=300)
MK(0x612, set_line("رح", 0.3, 120, 120)[0], top=300)
MK(0x613, set_line("رض", 0.3, 130, 110)[0], top=300)
MK(0x614, "w.55 -210,70 ~-210,140 -150,140 ~-90,140 -90,70 130,70 ~210,70 210,150", top=220)

# ---------------------------------------------------------------------------
# presentation forms -> same glyphs (Arabic Presentation Forms-A/B)
# ---------------------------------------------------------------------------
_TAG = {'<isolated>': 'isol', '<final>': 'fina', '<initial>': 'init', '<medial>': 'medi'}
for _cp in list(range(0xFB50, 0xFDF0)) + list(range(0xFE70, 0xFEFD)):
    dec = ud.decomposition(chr(_cp)).split()
    if len(dec) < 2 or dec[0] not in _TAG:
        continue
    form = _TAG[dec[0]]
    cps = [int(h, 16) for h in dec[1:]]
    if len(cps) == 1 and cps[0] in FORMS and form in FORMS[cps[0]]:
        REG[FORMS[cps[0]][form]].uni.append(_cp)
    elif len(cps) == 2 and cps[0] == 0x644 and (cps[1], form) in LIGA:
        REG[LIGA[(cps[1], form)]].uni.append(_cp)


# ---- digits inside the end-of-ayah sign: small fixed-width figures, positioned by GPOS (Sans families) ----
AYAH_DW = 190
AYAH_DIGITS = {}
for _n in ['uni%04X' % c for c in list(range(0x660, 0x66A)) + list(range(0x6F0, 0x6FA))] + ['uni06F6.urdu', 'uni06F7.urdu']:
    if _n in INFO:
        AR(_n + '.ayah', f"use:{_n}|0.34,0.34,0,121", adv=AYAH_DW)
        AYAH_DIGITS[_n] = _n + '.ayah'


# Sindhi signs: ampersand and the postposition men
AR('uni06FD', "use:uni0621|1,1,0,95; w.55 88,100 88,-30; w.55 165,100 165,-30", uni=[0x6FD], l=42, r=42,
   anchors={'top': (120, 500), 'bottom': (125, -60)})
AR('uni06FE', RASM['meem.isol']['spec'] + "; w.55 190,2*k+255 190,2*k+385; w.55 272,2*k+255 272,2*k+385", uni=[0x6FE],
   anchors={'top': (230, '2*k+440'), 'bottom': (120, -30)})
