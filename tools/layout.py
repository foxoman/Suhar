"""Tiny paragraph layout for proofs: script runs + a simplified bidi reorder
(enough for Arabic/Latin mixed lines; not a full UAX#9 implementation)."""
import unicodedata as ud
from PIL import Image


def _cls(ch):
    b = ud.bidirectional(ch)
    if b in ('R', 'AL'):
        return 'R'
    if b in ('L', 'EN', 'AN'):
        return 'L'
    if b == 'NSM':
        return 'M'
    return 'N'


def runs(text, rtl):
    cl = [_cls(c) for c in text]
    # marks take the previous class
    for i, c in enumerate(cl):
        if c == 'M':
            cl[i] = cl[i - 1] if i else ('R' if rtl else 'L')
    base = 'R' if rtl else 'L'
    # neutrals: same class on both sides -> that class, else paragraph direction
    i = 0
    n = len(cl)
    while i < n:
        if cl[i] == 'N':
            j = i
            while j < n and cl[j] == 'N':
                j += 1
            left = cl[i - 1] if i else base
            right = cl[j] if j < n else base
            fill = left if left == right else base
            for k in range(i, j):
                cl[k] = fill
            i = j
        else:
            i += 1
    out = []
    for ch, c in zip(text, cl):
        if out and out[-1][1] == c:
            out[-1][0] += ch
        else:
            out.append([ch, c])
    if rtl:
        out.reverse()
    return [(t, c) for t, c in out]


_MIRROR = str.maketrans('()[]«»', ')(][»«')


def line(rend, text, px, rtl=False):
    ims = []
    for t, c in runs(text, rtl):
        im, adv = rend.line(t, px, direction='rtl' if c == 'R' else 'ltr')
        ims.append((im, adv))
    W = int(sum(a for _, a in ims)) + 8
    H = max(i.height for i, _ in ims)
    page = Image.new('L', (W, H), 0)
    x = 0.0
    from PIL import ImageChops
    for im, adv in ims:
        tmp = Image.new('L', (W, H), 0)
        tmp.paste(im, (int(round(x)), 0))
        page = ImageChops.add(page, tmp)
        x += adv
    return page


def wrap(rend, text, px, width, rtl=False):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if sum(a for _, a in [rend.line(r, px, direction='rtl' if c == 'R' else 'ltr') for r, c in runs(t, rtl)]) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def paragraph(rend, text, px, width, rtl=False, leading=1.45):
    ls = [line(rend, t, px, rtl) for t in wrap(rend, text, px, width, rtl)]
    lh = int(px * leading)
    page = Image.new('L', (width + 8, lh * len(ls) + 10), 0)
    for i, im in enumerate(ls):
        x = (width + 8 - im.width) if rtl else 0
        page.paste(im, (max(x, 0), i * lh))
    return page
