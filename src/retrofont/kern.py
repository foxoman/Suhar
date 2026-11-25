"""Automatic kerning from the compiled outlines.

For every pair the horizontal gap between the right profile of the first glyph
and the left profile of the second is measured in 20-unit bands.  The mean of
the (depth-clipped) gap is compared with the H-H gap and the difference is
kerned out, limited by the closest approach so shapes never touch."""
import numpy as np
from fontTools.pens.basePen import BasePen
from . import engine as E

Y0, Y1, STEP = -220, 760, 20
NB = (Y1 - Y0) // STEP
CLIP = 300.0
BIG = 1e6


class _Flat(BasePen):
    def __init__(self):
        super().__init__(None)
        self.pts = []
        self.cur = None

    def _moveTo(self, p):
        self.cur = p
        self.start = p

    def _lineTo(self, p):
        a = self.cur
        n = max(2, int(max(abs(p[0] - a[0]), abs(p[1] - a[1])) / 8))
        for i in range(n + 1):
            t = i / n
            self.pts.append((a[0] + (p[0] - a[0]) * t, a[1] + (p[1] - a[1]) * t))
        self.cur = p

    def _curveToOne(self, b, c, d):
        a = self.cur
        for i in range(17):
            t = i / 16
            mt = 1 - t
            self.pts.append((mt ** 3 * a[0] + 3 * mt * mt * t * b[0] + 3 * mt * t * t * c[0] + t ** 3 * d[0],
                             mt ** 3 * a[1] + 3 * mt * mt * t * b[1] + 3 * mt * t * t * c[1] + t ** 3 * d[1]))
        self.cur = d

    def _closePath(self):
        if self.cur != self.start:
            self._lineTo(self.start)


def profile(g):
    """(left, right) arrays per band; BIG where there is no ink"""
    fp = _Flat()
    E.draw(g.contours, fp)
    left = np.full(NB, BIG)
    right = np.full(NB, BIG)
    if not fp.pts:
        return left, right
    arr = np.array(fp.pts)
    idx = np.floor((arr[:, 1] - Y0) / STEP).astype(int)
    ok = (idx >= 0) & (idx < NB)
    for i, x in zip(idx[ok], arr[ok, 0]):
        if x < left[i]:
            left[i] = x
        if g.advance - x < right[i]:
            right[i] = g.advance - x
    # fill interior bands (a band between inked bands is inked too)
    for a in (left, right):
        inked = np.where(a < BIG)[0]
        if len(inked) > 1:
            for i in range(inked[0], inked[-1]):
                if a[i] >= BIG:
                    a[i] = max(a[i - 1], 0)
    return left, right


def dilate(a, n=2):
    out = a.copy()
    for s in range(1, n + 1):
        out[s:] = np.minimum(out[s:], a[:-s])
        out[:-s] = np.minimum(out[:-s], a[s:])
    return out


LEFTS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz") + [
    'period', 'comma', 'hyphen', 'quoteright', 'quoteleft', 'quotedblleft', 'quotedblright', 'quotesingle',
    'quotedbl', 'parenleft', 'slash', 'endash', 'emdash', 'colon', 'semicolon', 'bracketleft', 'braceleft',
    'guillemotleft', 'guilsinglleft', 'guillemotright', 'guilsinglright', 'germandbls', 'AE', 'Oslash', 'oslash',
    'ae', 'oe', 'OE', 'Thorn', 'eth', 'thorn', 'dotlessi', 'question', 'exclam', 'ampersand', 'asterisk']
RIGHTS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz") + [
    'period', 'comma', 'hyphen', 'quoteright', 'quoteleft', 'quotedblleft', 'quotedblright', 'quotesingle',
    'quotedbl', 'parenright', 'slash', 'endash', 'emdash', 'colon', 'semicolon', 'bracketright', 'braceright',
    'guillemotleft', 'guilsinglleft', 'guillemotright', 'guilsinglright', 'question', 'exclam', 'AE', 'Oslash',
    'oslash', 'ae', 'oe', 'OE', 'eth', 'dotlessi', 'ampersand', 'asterisk', 'germandbls', 'thorn']


POS_LEFT = {'f', 'r', 'quotesingle', 'quotedbl', 'quoteright', 'quotedblright', 'asterisk'}
POS_RIGHT = {'quotesingle', 'quotedbl', 'quoteleft', 'quotedblleft', 'asterisk', 'parenright', 'bracketright', 'braceright', 'question'}


