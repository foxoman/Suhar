"""Hand-drawn Arabic bitmaps for the 8 and 9 px pixel fonts.

One-pixel strokes; the join line is the Latin baseline row.  Each letter body (rasm) is drawn once per form;
dots and hamza are added by rule from the same letter table the outline fonts use (arabic.LETTERS).
Rows are listed top to bottom, '#' = ink.  `below` = number of rows under the join row.
Optional: da / db = column the dots above / below are centred on; din = (column, row) of a dot inside the bowl."""
from . import arabic as A

B = {
    'alef.isol': (["#"] * 7, 0), 'alef.fina': (["#."] * 6 + ["##"], 0),
    'alefshort.isol': (["#"] * 5, 0, dict(da=0)), 'alefshort.fina': (["#."] * 4 + ["##"], 0, dict(da=0)),
    'beh.isol': (["#.....#", "#######"], 0), 'beh.fina': (["#.......", "########"], 0),
    'beh.init': ([".#", ".#", "##"], 0, dict(da=1, db=1)), 'beh.medi': ([".#.", ".#.", "###"], 0),
    'noon.isol': (["....#", "#...#", "#...#", ".###."], 2), 'noon.fina': (["#...##", "#...#.", ".###.."], 2, dict(da=2)),
    'yeh.isol': ([".....##", "#...#..", ".###..."], 1, dict(db=2)), 'yeh.fina': (["#...###", ".###..."], 1, dict(db=2)),
    'jeem.isol': (["#####.", "..#...", ".#....", "#.....", ".#####"], 3, dict(da=2, din=(4, -1))),
    'jeem.fina': (["######", ".#....", "#.....", ".###.."], 3, dict(da=2, din=(4, -2))),
    'jeem.init': (["####", "...#", "####"], 0, dict(da=1, db=2)), 'jeem.medi': (["####.", "...#.", "#####"], 0, dict(da=1, db=2)),
    'dal.isol': ([".#.", "..#", "###"], 0), 'dal.fina': ([".#..", "..#.", "####"], 0, dict(da=1)),
    'reh.isol': (["..#", "..#", ".#.", "#.."], 2, dict(da=2)), 'reh.fina': (["..##", ".#..", "#..."], 2, dict(da=2)),
    'waw.isol': ([".##", "#.#", ".##", "..#", "##."], 2), 'waw.fina': ([".##.", "#.#.", ".###", "..#.", "##.."], 2, dict(da=1)),
    'seen.isol': (["....#.#.#", "#...#####", "#...#....", ".###....."], 2, dict(da=6)),
    'seen.fina': (["....#.#.#.", "#...######", "#...#.....", ".###......"], 2, dict(da=6)),
    'seen.init': ([".#.#.#", "######"], 0, dict(da=3)), 'seen.medi': ([".#.#.#.", "#######"], 0, dict(da=3)),
    'sad.isol': (["......###.", ".....#...#", "#...######", "#...#.....", ".###......"], 2, dict(da=7)),
    'sad.fina': (["......###..", ".....#...#.", "#...#######", "#...#......", ".###......."], 2, dict(da=7)),
    'sad.init': (["...###.", ".##...#", "#######"], 0, dict(da=4)), 'sad.medi': (["...###..", ".##...#.", "########"], 0, dict(da=4)),
    'tah.isol': ([".#...."] * 4 + [".####.", ".#...#", ".#####"], 0, dict(da=4)),
    'tah.fina': ([".#....."] * 4 + [".####..", ".#...#.", ".######"], 0, dict(da=4)),
    'tah.init': ([".#...."] * 4 + [".####.", ".#...#", "######"], 0, dict(da=4)),
    'tah.medi': ([".#....."] * 4 + [".####..", ".#...#.", "#######"], 0, dict(da=4)),
    'ain.isol': ([".##.", "#...", ".###", ".#..", "#...", ".###"], 3, dict(da=1)), 'ain.init': ([".###", "#...", "####"], 0, dict(da=2)),
    'ain.medi': (["###", ".#.", "###"], 0), 'ain.fina': (["..###.", "...#..", "..####", ".#....", "#.....", ".####."], 3, dict(da=3)),
    'feh.isol': (["......##.", "#....#..#", "#########"], 0, dict(da=7)), 'feh.fina': (["......##..", "#....#..#.", "##########"], 0, dict(da=7)),
    'feh.init': ([".##.", "#..#", "####"], 0, dict(da=2)), 'feh.medi': ([".##..", "#..#.", "#####"], 0, dict(da=2)),
    'qaf.isol': (["...##", "..#.#", "#..##", "#...#", ".###."], 2, dict(da=4)),
    'qaf.fina': (["...##.", "..#.#.", "#..###", "#...#.", ".###.."], 2, dict(da=4)),
    'kaf.isol': (["....#"] * 3 + ["..#.#", ".#..#", "#...#", "#####"], 0),
    'kaf.fina': (["....#."] * 3 + ["..#.#.", ".#..#.", "#...#.", "######"], 0),
    'kaf.init': (["...#", "..#.", ".#..", "..#.", "...#", "...#", "####"], 0),
    'kaf.medi': (["...#.", "..#..", ".#...", "..#..", "...#.", "...#.", "#####"], 0),
    'lam.isol': (["...#"] * 7 + ["#..#", ".##."], 2), 'lam.fina': (["...#."] * 6 + ["...##", "#..#.", ".##.."], 2),
    'lam.init': ([".#"] * 6 + ["##"], 0), 'lam.medi': ([".#."] * 6 + ["###"], 0),
    'meem.isol': ([".##", "#.#", "###", "#..", "#.."], 3), 'meem.fina': ([".##.", "#.##", "###.", "#...", "#..."], 3),
    'meem.init': (["..##", "##.#", "..##"], 1), 'meem.medi': (["..##.", "##.##", "..##."], 1),
    'heh.isol': ([".##.", "#..#", ".##."], 0, dict(da=2)), 'heh.fina': ([".#..", "#.#.", ".###"], 0, dict(da=1)),
    'heh.init': ([".###", "#..#", "#.##", "####"], 0), 'heh.medi': ([".#.", "#.#", "###", "#.#", ".#."], 2),
    'hamza.isol': ([".##", "#..", ".##", "##."], 0),
    'lamalef.isol': (["#..#", "#..#", "#..#", ".#.#", ".#.#", "..##", "..#."], 0),
    'lamalef.fina': (["#..#.", "#..#.", "#..#.", ".#.#.", ".#.#.", "..##.", "..###"], 0),
    'tatweel.medi': (["###"], 0),
    # Persian and Urdu
    'keheh.isol': (["...#", "..#.", ".#..", "..#.", "...#", "#..#", "####"], 0),
    'keheh.fina': (["...#.", "..#..", ".#...", "..#..", "...#.", "#..#.", "#####"], 0),
    'barree.isol': ([".##.....", "#.......", ".#######"], 1), 'barree.fina': (["...####", "..#....", ".######"], 2),
}
B['gaf.isol'] = B['keheh.isol']; B['gaf.fina'] = B['keheh.fina']; B['gaf.init'] = B['kaf.init']; B['gaf.medi'] = B['kaf.medi']
for _k, _v in B.items():
    assert len({len(r) for r in _v[0]}) == 1, _k


