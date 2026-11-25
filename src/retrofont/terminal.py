"""Terminal glyphs drawn on the exact character cell: box drawing (complete
U+2500..257F), block elements (U+2580..259F), Braille (U+2800..28FF),
Powerline (U+E0A0..E0A3, E0B0..E0BF) and sextants / eighth blocks from
Symbols for Legacy Computing.  All of them have the Mono advance (600) in every
family and span exactly descender..ascender so they tile without gaps."""
import unicodedata as ud
from . import engine as E
from .model import G, GlyphOut, MONO_W, ASCENT, DESCENT, lerp

W = MONO_W
B, T = DESCENT, ASCENT
CX, CY = W / 2, (ASCENT + DESCENT) / 2
H = T - B


def rect(x0, y0, x1, y1):
    return [(x0, y0, True), (x1, y0, True), (x1, y1, True), (x0, y1, True)]


def poly(pts):
    c = [(x, y, True) for x, y in pts]
    return c if E._area(c) > 0 else E._rev(c)


def thick(st):
    """light and heavy line thickness (even numbers, weight aware)"""
    t = 0.0 if st.compat else st.t
    l = 2 * round(lerp(34, 50, t))
    return l, 2 * l


def out(st, d, cs, do_union=True):
    g = GlyphOut(d.name, d.uni, cs, W)
    g.needs_union = False
    if do_union and len(cs) > 1:
        g.contours = E.union(cs)
    return g


def T_(fn):
    def wrap(st, d):
        r = fn(st)
        if isinstance(r, tuple):
            return out(st, d, r[0], r[1])
        return out(st, d, r)
    return wrap


def reg(cp, fn):
    G(cp, None, fn=T_(fn), slant=False, script='sym')


# ---- box drawing ----------------------------------------------------------
DIRS = ('UP', 'RIGHT', 'DOWN', 'LEFT')


def parse_box(name):
    """-> dict dir -> 'L' | 'H' | 'D' from the Unicode character name"""
    n = name.replace('BOX DRAWINGS ', '')
    arms = {}
    carry = None
    for ci, clause in enumerate(n.split(' AND ')):
        words = clause.split()
        wt = None
        for w in words:
            if w in ('LIGHT', 'SINGLE'):
                wt = 'L'
            elif w == 'HEAVY':
                wt = 'H'
            elif w == 'DOUBLE':
                wt = 'D'
        if wt is None:
            wt = carry
        elif ci == 0 and words[0] in ('LIGHT', 'HEAVY', 'DOUBLE'):
            carry = wt
        for w in words:
            if w == 'HORIZONTAL':
                arms['LEFT'] = arms['RIGHT'] = wt
            elif w == 'VERTICAL':
                arms['UP'] = arms['DOWN'] = wt
            elif w in DIRS:
                arms[w] = wt
    return arms


def box(arms):
    def fn(st):
        tl, th = thick(st)
        t = tl
        wd = {'L': tl, 'H': th, 'D': 3 * tl}

        def arm_rect(d, half, e):
            # rectangle of an arm: from the cell edge to centre + e (e>0 passes the centre)
            if d == 'RIGHT':
                return rect(CX - e, CY - half, W, CY + half)
            if d == 'LEFT':
                return rect(0, CY - half, CX + e, CY + half)
            if d == 'UP':
                return rect(CX - half, CY - e, CX + half, T)
            return rect(CX - half, B, CX + half, CY + e)

        opp = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
        perp = {'UP': ('LEFT', 'RIGHT'), 'DOWN': ('LEFT', 'RIGHT'), 'LEFT': ('UP', 'DOWN'), 'RIGHT': ('UP', 'DOWN')}
        fats, cores, singles = [], [], []
        for d, w in arms.items():
            ps = [arms.get(p) for p in perp[d]]
            has_opp = opp[d] in arms
            if w == 'D':
                if 'D' in ps:
                    ef, ec = 1.5 * t, 0.5 * t
                    if not has_opp and ps.count('D') == 1 and None in ps:
                        ec = -0.5 * t if False else 0.5 * t
                    if has_opp is False and ps.count('D') == 2:
                        ec = 0.5 * t
                elif any(ps):
                    ef, ec = 0.5 * max(wd[p] for p in ps if p), -0.5 * max(wd[p] for p in ps if p)
                else:
                    ef, ec = 0, 0
                if 'D' in ps and not has_opp:
                    # corner or tee: core must not cut the far outer line of the perpendicular double
                    ec = 0.5 * t
                    if ps.count('D') == 1:
                        # corner: reaches into the perpendicular core only on its own side
                        ec = 0.5 * t
                if 'D' in ps and has_opp and ps.count('D') == 1:
                    ec = 0.5 * t
                fats.append(arm_rect(d, 1.5 * t, ef))
                cores.append(arm_rect(d, 0.5 * t, ec))
            else:
                half = wd[w] / 2
                nd = ps.count('D')
                if nd == 2 and not has_opp:
                    e = -0.5 * t
                elif nd == 1 and not has_opp:
                    e = 1.5 * t
                elif nd == 1 and has_opp and None in ps:
                    e = 1.5 * t
                elif nd:
                    e = 0
                else:
                    pw = [wd[p] for p in ps if p]
                    e = max(pw) / 2 if pw else 0
                    if not pw and not has_opp:
                        e = 0
                singles.append(arm_rect(d, half, e))
        cs = []
        if fats:
            f = E.union(fats)
            # a core must stop where a perpendicular double has an unbroken outer line
            c = E.union(cores)
            cs = E.difference(f, c)
        if singles:
            cs = E.union(cs + singles)
        return cs, False
    return fn


