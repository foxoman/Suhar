"""RetroUI Sans outline engine.

Glyphs are authored as *skeletons* (centre lines) in a small text language and
expanded to outlines with an elliptical pen.  Because weight, contrast, width,
slant and optical size are parameters of the expansion rather than of the
drawing, every style of the family is generated from one set of drawings, and
the point structure is identical in every master (variable-font compatible).

Skeleton language
-----------------
A glyph spec is a string of items separated by ';'.  Each item is a list of
whitespace separated tokens.  Leading option tokens:

    z            closed stroke
    f            filled polygon (no stroke)
    w<num>       stroke width multiplier for this item      (w0.8)
    m<num>       monoline: use a round pen of this many units radius scale
    k<num>       corner tension for '~' points in this item (default 0.60)
    dot          square dot,     "dot x,y [scale]"
    rect         filled box,     "rect x0,y0 x1,y1"
    oval         filled ellipse, "oval cx,cy rx,ry"
    ring         stroked ellipse,"ring cx,cy rx,ry"
    use:NAME     include another glyph's skeleton, "use:O" or
                 "use:six|sx,sy,dx,dy" (scale then translate)

Point tokens are "x,y" where x and y are arithmetic expressions over the
metric variables below (no spaces).  A leading '~' makes the point a *rounded
corner*: the path does not pass through it, but is tangent to both sides, like
a TrueType off-curve point.  Suffixes:

    !h !v !r !b  end cap: horizontal cut, vertical cut, round, butt (default)
    !<deg>       end cap cut at the given angle
    @<num>       stroke width multiplier at this point (tapering)

Metric variables: C cap height, X x-height, D descender, a (half stem),
hb (half horizontal stroke), o overshoot, and the centre-line levels
b, x, c, d (flat strokes sitting on baseline / x-height / cap height /
descender) and bo, xo, co, do (the same with overshoot for round strokes),
dt half dot size.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Callable

import pathops
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen

KAPPA = 0.5522847498


# --------------------------------------------------------------------------
# skeleton data model
# --------------------------------------------------------------------------
@dataclass
class Node:
    x: float
    y: float
    cc: bool = False        # rounded-corner control
    w: float = 1.0          # width multiplier
    cap: str | None = None  # end cap
    k: float = 0.60


@dataclass
class Shape:
    kind: str                # 'stroke' | 'fill'
    nodes: list
    closed: bool = False
    w: float = 1.0           # stroke width multiplier
    mono: float | None = None  # monoline radius scale (round pen) or None
    scale_w: bool = False

    def copy(self):
        return Shape(self.kind, [Node(n.x, n.y, n.cc, n.w, n.cap, n.k) for n in self.nodes],
                     self.closed, self.w, self.mono, self.scale_w)

    def transform(self, fn):
        for n in self.nodes:
            n.x, n.y = fn(n.x, n.y)
        return self


_code_cache: dict = {}


def _ev(expr: str, ns: dict) -> float:
    code = _code_cache.get(expr)
    if code is None:
        code = _code_cache[expr] = compile(expr, '<skel>', 'eval')
    return float(eval(code, {'__builtins__': {}, 'min': min, 'max': max, 'abs': abs}, ns))


def _parse_point(tok: str, ns: dict, k: float) -> Node:
    cc = tok.startswith('~')
    if cc:
        tok = tok[1:]
    cap = None
    w = 1.0
    # suffixes
    while True:
        i = max(tok.rfind('!'), tok.rfind('@'))
        if i <= 0:
            break
        suf = tok[i:]
        tok = tok[:i]
        if suf[0] == '!':
            cap = suf[1:]
        else:
            w = float(suf[1:])
    xs, ys = tok.split(',')
    return Node(_ev(xs, ns), _ev(ys, ns), cc, w, cap, k)


def parse(spec: str, ns: dict, lookup: Callable[[str], str] | None = None, _depth=0) -> list:
    """Resolve a glyph spec to a list of Shapes using metric namespace ns."""
    shapes = []
    for item in spec.split(';'):
        toks = item.split()
        if not toks:
            continue
        closed = False
        fill = False
        wmul = 1.0
        mono = None
        k = ns.get('K', 0.60)
        while toks:
            t = toks[0]
            if t == 'z':
                closed = True
            elif t == 'f':
                fill = True
                closed = True
            elif t[0] == 'w' and _isnum(t[1:]):
                wmul = float(t[1:])
            elif t[0] == 'm' and _isnum(t[1:]):
                mono = float(t[1:])
            elif t[0] == 'k' and _isnum(t[1:]):
                k = float(t[1:])
            else:
                break
            toks = toks[1:]
        if not toks:
            continue
        head = toks[0]
        if head.startswith('use:'):
            ref = head[4:]
            tr = (1, 1, 0, 0)
            if '|' in ref:
                ref, trs = ref.split('|')
                tr = tuple(_ev(e, ns) for e in trs.split(','))
            sub = parse(lookup(ref), ns, lookup, _depth + 1)
            sx, sy, dx, dy = tr
            for s in sub:
                s.transform(lambda x, y: (x * sx + dx, y * sy + dy))
                if sx * sy != 1 and abs(sx) == abs(sy) and abs(sx) != 1:
                    s.w *= abs(sx) ** 0.5   # scaled-down copies keep some weight
                s.w *= wmul
            shapes += sub
            continue
        if head == 'dot':
            p = _parse_point(toks[1], ns, k)
            sc = float(toks[2]) if len(toks) > 2 else 1.0
            r = ns['dt'] * sc
            shapes.append(Shape('fill', [Node(p.x - r, p.y - r), Node(p.x + r, p.y - r),
                                         Node(p.x + r, p.y + r), Node(p.x - r, p.y + r)], True))
            continue
        if head == 'rect':
            p = _parse_point(toks[1], ns, k)
            q = _parse_point(toks[2], ns, k)
            shapes.append(Shape('fill', [Node(p.x, p.y), Node(q.x, p.y), Node(q.x, q.y), Node(p.x, q.y)], True))
            continue
        if head in ('oval', 'ring'):
            p = _parse_point(toks[1], ns, k)
            q = _parse_point(toks[2], ns, k)
            kk = KAPPA
            nodes = [Node(p.x + q.x, p.y), Node(p.x + q.x, p.y + q.y, True, k=kk), Node(p.x, p.y + q.y),
                     Node(p.x - q.x, p.y + q.y, True, k=kk), Node(p.x - q.x, p.y),
                     Node(p.x - q.x, p.y - q.y, True, k=kk), Node(p.x, p.y - q.y),
                     Node(p.x + q.x, p.y - q.y, True, k=kk)]
            shapes.append(Shape('fill' if head == 'oval' else 'stroke', nodes, True, wmul, mono))
            continue
        nodes = [_parse_point(t, ns, k) for t in toks]
        shapes.append(Shape('fill' if fill else 'stroke', nodes, closed, wmul, mono))
    return shapes


def _isnum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# --------------------------------------------------------------------------
# pen
# --------------------------------------------------------------------------
@dataclass
class Pen:
    a: float            # half width of vertical strokes   (ellipse x radius before rotation)
    b: float            # half width of horizontal strokes (ellipse y radius before rotation)
    ang: float = 0.0    # rotation of the ellipse in degrees (broad-nib pens)

    def off(self, nx, ny, w=1.0):
        """support point of the (rotated) ellipse for outward normal (nx, ny)"""
        a, b = self.a, self.b
        if self.ang:
            c, s_ = math.cos(math.radians(self.ang)), math.sin(math.radians(self.ang))
            nx, ny = nx * c + ny * s_, -nx * s_ + ny * c
        den = math.hypot(a * nx, b * ny)
        if den < 1e-9:
            return (0.0, 0.0)
        px, py = w * a * a * nx / den, w * b * b * ny / den
        if self.ang:
            px, py = px * c - py * s_, px * s_ + py * c
        return (px, py)

    def extent(self):
        """half extents (x, y) of the pen: half thickness of vertical / horizontal strokes"""
        return self.off(1, 0)[0], self.off(0, 1)[1]


def _unit(dx, dy):
    L = math.hypot(dx, dy)
    return (dx / L, dy / L) if L > 1e-9 else None


def _isect(p, d, q, e):
    """intersection of p+t*d and q+s*e, or None"""
    cr = d[0] * e[1] - d[1] * e[0]
    if abs(cr) < 1e-9:
        return None
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / cr
    return (p[0] + t * d[0], p[1] + t * d[1])


def _expand(shape: Shape):
    """skeleton nodes -> control polygon [(x, y, on, w)], closed flag"""
    seq = list(shape.nodes)
    closed = shape.closed
    if closed:
        idx = next((i for i, n in enumerate(seq) if not n.cc), None)
        if idx is None:
            f, l = seq[0], seq[-1]
            seq = [Node((f.x + l.x) / 2, (f.y + l.y) / 2)] + seq
        else:
            seq = seq[idx:] + seq[:idx]
        seq = seq + [seq[0]]
    tmp = [seq[0]]
    for n in seq[1:]:
        if n.cc and tmp[-1].cc:
            p = tmp[-1]
            tmp.append(Node((p.x + n.x) / 2, (p.y + n.y) / 2))
        tmp.append(n)
    poly = [(tmp[0].x, tmp[0].y, True, tmp[0].w)]
    i = 1
    while i < len(tmp):
        n = tmp[i]
        if n.cc:
            A, B = tmp[i - 1], tmp[i + 1]
            kk = n.k
            poly.append((A.x + kk * (n.x - A.x), A.y + kk * (n.y - A.y), False, A.w + (B.w - A.w) / 3))
            poly.append((B.x + kk * (n.x - B.x), B.y + kk * (n.y - B.y), False, A.w + 2 * (B.w - A.w) / 3))
            poly.append((B.x, B.y, True, B.w))
            i += 2
        else:
            poly.append((n.x, n.y, True, n.w))
            i += 1
    return poly, closed, (tmp[0].cap, tmp[-1].cap)


def _offset(P, closed, pen: Pen, side: int, wmul: float, miter=2.4):
    """Tiller-Hanson style offset of a control polygon.  Returns list of (x, y)
    with exactly the same structure as P (so masters stay compatible)."""
    n = len(P)
    if closed:
        P = P[:-1]
        n -= 1
    nl = n if closed else n - 1
    dirs = []
    for i in range(nl):
        A = P[i]
        B = P[(i + 1) % n]
        dirs.append(_unit(B[0] - A[0], B[1] - A[1]))
    # fill degenerate legs from neighbours
    for i in range(nl):
        if dirs[i] is None:
            j = i
            while j < nl and dirs[j] is None:
                j += 1
            if j < nl:
                dirs[i] = dirs[j]
            else:
                j = i
                while j >= 0 and dirs[j] is None:
                    j -= 1
                dirs[i] = dirs[j] if j >= 0 else (1.0, 0.0)
    vs = [pen.off(-d[1] * side, d[0] * side) for d in dirs]
    out = []
    for j in range(n):
        x, y, on, w = P[j]
        w *= wmul
        pi = j - 1 if j > 0 else (nl - 1 if closed else None)
        ni = j if j < nl else (0 if closed else None)
        if pi is None:
            v = vs[ni]
            out.append((x + w * v[0], y + w * v[1]))
            continue
        if ni is None:
            v = vs[pi]
            out.append((x + w * v[0], y + w * v[1]))
            continue
        vp, vn = vs[pi], vs[ni]
        Pm = P[(j - 1) % n]
        Pn = P[(j + 1) % n]
        A1 = (Pm[0] + Pm[3] * wmul * vp[0], Pm[1] + Pm[3] * wmul * vp[1])
        A2 = (x + w * vp[0], y + w * vp[1])
        B1 = (x + w * vn[0], y + w * vn[1])
        B2 = (Pn[0] + Pn[3] * wmul * vn[0], Pn[1] + Pn[3] * wmul * vn[1])
        dA = _unit(A2[0] - A1[0], A2[1] - A1[1]) or dirs[pi]
        dB = _unit(B2[0] - B1[0], B2[1] - B1[1]) or dirs[ni]
        cr = dA[0] * dB[1] - dA[1] * dB[0]
        dot = dA[0] * dB[0] + dA[1] * dB[1]
        if abs(cr) < 0.06 and dot > 0:
            out.append(((A2[0] + B1[0]) / 2, (A2[1] + B1[1]) / 2))
            continue
        pt = _isect(A2, dA, B1, dB)
        if pt is None:
            pt = ((A2[0] + B1[0]) / 2, (A2[1] + B1[1]) / 2)
        lim = miter * w * max(pen.a, pen.b)
        dist = math.hypot(pt[0] - x, pt[1] - y)
        if dist > lim:
            s = lim / dist
            pt = (x + (pt[0] - x) * s, y + (pt[1] - y) * s)
        out.append(pt)
    # collapse legs that flipped direction (inner side of tight curves)
    for i in range(nl):
        j = (i + 1) % n
        d = dirs[i]
        ex, ey = out[j][0] - out[i][0], out[j][1] - out[i][1]
        if ex * d[0] + ey * d[1] < 0:
            mx, my = (out[i][0] + out[j][0]) / 2, (out[i][1] + out[j][1]) / 2
            # keep the two points a hair apart: identical points would change the segment count
            # of a contour in one master only
            out[i] = (mx - 0.03 * d[0], my - 0.03 * d[1])
            out[j] = (mx + 0.03 * d[0], my + 0.03 * d[1])
    return out, dirs


def _area(pts):
    s = 0.0
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i][0], pts[i][1]
        x1, y1 = pts[(i + 1) % n][0], pts[(i + 1) % n][1]
        s += x0 * y1 - x1 * y0
    return s / 2


def _cap_dir(cap, d):
    if cap in (None, 'b', 'r'):
        return None
    if cap == 'h':
        return (1.0, 0.0)
    if cap == 'v':
        return (0.0, 1.0)
    ang = math.radians(float(cap))
    return (math.cos(ang), math.sin(ang))


def stroke(shape: Shape, pen: Pen):
    """Expand one skeleton stroke to a list of contours [(x, y, on), ...].
    Outer contours are counter-clockwise (PostScript/UFO convention)."""
    P, closed, caps = _expand(shape)
    if shape.mono is not None:
        r = (pen.a + pen.b) / 2 * shape.mono
        pen = Pen(r, r) if not pen.ang else Pen(pen.a * shape.mono, pen.b * shape.mono, pen.ang)
    L, dirs = _offset(P, closed, pen, +1, shape.w)
    R, _ = _offset(P, closed, pen, -1, shape.w)
    flags = [p[2] for p in P]
    if closed:
        flags = flags[:-1]
        c1 = [(x, y, f) for (x, y), f in zip(L, flags)]
        c2 = [(x, y, f) for (x, y), f in zip(R, flags)]
        # A counter-clockwise skeleton has its left offset inside.  The choice is made from the
        # skeleton alone so that every master gets the same point order, even where a tight
        # inner offset collapses.
        if _area([(q[0], q[1]) for q in P[:-1]]) > 0:
            outer, inner = c2, _rev(c1)
        else:
            outer, inner = _rev(c1), c2
        return [outer, inner]
    n = len(P)
    # end caps
    def cut(side_pts, idx, nxt, q, cap, d):
        dc = _cap_dir(cap, d)
        if dc is None:
            return side_pts[idx]
        p = side_pts[idx]
        e = _unit(side_pts[nxt][0] - p[0], side_pts[nxt][1] - p[1]) or d
        if abs(e[0] * dc[1] - e[1] * dc[0]) < 0.12:
            return p
        r = _isect(p, e, q, dc)
        return r if r else p
    q0 = (P[0][0], P[0][1])
    qn = (P[-1][0], P[-1][1])
    L = list(L)
    R = list(R)
    L[0] = cut(L, 0, 1, q0, caps[0], dirs[0])
    R[0] = cut(R, 0, 1, q0, caps[0], dirs[0])
    L[-1] = cut(L, n - 1, n - 2, qn, caps[1], dirs[-1])
    R[-1] = cut(R, n - 1, n - 2, qn, caps[1], dirs[-1])
    pts = [(x, y, f) for (x, y), f in zip(L, flags)]
    if caps[1] == 'r':
        pts += _round_cap(qn, dirs[-1], pen, P[-1][3] * shape.w, +1)
    pts += [(x, y, f) for (x, y), f in zip(reversed(R), reversed(flags))]
    if caps[0] == 'r':
        d = dirs[0]
        pts += _round_cap(q0, (-d[0], -d[1]), pen, P[0][3] * shape.w, +1)
    pts = _rev(pts)      # left side forward + right side back is always clockwise
    return [pts]


def _round_cap(q, d, pen, w, side):
    """off/on points of a half-ellipse from the left offset point round the
    tip to the right offset point (exclusive of both ends)."""
    n = pen.off(-d[1], d[0], w)       # left normal offset
    u = pen.off(d[0], d[1], w)        # forward offset
    Lp = (q[0] + n[0], q[1] + n[1])
    T = (q[0] + u[0], q[1] + u[1])
    Rp = (q[0] - n[0], q[1] - n[1])
    k = KAPPA
    return [(Lp[0] + k * u[0], Lp[1] + k * u[1], False), (T[0] + k * n[0], T[1] + k * n[1], False),
            (T[0], T[1], True),
            (T[0] - k * n[0], T[1] - k * n[1], False), (Rp[0] + k * u[0], Rp[1] + k * u[1], False)]


def _rev(pts):
    return [pts[0]] + pts[:0:-1]


def fill(shape: Shape):
    P, closed, _ = _expand(shape)
    pts = [(p[0], p[1], p[2]) for p in P[:-1]]
    if _area(pts) < 0:
        pts = _rev(pts)
    return [pts]


def outline(shapes, pen: Pen):
    cs = []
    for s in shapes:
        if s.kind == 'fill':
            cs += fill(s)
        else:
            cs += stroke(s, pen)
    return cs


# --------------------------------------------------------------------------
# contour utilities
# --------------------------------------------------------------------------
def draw(contours, pen):
    """draw [(x, y, on)] contours to a fontTools segment pen (cubic)"""
    for c in contours:
        n = len(c)
        if n < 2:
            continue
        s = next((i for i, p in enumerate(c) if p[2]), 0)
        c = c[s:] + c[:s]
        # a contour that returns to its starting point: drop the repeat, so that every master of a variable font
        # has the same number of segments whether the two points are equal exactly or only nearly
        while len(c) > 2 and c[-1][2] and abs(c[-1][0] - c[0][0]) < 0.01 and abs(c[-1][1] - c[0][1]) < 0.01:
            c = c[:-1]
        pen.moveTo((c[0][0], c[0][1]))
        offs = []
        for p in c[1:] + [c[0]]:
            if p[2]:
                if not offs:
                    if p is c[0]:
                        break
                    pen.lineTo((p[0], p[1]))
                elif len(offs) == 2:
                    pen.curveTo(offs[0], offs[1], (p[0], p[1]))
                else:
                    pen.qCurveTo(*offs, (p[0], p[1]))
                offs = []
            else:
                offs.append((p[0], p[1]))
        pen.closePath()


def from_recording(value):
    """RecordingPen value -> contours [(x, y, on)] (cubic)"""
    out = []
    cur = None
    for op, args in value:
        if op == 'moveTo':
            cur = [(args[0][0], args[0][1], True)]
        elif op == 'lineTo':
            cur.append((args[0][0], args[0][1], True))
        elif op == 'curveTo':
            cur.append((args[0][0], args[0][1], False))
            cur.append((args[1][0], args[1][1], False))
            cur.append((args[2][0], args[2][1], True))
        elif op == 'qCurveTo':
            p0 = cur[-1]
            q = args[0]
            e = args[-1]
            if len(args) != 2:
                raise ValueError('unexpected multi-off quadratic')
            cur.append((p0[0] + 2 / 3 * (q[0] - p0[0]), p0[1] + 2 / 3 * (q[1] - p0[1]), False))
            cur.append((e[0] + 2 / 3 * (q[0] - e[0]), e[1] + 2 / 3 * (q[1] - e[1]), False))
            cur.append((e[0], e[1], True))
        elif op in ('closePath', 'endPath'):
            if cur:
                if len(cur) > 1 and cur[-1][2] and abs(cur[-1][0] - cur[0][0]) < 1e-6 and abs(cur[-1][1] - cur[0][1]) < 1e-6:
                    cur.pop()
                if len(cur) >= 3:
                    out.append(cur)
            cur = None
    return out


def union(contours):
    """remove overlaps (non-zero winding) with skia-pathops"""
    path = pathops.Path()
    draw(contours, path.getPen())
    path.simplify(fix_winding=True, keep_starting_points=False)
    rec = RecordingPen()
    path.draw(rec)
    return from_recording(rec.value)


def difference(a, b):
    pa, pb = pathops.Path(), pathops.Path()
    draw(a, pa.getPen())
    draw(b, pb.getPen())
    res = pathops.op(pa, pb, pathops.PathOp.DIFFERENCE, fix_winding=True)
    rec = RecordingPen()
    res.draw(rec)
    return from_recording(rec.value)


def intersection(a, b):
    pa, pb = pathops.Path(), pathops.Path()
    draw(a, pa.getPen())
    draw(b, pb.getPen())
    res = pathops.op(pa, pb, pathops.PathOp.INTERSECTION, fix_winding=True)
    rec = RecordingPen()
    res.draw(rec)
    return from_recording(rec.value)


def bounds(contours):
    if not contours:
        return None
    bp = BoundsPen(None)
    draw(contours, bp)
    return bp.bounds


def xform(contours, fn):
    return [[(*fn(p[0], p[1]), p[2]) for p in c] for c in contours]


def shift(contours, dx, dy=0.0):
    return [[(p[0] + dx, p[1] + dy, p[2]) for p in c] for c in contours]


def ink_traps(contours, depth, mouth, ylo, yhi, min_turn=55.0, max_turn=150.0, fillet=False):
    """Cut a small notch into every sharp inner corner of the ink (a crotch between two strokes) whose y lies between
    ylo and yhi.  On absorbent paper ink fills such corners; the notch leaves room for it.  Contours must be free of
    overlaps.  Returns new contours."""
    if not contours:
        return contours
    big = max(contours, key=lambda c: abs(_area([(p[0], p[1]) for p in c])))
    sgn = 1.0 if _area([(p[0], p[1]) for p in big]) > 0 else -1.0
    cuts = []
    lo, hi = math.radians(min_turn), math.radians(max_turn)
    for c in contours:
        n = len(c)
        for i, p in enumerate(c):
            if not p[2] or not (ylo <= p[1] <= yhi):
                continue
            a, b = c[i - 1], c[(i + 1) % n]
            d1, d2 = _unit(p[0] - a[0], p[1] - a[1]), _unit(b[0] - p[0], b[1] - p[1])
            if d1 is None or d2 is None:
                continue
            cr = (d1[0] * d2[1] - d1[1] * d2[0]) * sgn
            if cr >= 0:
                continue
            th = math.atan2(-cr, d1[0] * d2[0] + d1[1] * d2[1])
            if not (lo <= th <= hi):
                continue
            e = _unit(d2[0] - d1[0], d2[1] - d1[1])
            if e is None:
                continue
            A = (p[0] - d1[0] * mouth, p[1] - d1[1] * mouth)
            B = (p[0] + d2[0] * mouth, p[1] + d2[1] * mouth)
            C = (p[0] - e[0] * depth, p[1] - e[1] * depth)
            if fillet:                 # the opposite of a trap: the corner is filled, as ink does on a typewriter ribbon
                cuts.append([(A[0], A[1], True), (p[0] - e[0] * 2, p[1] - e[1] * 2, True), (B[0], B[1], True)])
            else:
                cuts.append([(A[0], A[1], True), (C[0], C[1], True), (B[0], B[1], True)])
    if not cuts:
        return contours
    return union(contours + cuts) if fillet else difference(contours, cuts)