class Bmp:
    """sparse bitmap: set of (col, row); row 0 = join row, positive = up"""
    def __init__(self, key):
        rows, below = B[key][0], B[key][1]
        self.opt = B[key][2] if len(B[key]) > 2 else {}
        self.w = len(rows[0])
        self.px = set()
        top = len(rows) - 1 - below
        for i, r in enumerate(rows):
            for c, ch in enumerate(r):
                if ch == '#':
                    self.px.add((c, top - i))
        self.x0 = 0

    def col_ext(self, c, hi):
        ys = [y for (x, y) in self.px if abs(x - c) <= 1]
        return (max(ys) if hi else min(ys)) if ys else 0

    def add(self, pts):
        self.px.update(pts)


def _dots(n, c, y, up):
    s = 1 if up else -1
    if n == 1:
        return [(c, y)]
    if n == 2:
        return [(c - 1, y), (c + 1, y)]
    return [(c - 1, y), (c + 1, y), (c, y + s)]


def compose(cp, form):
    """bitmap of one letter form, or None when its body or its marks are not in the hand-drawn set"""
    isolfina, initmedi, code = A.LETTERS[cp]
    rasm = isolfina if form in ('isol', 'fina') else initmedi
    key = f"{rasm}.{form}"
    if key not in B:
        return None
    if code == 'fy':
        code = None if form in ('isol', 'fina') else '2b'
    if code == 'ng':
        code = None
    b = Bmp(key)
    if rasm == 'gaf':                         # the second stroke of gaf: a short dash above the top stroke
        b.add([(2, 7), (1, 6)])
    if code == '3i':                          # cheh: three dots, under the letter when it joins forward
        if form in ('init', 'medi'):
            code = '3b'
        else:
            b.add([(3, -1), (5, -1), (4, -2)] if form == 'isol' else [(3, -2), (5, -2), (4, -1)])
            code = None
    jl, jr = form in ('init', 'medi'), form in ('medi', 'fina')
    if code is None:
        pass
    elif code in ('1a', '2a', '3a', '1b', '2b', '3b', '1i'):
        n, where = int(code[0]), code[1]
        if where == 'i':
            if 'din' in b.opt:
                b.add([b.opt['din']])
                where = None
            else:
                where = 'b'
        if where:
            up = where == 'a'
            c = b.opt.get('da' if up else 'db', b.w // 2)
            if n >= 2 and rasm == 'beh' and form == 'medi' and b.w < 4:      # one more join pixel so neighbouring dots do not merge
                b.px.add((b.w, 0))
                b.w += 1
            y = b.col_ext(c, up) + (2 if up else -2)
            if not up and y - (1 if n == 3 else 0) < -3:
                return None
            b.add(_dots(n, c, y, up))
    elif code == 'ha':
        c = b.opt.get('da', b.w // 2)
        y = b.col_ext(c, True) + 2
        if y + 1 > 7:
            y = 6
        b.add([(c, y), (c, y + 1), (c + 1, y + 1)])
    elif code == 'hb':
        b.add([(0, -2), (1, -2), (0, -3)])
    elif code == 'ma':
        b.add([(-1, 6), (0, 6), (1, 6)])
    elif code == 'wa':
        b.add([(0, 6), (1, 6)])
    else:
        return None
    xs = [x for x, _ in b.px]
    lo = min(min(xs), 0)
    hi = max(max(xs), b.w - 1)
    if lo < 0 and jl or hi > b.w - 1 and jr:
        return None
    b.px = {(x - lo, y) for x, y in b.px}
    b.w = hi - lo + 1
    if max(y for _, y in b.px) > 7 or min(y for _, y in b.px) < -3:
        return None
    b.jl, b.jr = jl, jr
    return b


def table(bold=False):
    """glyph name -> Bmp for every glyph the set covers; bold doubles every pixel to the right"""
    out = {}
    for cp, forms in A.FORMS.items():
        for form, name in forms.items():
            b = compose(cp, form)
            if b is not None:
                out[name] = b
    for (alef, form), name in A.LIGA.items():
        b = Bmp('lamalef.' + form)
        if alef == 0x622:
            b.add([(-1, 7), (0, 7), (1, 7)])
        elif alef == 0x623:
            b.add([(0, 7), (-1, 7)])
        elif alef == 0x625:
            b.add([(1, -2), (2, -2), (1, -3)])
        lo = min(x for x, _ in b.px)
        b.px = {(x - lo, y) for x, y in b.px}
        b.w = max(x for x, _ in b.px) + 1
        b.jl, b.jr = False, form == 'fina'
        out[name] = b
    if 'uni0640' in A.INFO:
        b = Bmp('tatweel.medi'); b.jl = b.jr = True
        out['uni0640'] = b
    if bold:
        for b in out.values():
            b.px = b.px | {(x + 1, y) for x, y in b.px}
            b.w += 1
    return out