def dashed(n, heavy, vertical):
    def fn(st):
        tl, th = thick(st)
        t = th if heavy else tl
        cs = []
        L = H if vertical else W
        seg = L / n
        for i in range(n):
            a = i * seg + seg * 0.18
            b = (i + 1) * seg - seg * 0.18
            if vertical:
                cs.append(rect(CX - t / 2, B + a, CX + t / 2, B + b))
            else:
                cs.append(rect(a, CY - t / 2, b, CY + t / 2))
        return cs, False
    return fn


def arc(which):
    def fn(st):
        tl, _ = thick(st)
        r = 240
        sx = 1 if 'RIGHT' in which else -1
        sy = 1 if 'UP' in which else -1
        ex = W if sx > 0 else 0
        ey = T if sy > 0 else B
        nodes = [E.Node(CX, ey), E.Node(CX, CY + sy * r), E.Node(CX, CY, True, k=E.KAPPA),
                 E.Node(CX + sx * r, CY), E.Node(ex, CY)]
        return E.stroke(E.Shape('stroke', nodes), E.Pen(tl / 2, tl / 2)), False
    return fn


def diag(kind):
    def fn(st):
        tl, _ = thick(st)
        cs = []
        cell = [rect(0, B, W, T)]
        ext = 0.2
        for k in kind:
            if k == '/':
                p, q = (0 - W * ext, B - H * ext), (W + W * ext, T + H * ext)
            else:
                p, q = (0 - W * ext, T + H * ext), (W + W * ext, B - H * ext)
            cs += E.stroke(E.Shape('stroke', [E.Node(*p), E.Node(*q)]), E.Pen(tl / 2, tl / 2))
        return E.intersection(E.union(cs), cell), False
    return fn


_DASH = {0x2504: (3, 0, 0), 0x2505: (3, 1, 0), 0x2506: (3, 0, 1), 0x2507: (3, 1, 1), 0x2508: (4, 0, 0),
         0x2509: (4, 1, 0), 0x250A: (4, 0, 1), 0x250B: (4, 1, 1), 0x254C: (2, 0, 0), 0x254D: (2, 1, 0),
         0x254E: (2, 0, 1), 0x254F: (2, 1, 1)}
_ARC = {0x256D: ('DOWN', 'RIGHT'), 0x256E: ('DOWN', 'LEFT'), 0x256F: ('UP', 'LEFT'), 0x2570: ('UP', 'RIGHT')}
for cp in range(0x2500, 0x2580):
    if cp in _DASH:
        reg(cp, dashed(*_DASH[cp]))
    elif cp in _ARC:
        reg(cp, arc(_ARC[cp]))
    elif cp in (0x2571, 0x2572, 0x2573):
        reg(cp, diag({0x2571: '/', 0x2572: '\\', 0x2573: '/\\'}[cp]))
    else:
        reg(cp, box(parse_box(ud.name(chr(cp)))))


