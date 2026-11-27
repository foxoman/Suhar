"""Styles, glyph registry and glyph generation for RetroUI Sans."""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from fontTools import agl

from . import engine as E

UPM = 1000
CAP = 700
XH = 520
DESC = -200
ASCENT = 940       # line metrics (all families)
DESCENT = -360
MONO_W = 600
ITALIC_DEG = 11.0
SKEW_Y = 260       # italics are sheared about the middle of the x-height


WEIGHT_NAMES = {300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold', 900: 'Black'}


def lerp(a, b, t):
    return a + (b - a) * t


class Style:
    """One point of the design space.

    family : 'Sans' | 'Mono'
    wght   : 400..700
    italic : bool
    opsz   : -1 (8 pt caption master) .. 0 (text, default) .. +1 (display master)
    compat : keep stroke overlaps and exact point structure (variable masters)
    """

    def __init__(self, family='Sans', wght=400, italic=False, opsz=0.0, compat=False, width=1.0):
        self.width = width
        self.cond = width < 0.99
        self.arx = 0.9 if self.cond else 1.0      # Arabic is condensed less than Latin
        self.family = family
        self.mono = family == 'Mono'
        self.wght = wght
        self.italic = italic
        self.opsz = opsz
        self.compat = compat
        t = (wght - 400) / 300.0
        self.t = t
        a = lerp(44, 74, t)
        hb = lerp(38, 61, t)
        sbs, sba, xs = lerp(1.0, 0.86, t), 0.0, lerp(1.0, 0.94, t)
        if self.mono:
            a *= lerp(1.0, 0.92, t)
            hb *= lerp(1.0, 0.94, t)
            xs = 1.0
        if opsz < 0:      # caption: sturdier, looser, lower contrast
            k = -opsz
            a *= 1 + 0.05 * k
            hb *= 1 + 0.11 * k
            sba += 16 * k
            xs *= 1 + 0.03 * k
        elif opsz > 0:    # display: finer, tighter
            k = opsz
            a *= 1 - 0.04 * k
            hb *= 1 - 0.08 * k
            sba -= 9 * k
            xs *= 1 - 0.01 * k
        if self.cond:
            xs *= width
            sbs *= 0.86
            a *= 0.97
        self.a, self.hb, self.sbs, self.sba, self.xs = a, hb, sbs, sba, xs
        self.o = 10.0
        self.dt = a * 1.16
        self.tan = math.tan(math.radians(ITALIC_DEG)) if italic else 0.0
        self.pen = E.Pen(a, hb)
        r = (a + hb) / 2
        self.r = r
        # Arabic: a broad-nib (Naskh) pen, long axis at 65 degrees: full horizontals, lighter verticals
        ta_ = t if t <= 1 else 1 + (t - 1) * 0.55        # past Bold the Arabic pen grows more slowly: counters stay open
        ra_ = (lerp(44, 74, ta_) + lerp(38, 61, ta_)) / 2 * (r / ((lerp(44, 74, t) + lerp(38, 61, t)) / 2))
        self.apen = E.Pen(ra_ * lerp(1.06, 1.12, ta_), ra_ * lerp(0.88, 0.90, ta_), 65.0)
        self.ra = self.apen.extent()[1]          # half thickness of the baseline stroke
        C, X, D, o = CAP, XH, DESC, self.o
        self.ns = dict(C=C, X=X, D=D, a=a, hb=hb, o=o, r=r, dt=self.dt, t=t,
                       b=hb, x=X - hb, c=C - hb, d=D + hb,
                       bo=hb - o, xo=X - hb + o, co=C - hb + o, do=D + hb - o,
                       M=C / 2, W=MONO_W, AS=ASCENT, DS=DESCENT,
                       mono=1.0 if self.mono else 0.0, K=0.70, k=self.ra, q=self.ra * lerp(1.2, 0.98, t))

    def set_naskh(self):
        """Suhar Naskh: Arabic written with a contrasted reed pen (thick baseline, lighter uprights, thin up-strokes),
        rounder curves and pointed terminals.  The Latin is unchanged."""
        self.naskh = True
        t = self.t
        ta_ = t if t <= 1 else 1 + (t - 1) * 0.55
        ra_ = (lerp(44, 74, ta_) + lerp(38, 61, ta_)) / 2 * (self.r / ((lerp(44, 74, t) + lerp(38, 61, t)) / 2))
        self.apen = E.Pen(ra_ * lerp(1.36, 1.40, ta_), ra_ * lerp(0.50, 0.56, ta_), 62.0)
        self.ra = self.apen.extent()[1]
        self.ns['k'] = self.ra
        self.ns['q'] = self.ra * lerp(1.02, 0.86, t)
        return self

    @property
    def style_name(self):
        w = WEIGHT_NAMES[self.wght]
        if self.italic:
            return 'Italic' if w == 'Regular' else w + ' Italic'
        return w

    def skew(self, x, y):
        return (x + (y - SKEW_Y) * self.tan, y)


@dataclass
class GDef:
    name: str
    uni: list
    spec: str | None = None
    sb: tuple = (60, 60)
    mono: str | None = None          # alternative skeleton for the Mono family
    ital: str | None = None          # alternative skeleton for the italics
    fn: object = None                # programmatic: fn(style) -> GlyphOut-like dict
    comp: tuple | None = None        # (base, [mark names]) precomposed
    cat: str = 'base'
    anchors: dict | None = None      # explicit anchors {name: (xexpr, yexpr)} in skeleton space
    tab: bool = False                # tabular width (figures)
    slant: bool = True               # participates in italic shear
    fit: bool = True                 # may be compressed to fit the Mono cell
    adv: object = None               # fixed advance (number) in proportional fonts
    script: str = 'latn'
    kern: str | None = None          # kerning group override (name of the glyph to share with)
    top: str | None = None           # 'C' or 'X' to force top-anchor level
    pen: tuple | None = None         # (a_scale, hb_scale) pen override
    xs: bool = True                  # apply weight x-scale


@dataclass
class GlyphOut:
    name: str
    uni: list
    contours: list = field(default_factory=list)
    advance: float = 0
    anchors: dict = field(default_factory=dict)
    components: list = field(default_factory=list)   # [(base, dx, dy)]
    cat: str = 'base'
    script: str = 'latn'
    ink: tuple | None = None


REG: dict = {}
ORDER: list = []


def gname(cp: int) -> str:
    if cp < 0x250 and cp in agl.UV2AGL:
        n = agl.UV2AGL[cp]
        return n if isinstance(n, str) else n[0]
    return ('uni%04X' if cp <= 0xFFFF else 'u%05X') % cp


def G(key, spec=None, l=60, r=60, **kw):
    """register a glyph.  key: a character, a code point, or a glyph name"""
    if isinstance(key, int):
        uni, name = [key], gname(key)
    elif isinstance(key, str) and len(key) == 1:
        uni, name = [ord(key)], gname(ord(key))
    else:
        uni, name = [], key
    extra = kw.pop('also', None)
    if extra:
        uni = uni + [ord(c) if isinstance(c, str) else c for c in extra]
    name = kw.pop('name', name)
    if 'uni' in kw:
        u = kw.pop('uni')
        uni = [u] if isinstance(u, int) else list(u)
    d = GDef(name, uni, spec, (l, r), **kw)
    if name not in REG:
        ORDER.append(name)
    REG[name] = d
    return d


def lookup(name):
    if len(name) == 1 and gname(ord(name)) in REG:
        name = gname(ord(name))
    return REG[name].spec


# --------------------------------------------------------------------------
def _shapes(d: GDef, st: Style, xs: float):
    spec = d.mono if (st.mono and d.mono) else (d.ital if (st.italic and d.ital) else d.spec)
    _la = getattr(st, 'latalt', None)           # a family with its own Latin drawings: {glyph name: spec}
    _ls = getattr(st, 'latserif', None)         # ... and with serifs added to the shared skeletons: {glyph name: spec}
    _lm = getattr(st, 'latmap', None)           # ... and its own lower-case proportions: y -> y
    own = bool(_la and d.name in _la)
    _u = spec.strip()[4:].split('|')[0] if (spec and spec.strip().startswith('use:') and ';' not in spec) else None
    alias = bool(_la and _u and (gname(ord(_u)) if len(_u) == 1 else _u) in _la)     # a copy of a redrawn letter
    if own:
        spec = _la[d.name]
    elif _ls and d.name in _ls:
        spec = spec + '; ' + _ls[d.name]

    def look(n):
        if len(n) == 1 and gname(ord(n)) in REG:
            n = gname(ord(n))
        if _la and n in _la:
            return _la[n]
        if _ls and n in _ls:
            return REG[n].spec + '; ' + _ls[n]
        return REG[n].spec
    shapes = E.parse(spec, st.ns, look if (_la or _ls) else lookup)
    if _lm and not own and not alias and _is_lower(d):
        for s in shapes:
            _ys = [n.y for n in s.nodes]
            if s.kind == 'fill' and min(_ys) > 300 and max(_ys) - min(_ys) < 260:      # a dot stays where it is
                continue
            else:
                s.transform(lambda x, y: (x, _lm(y)))
    if xs != 1.0:
        for s in shapes:
            s.transform(lambda x, y: (x * xs, y))
    return shapes


def _is_lower(d):
    import unicodedata
    return bool(d.uni) and unicodedata.category(chr(d.uni[0])) == 'Ll'


def _pen(d: GDef, st: Style):
    if d.pen:
        return E.Pen(st.a * d.pen[0], st.hb * d.pen[1])
    return st.pen


def make_skeleton_glyph(d: GDef, st: Style) -> GlyphOut:
    pen = _pen(d, st)
    xs = st.xs if d.xs else 1.0
    shapes = _shapes(d, st, xs)
    cs = E.outline(shapes, pen)
    bb = E.bounds(cs)
    is_mark = d.cat == 'mark'
    l, r = (getattr(st, 'latsb', None) or {}).get(d.name, d.sb)
    _sf = getattr(st, 'latsbf', None)
    if _sf:
        l, r = l * _sf(d.name), r * _sf(d.name)
    l = l * st.sbs + st.sba
    r = r * st.sbs + st.sba
    if bb is None:
        return GlyphOut(d.name, d.uni, [], d.adv or 0, {}, [], d.cat, d.script)
    if st.mono and not is_mark:
        msb = lerp(30, 20, st.t)
        limit = MONO_W - 2 * msb
        for _ in range(4):
            ink = bb[2] - bb[0]
            if not d.fit or ink <= limit + 0.5:
                break
            core = max(ink - 2 * pen.a, 1)
            f = max((limit - 2 * pen.a) / core, 0.2)
            xs *= f
            shapes = _shapes(d, st, xs)
            cs = E.outline(shapes, pen)
            bb = E.bounds(cs)
        ink = bb[2] - bb[0]
        adv = MONO_W
        bias = max(-20, min(20, (l - r) / 2))
        dx = (adv - ink) / 2 - bb[0] + bias
    elif is_mark:
        adv = 0
        dx = 0.0
    else:
        ink = bb[2] - bb[0]
        if d.tab:
            adv = round((lerp(556, 572, st.t) + 2 * st.sba) * (0.5 + 0.5 * st.width if st.cond else 1.0) * (st.width if st.cond else 1.0) ** 0.5)
            dx = (adv - ink) / 2 - bb[0]
        elif d.adv is not None:
            adv = d.adv
            dx = (adv - ink) / 2 - bb[0]
        else:
            adv = round(l + ink + r)
            dx = l - bb[0]
    dx = round(dx)
    if st.italic and d.slant:
        for s in shapes:
            s.transform(st.skew)
        cs = E.outline(shapes, pen)
    cs = E.shift(cs, dx)
    if not st.compat:
        cs = E.union(cs)
    g = GlyphOut(d.name, d.uni, cs, adv, {}, [], d.cat, d.script)
    g.ink = (bb[0] + dx, bb[1], bb[2] + dx, bb[3])
    # anchors
    sk = st.skew if (st.italic and d.slant) else (lambda x, y: (x, y))
    if d.anchors:
        for an, (ax, ay) in d.anchors.items():
            x = E._ev(str(ax), st.ns) * xs + dx
            y = E._ev(str(ay), st.ns)
            g.anchors[an] = sk(x, y)
    if d.cat == 'base' and d.script == 'latn' and not (d.anchors and 'top' in d.anchors):
        cx = (g.ink[0] + g.ink[2]) / 2
        _xh = getattr(st, 'xh', XH)
        top = CAP if (d.top == 'C' or (d.top is None and bb[3] > _xh + 60)) else _xh
        g.anchors.setdefault('top', sk(cx, top))
        g.anchors.setdefault('bottom', sk(cx, 0))
    return g


def build_glyphs(st: Style, only=None) -> dict:
    out: dict = {}
    names = [n for n in ORDER if (only is None or n in only)]
    # pass 1: outlines
    for n in names:
        d = REG[n]
        if d.comp:
            continue
        if d.fn:
            g = d.fn(st, d)
            if g is None:
                continue
            g.name, g.uni, g.cat, g.script = d.name, d.uni, d.cat, d.script
            if not st.compat and g.contours and getattr(g, 'needs_union', True):
                g.contours = E.union(g.contours)
        else:
            g = make_skeleton_glyph(d, st)
        out[n] = g
    # pass 2: composites
    for n in names:
        d = REG[n]
        if not d.comp:
            continue
        base, marks = d.comp
        if base not in out or any(m not in out for m in marks):
            continue
        bg = out[base]
        g = GlyphOut(d.name, d.uni, [], bg.advance, dict(bg.anchors), [(base, 0, 0)], d.cat, d.script)
        g.ink = bg.ink
        for m in marks:
            mg = out[m]
            cls = next((k[1:] for k in mg.anchors if k.startswith('_') and k[1:] in g.anchors), None)
            if cls is None:
                continue
            ax, ay = g.anchors[cls]
            mx, my = mg.anchors['_' + cls]
            dx, dy = round(ax - mx), round(ay - my)
            g.components.append((m, dx, dy))
            if cls in mg.anchors:      # stacking
                g.anchors[cls] = (mg.anchors[cls][0] + dx, mg.anchors[cls][1] + dy)
        out[n] = g
    return out