def _n(c):
    from .model import gname
    return gname(ord(c)) if len(c) == 1 else c


PUNCT_L = [n for n in LEFTS if len(n) > 1 and n not in ('germandbls', 'AE', 'Oslash', 'oslash', 'ae', 'oe', 'OE', 'Thorn', 'eth', 'thorn', 'dotlessi')]
PUNCT_R = [n for n in RIGHTS if len(n) > 1 and n not in ('germandbls', 'AE', 'Oslash', 'oslash', 'ae', 'oe', 'OE', 'eth', 'dotlessi', 'thorn')]
GREEK = ['uni%04X' % c for c in list(range(0x391, 0x3AA)) + list(range(0x3B1, 0x3CA)) if c != 0x3A2]
CYRIL = ['uni%04X' % c for c in list(range(0x410, 0x450)) + [0x404, 0x406, 0x454, 0x456, 0x490, 0x491, 0x402, 0x40B, 0x409, 0x40A,
                                                             0x40F, 0x452, 0x45B, 0x459, 0x45A, 0x45F, 0x4AF, 0x4B1, 0x49A, 0x49B]]


def compute(glyphs, comps):
    """-> (kerning dict, groups dict).  comps: {composite name: base name}.
    Pairs are measured within one script (plus punctuation); cross-script pairs are left alone."""
    sets = [([_n(c) for c in LEFTS], [_n(c) for c in RIGHTS]),
            (GREEK + PUNCT_L, GREEK + PUNCT_R), (CYRIL + PUNCT_L, CYRIL + PUNCT_R)]
    allnames = set()
    for l, r in sets:
        allnames.update(l)
        allnames.update(r)
    allnames = [n for n in allnames if n in glyphs and glyphs[n].contours]
    prof = {n: profile(glyphs[n]) for n in allnames}
    RP = {n: (prof[n][1], dilate(prof[n][1])) for n in allnames}
    LP = {n: (prof[n][0], dilate(prof[n][0])) for n in allnames}

    def measure(a, b):
        r, rd = RP[a]
        l, ld = LP[b]
        both = (r < BIG) & (l < BIG)
        if not both.any():
            return None
        gap = r[both] + l[both]
        m = float(np.minimum(gap, CLIP).mean())
        bd = (rd < BIG) & (ld < BIG)
        mn = float((rd[bd] + ld[bd]).min())
        cover = both.sum() * STEP
        return m, mn, cover

    T = measure('H', 'H')[0]
    safe = 0.42 * T
    kern = {}
    lefts, rights = [], []
    for si, (ls, rs) in enumerate(sets):
        ls = [n for n in ls if n in RP]
        rs = [n for n in rs if n in LP]
        lefts += ls
        rights += rs
        for a in ls:
            for b in rs:
                if si and a in PUNCT_L and b in PUNCT_R:
                    continue                      # punctuation pairs were done with Latin
                if (a, b) in kern:
                    continue
                ms = measure(a, b)
                if ms is None:
                    continue
                m, mn, cover = ms
                k = -(m - T) * 0.6
                if cover < 160:
                    k *= 0.6
                k = max(k, -(mn - safe), -120)
                k = min(k, 0)
                if mn < 30 and (a in POS_LEFT or b in POS_RIGHT):
                    k = 30 - mn
                k = round(k)
                if k <= -18 or k >= 10:
                    kern[(a, b)] = int(k)
    # groups: accented letters share their base letter's kerning
    g1, g2 = {}, {}
    for c, base in comps.items():
        if base in lefts:
            g1.setdefault(base, [base]).append(c)
        if base in rights:
            g2.setdefault(base, [base]).append(c)
    groups = {}
    out = {}
    tall_left = {'T', 'V', 'W', 'Y', 'F', 'P'}
    for (a, b), k in kern.items():
        ka = 'public.kern1.' + a if a in g1 else a
        kb = 'public.kern2.' + b if b in g2 else b
        if a in tall_left and b in g2 and b.islower() and k < -30:
            # accents above lower case would collide with the overhang: unaccented keeps full value
            out[(ka, kb)] = int(k * 0.45)
            out[(ka, b)] = k
        else:
            out[(ka, kb)] = k
    for base, members in g1.items():
        groups['public.kern1.' + base] = members
    for base, members in g2.items():
        groups['public.kern2.' + base] = members
    return out, groups