# ---- block elements -------------------------------------------------------
def shade(level):
    def fn(st):
        nx, ny = 6, 13
        dx, dy = W / nx, H / ny
        cs = []
        for j in range(ny):
            for i in range(nx):
                if level == 1:
                    on = (i % 2 == 0 and j % 2 == 0) if (j // 2) % 2 == 0 else (i % 2 == 1 and j % 2 == 0)
                    on = (i + 2 * (j % 4 // 2)) % 4 == 0 and j % 2 == 0 or (i + 2) % 4 == 0 and j % 4 == 2 and False
                    on = (j % 2 == 0) and ((i + (j // 2) * 2) % 4 == 0 or (i + (j // 2) * 2) % 4 == 2) and (i + j // 2) % 2 == 0
                elif level == 2:
                    on = (i + j) % 2 == 0
                else:
                    on = not ((j % 2 == 0) and (i + j // 2) % 2 == 0)
                if on:
                    cs.append(rect(i * dx, B + j * dy, (i + 1) * dx, B + (j + 1) * dy))
        return E.union(cs), False
    return fn


def frac_rect(x0, y0, x1, y1):
    return lambda st: ([rect(x0 * W, B + y0 * H, x1 * W, B + y1 * H)], False)


def quads(mask):   # bit0 upper-left, 1 upper-right, 2 lower-left, 3 lower-right
    def fn(st):
        cs = []
        for i, (x, y) in enumerate([(0, CY), (CX, CY), (0, B), (CX, B)]):
            if mask & (1 << i):
                cs.append(rect(x, y, x + W / 2, y + H / 2))
        return (E.union(cs) if len(cs) > 1 else cs), False
    return fn


reg(0x2580, frac_rect(0, .5, 1, 1))
for i in range(1, 9):
    reg(0x2580 + i, frac_rect(0, 0, 1, i / 8))
for i in range(1, 8):
    reg(0x2588 + i, frac_rect(0, 0, (8 - i) / 8, 1))
reg(0x2590, frac_rect(.5, 0, 1, 1))
reg(0x2591, shade(1)); reg(0x2592, shade(2)); reg(0x2593, shade(3))
reg(0x2594, frac_rect(0, 7 / 8, 1, 1))
reg(0x2595, frac_rect(7 / 8, 0, 1, 1))
for cp, m in zip(range(0x2596, 0x25A0), [4, 8, 1, 13, 9, 7, 11, 2, 6, 14]):
    reg(cp, quads(m))
# legacy computing: sextants, eighth blocks
_idx = 0
for m in range(1, 63):
    if m in (21, 42):
        continue

    def sext(st, m=m):
        cs = []
        for bit in range(6):
            if m & (1 << bit):
                col, row = bit % 2, bit // 2
                cs.append(rect(col * W / 2, T - (row + 1) * H / 3, (col + 1) * W / 2, T - row * H / 3))
        return (E.union(cs) if len(cs) > 1 else cs), False
    reg(0x1FB00 + _idx, sext)
    _idx += 1
for i in range(6):
    reg(0x1FB70 + i, frac_rect((i + 1) / 8, 0, (i + 2) / 8, 1))
    reg(0x1FB76 + i, frac_rect(0, 1 - (i + 2) / 8, 1, 1 - (i + 1) / 8))
reg(0x1FB82, frac_rect(0, 6 / 8, 1, 1)); reg(0x1FB83, frac_rect(0, 5 / 8, 1, 1)); reg(0x1FB84, frac_rect(0, 3 / 8, 1, 1))
reg(0x1FB85, frac_rect(0, 2 / 8, 1, 1)); reg(0x1FB86, frac_rect(0, 1 / 8, 1, 1))
reg(0x1FB87, frac_rect(6 / 8, 0, 1, 1)); reg(0x1FB88, frac_rect(5 / 8, 0, 1, 1)); reg(0x1FB89, frac_rect(3 / 8, 0, 1, 1))
reg(0x1FB8A, frac_rect(2 / 8, 0, 1, 1)); reg(0x1FB8B, frac_rect(1 / 8, 0, 1, 1))


# ---- Braille --------------------------------------------------------------
def braille(cp):
    def fn(st):
        r = 52 if st.compat else lerp(48, 62, st.t)
        xs = (CX - 120, CX + 120)
        ys = [CY + 1.5 * 250, CY + 0.5 * 250, CY - 0.5 * 250, CY - 1.5 * 250]
        order = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (0, 3), (1, 3)]
        cs = []
        k = E.KAPPA * r
        for bit, (c, rw) in enumerate(order):
            if (cp - 0x2800) & (1 << bit):
                x, y = xs[c], ys[rw]
                cs.append([(x + r, y, True), (x + r, y + k, False), (x + k, y + r, False), (x, y + r, True),
                           (x - k, y + r, False), (x - r, y + k, False), (x - r, y, True),
                           (x - r, y - k, False), (x - k, y - r, False), (x, y - r, True),
                           (x + k, y - r, False), (x + r, y - k, False)])
        return cs, False
    return fn


for cp in range(0x2800, 0x2900):
    reg(cp, braille(cp))


# ---- Powerline ------------------------------------------------------------
def chevron(right):
    def fn(st):
        tl, _ = thick(st)
        x0, x1 = (0, W) if right else (W, 0)
        ext = 0.3
        p = (x0 - (x1 - x0) * ext, T + (T - CY) * ext)
        q = (x0 - (x1 - x0) * ext, B - (CY - B) * ext)
        s = E.Shape('stroke', [E.Node(*p), E.Node(x1, CY), E.Node(*q)])
        cs = E.stroke(s, E.Pen(tl / 2, tl / 2))
        return E.intersection(cs, [rect(0, B, W, T)]), False
    return fn


def halfround(right, filled):
    def fn(st):
        tl, _ = thick(st)
        x0, x1 = (0, W) if right else (W, 0)
        k = E.KAPPA
        ry = H / 2
        rx = x1 - x0
        c = [(x0, T, True), (x0 + rx * k, T, False), (x1, CY + ry * k, False), (x1, CY, True),
             (x1, CY - ry * k, False), (x0 + rx * k, B, False), (x0, B, True)]
        if E._area(c) < 0:
            c = E._rev(c)
        if filled:
            return [c], False
        s = (rx - (tl if right else -tl)) / rx
        inner = [(x0, CY + (y - CY) * (H - 2 * tl) / H if False else CY + (y - CY) * (1 - 2 * tl / H), o) if x == x0
                 else (x0 + (x - x0) * s, CY + (y - CY) * (1 - 2 * tl / H), o) for x, y, o in c]
        return E.difference([c], [inner]), False
    return fn


def slant(corner, filled):
    def fn(st):
        tl, _ = thick(st)
        pts = {'ll': [(0, B), (W, B), (0, T)], 'lr': [(0, B), (W, B), (W, T)],
               'ul': [(0, T), (W, T), (0, B)], 'ur': [(0, T), (W, T), (W, B)]}[corner]
        if filled:
            return [poly(pts)], False
        a, b = (pts[1], pts[2])
        ext = 0.2
        p = (a[0] - (b[0] - a[0]) * ext, a[1] - (b[1] - a[1]) * ext)
        q = (b[0] + (b[0] - a[0]) * ext, b[1] + (b[1] - a[1]) * ext)
        cs = E.stroke(E.Shape('stroke', [E.Node(*p), E.Node(*q)]), E.Pen(tl / 2, tl / 2))
        return E.intersection(cs, [rect(0, B, W, T)]), False
    return fn


reg(0xE0B0, lambda st: ([poly([(0, B), (W, CY), (0, T)])], False))
reg(0xE0B2, lambda st: ([poly([(W, B), (W, T), (0, CY)])], False))
reg(0xE0B1, chevron(True))
reg(0xE0B3, chevron(False))
reg(0xE0B4, halfround(True, True)); reg(0xE0B5, halfround(True, False))
reg(0xE0B6, halfround(False, True)); reg(0xE0B7, halfround(False, False))
reg(0xE0B8, slant('ll', True)); reg(0xE0B9, slant('ll', False))
reg(0xE0BA, slant('lr', True)); reg(0xE0BB, slant('lr', False))
reg(0xE0BC, slant('ul', True)); reg(0xE0BD, slant('ul', False))
reg(0xE0BE, slant('ur', True)); reg(0xE0BF, slant('ur', False))
# branch, line number, lock, column number (original drawings)
_S = dict(slant=False, script='sym', adv=W, fit=True)
G(0xE0A0, "w.85 150,620 150,-60; w.85 ring 150,-110 55,55; w.85 ring 150,670 55,55; w.85 ring 450,470 55,55;"
          "w.85 450,415 ~450,200 150,200", 30, 30, **_S)
G(0xE0A1, "use:L|0.5,0.5,40,330; use:N|0.5,0.5,290,-30", 20, 20, **_S)
G(0xE0A2, "z 90,0+hb 510,0+hb 510,330 90,330; 170,330 170,470 ~170,620 300,620 ~430,620 430,470 430,330; dot 300,165 .9",
  30, 30, **_S)
G(0xE0A3, "use:C|0.5,0.5,20,330; use:N|0.5,0.5,290,-30", 20, 20, **_S)
