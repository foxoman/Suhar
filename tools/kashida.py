"""Kashida justification: where a tatweel may go, and a line breaker that uses it.

A font cannot justify a line; the application does.  This file is the rule set I use for Suhar, as code that can be
called or ported (site/kashida.js is the same logic for the web):

    1  after a joined seen or sad             سـ شـ صـ ضـ
    2  before a final heh, teh marbuta, dal    ـه ـة ـد ـذ
    3  before a final alef, lam, kaf           ـا ـل ـك
    4  before a final reh, yeh, noon, ain ...  ـر ـي ـن ـع
    5  between two other joined letters        ـبـ
    never: after a letter that does not join forward, inside lam-alef, at the edge of a word, in a word of two letters

One kashida per place; the longest words get them first; what is left over goes to the word spaces.

    python3 tools/kashida.py FONT.ttf SIZE WIDTH < text.txt        (SIZE and WIDTH in the same unit, e.g. points)"""
import sys
import unicodedata

TATWEEL = 'ـ'
RIGHT_ONLY = set('اأإآٱدذرزوؤةىءٹڈڑژۃے')                       # do not join to the following letter
SEEN, P2, P3, P4 = set('سشصض'), set('هةدذ'), set('الك'), set('ريىنعغز')


def is_mark(c):
    return unicodedata.category(c) in ('Mn', 'Me')


def is_arabic(c):
    return 'ؠ' <= c <= 'ۿ' and c != TATWEEL and not is_mark(c) and unicodedata.category(c).startswith('L')


def places(word):
    """[(priority, index)]: a tatweel may be inserted before word[index]"""
    letters = [i for i, c in enumerate(word) if is_arabic(c)]
    if len(letters) < 3 or TATWEEL in word:
        return []
    out = []
    for a, b in zip(letters, letters[1:]):
        ca, cb = word[a], word[b]
        if ca in RIGHT_ONLY or (ca == 'ل' and cb in 'اأإآٱ'):
            continue
        last = b == letters[-1]
        if ca in SEEN:
            pr = 1
        elif last and cb in P2:
            pr = 2
        elif last and cb in P3:
            pr = 3
        elif last and cb in P4:
            pr = 4
        else:
            pr = 5
        out.append((pr, b))
    return out


def justify(words, width, measure, max_per_word=1):
    """Stretch a line of words to `width` with kashidas; -> (words, width reached).  measure(text) -> width."""
    words = list(words)
    used = [0] * len(words)
    cur = measure(' '.join(words))
    while True:
        cand = []
        for wi, w in enumerate(words):
            if used[wi] >= max_per_word:
                continue
            for pr, idx in places(w):
                cand.append((pr, used[wi], -len(w), wi, idx))
        if not cand:
            break
        pr, _, _, wi, idx = min(cand)
        trial = words[wi][:idx] + TATWEEL + words[wi][idx:]
        new = measure(' '.join(words[:wi] + [trial] + words[wi + 1:]))
        if new > width:
            used[wi] = max_per_word                       # this word cannot take one; try the others
            continue
        words[wi], cur = trial, new
        used[wi] += 1
    return words, cur


def break_lines(text, width, measure):
    lines, cur = [], []
    for w in text.split():
        if cur and measure(' '.join(cur + [w])) > width:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def hb_measure(font_path, size):
    import uharfbuzz as hb
    face = hb.Face(open(font_path, 'rb').read())
    font = hb.Font(face)
    upm = face.upem

    def m(text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf)
        return sum(p.x_advance for p in buf.glyph_positions) * size / upm
    return m


if __name__ == '__main__':
    path, size, width = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    m = hb_measure(path, size)
    ls = break_lines(sys.stdin.read(), width, m)
    for i, l in enumerate(ls):
        if i < len(ls) - 1:
            l, w = justify(l, width, m)
        print(' '.join(l))