def arabic_tails(glyphs):
    """Kerning after letters that do not join forward and end in a tail under the baseline (reh, zain, waw ...).
    The next letter is drawn over the tail so the word does not fall apart.  Pairs are in logical order."""
    from . import arabic as A
    firsts, seconds = [], []
    for cp, forms in A.FORMS.items():
        if 'init' not in forms:
            for f in ('isol', 'fina'):
                n = forms.get(f)
                for m in (n, A.SS01.get(n)):
                    if m and m in glyphs and glyphs[m].contours:
                        firsts.append(m)
        for f in ('isol', 'init'):
            n = forms.get(f)
            if n and n in glyphs and glyphs[n].contours:
                seconds.append(n)
    seconds += [n for n in getattr(A, 'LIGA_NAMES', []) if n in glyphs]
    b0 = (0 - Y0) // STEP
    hi = slice(b0 + 1, b0 + 16)                     # 20..320 above the baseline
    ref = glyphs.get('uni0627')
    if ref is None:
        return {}
    la, ra = profile(ref)
    target_up = float(np.min(la[hi]) + np.min(ra[hi]))            # alef next to alef
    out = {}
    LP = {n: profile(glyphs[n])[0] for n in firsts}
    RP = {n: profile(glyphs[n])[1] for n in set(seconds)}
    for a in firsts:
        l = LP[a]
        low = l[:b0 - 2]
        if not (np.min(low) + 90 < np.min(l[hi])):                # no tail reaching left under the baseline
            continue
        for b in RP:
            g = l + RP[b]
            both = g < BIG / 2
            if not both.any():
                continue
            m_all = float(np.min(g[both]))
            up = g[hi][g[hi] < BIG / 2]
            m_up = float(np.min(up)) if len(up) else BIG
            k = -min(m_up - target_up, m_all - 55.0)
            k = max(k, -240.0)
            if k < -12:
                out[(a, b)] = int(round(k))
    return out


def arabic_word_space(glyphs):
    """Kerning between a word-final letter and the space.  A letter whose body sits to the right of a tail under the
    line (reh, zain, waw, final meem ...) would otherwise show a wider gap than the other letters."""
    from . import arabic as A
    names = set()
    for cp, forms in A.FORMS.items():
        for f in ('isol', 'fina'):
            n = forms.get(f)
            for m in (n, A.SS01.get(n), A.RET.get(n), A.STACK_JEEM.get(n)):
                if m:
                    names.add(m)
    names.update(n for n in A.LIGA.values())
    names.update(l for _, _, l in A.DLIG)
    b0 = (0 - Y0) // STEP
    out = {}
    for n in names:
        g = glyphs.get(n)
        if g is None or not g.contours:
            continue
        l = profile(g)[0]
        body = l[b0: b0 + 18]                 # baseline up to 360
        body = body[body < BIG / 2]
        allv = l[l < BIG / 2]
        if not len(body) or not len(allv):
            continue
        e = float(np.min(body) - np.min(allv))
        if e > 45:
            k = -int(round(min(0.6 * (e - 20), 110)))      # the tail may run under the space, but not across most of it
            for sp in ('space', 'uni00A0'):
                if sp in glyphs:
                    out[(n, sp)] = k
    return out


def hebrew(glyphs):
    """Kerning inside Hebrew.  Pairs are in logical order (the first letter stands on the right)."""
    names = [n for n in ('uni%04X' % c for c in range(0x5D0, 0x5EB)) if n in glyphs and glyphs[n].contours]
    if len(names) < 20:
        return {}
    b0 = (0 - Y0) // STEP
    body = slice(b0, b0 + 29)                 # baseline to the top of the letters
    P = {n: profile(glyphs[n]) for n in names}
    gap = {}
    for a in names:
        for b in names:
            g = P[a][0][body] + P[b][1][body]
            g = g[g < BIG / 2]
            if len(g):
                gap[(a, b)] = float(np.min(g))
    ref = float(np.median(list(gap.values())))
    out = {}
    for pr, m in gap.items():
        d = m - ref
        if d > 25:
            out[pr] = -int(round(min(0.7 * d, 90)))
        elif d < -25:
            out[pr] = int(round(min(-0.6 * d, 50)))
    return out
