"""proof sheet of the 1.3 additions; fonts from a directory given as argv[1] (file stems as in build/quick)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proof import Renderer
from layout import line
from PIL import Image

def L(path, text, px=44, feat=None, rtl=False):
    r = Renderer(path)
    if feat:
        orig = r.shape
        r.shape = lambda t, features=None, **kw: orig(t, {**(features or {}), **feat}, **kw)
    return line(r, text, px, rtl=rtl)

def page(rows, out, gap=14):
    W = max(r.width for r in rows) + 40; H = sum(r.height + gap for r in rows) + 40
    pg = Image.new('L', (W, H), 0); y = 20
    for r in rows:
        pg.paste(r, (20, y)); y += r.height + gap
    Image.eval(pg, lambda v: 255 - v).save(out)

if __name__ == '__main__':
    Q = sys.argv[1]; out = sys.argv[2]
    f = lambda n: os.path.join(Q, n + '.ttf')
    N = dict(L='Suhar-Light', R='Suhar-Regular', XB='Suhar-ExtraBold', C='SuharCondensed-Regular', CB='SuharCondensed-Bold',
             ML='SuharMono-Light', M='SuharMono-Regular', MX='SuharMono-ExtraBold') if len(sys.argv) > 3 else {}
    g = lambda k: f(N.get(k, k))
    T = "Suhar صحار مدينة عُمانية 0123"
    rows = [L(g('L'), "Light  " + T), L(g('R'), "Regular  " + T), L(g('XB'), "ExtraBold  " + T),
            L(g('C'), "Condensed  Sohar Port and Freezone — ميناء صحار والمنطقة الحرة 240 km"),
            L(g('CB'), "Condensed Bold  Sohar Port — ميناء صحار والمنطقة الحرة"),
            L(g('R'), "default: young jogging Quay Jy"), L(g('R'), "ss01: young jogging Quay Jy", feat={'ss01': True}),
            L(g('R'), "دور وزير يرى نور", rtl=True), L(g('R'), "دور وزير يرى نور", feat={'ss01': True}, rtl=True),
            L(g('R'), "لم لحم الحج في المخ  ببببب تتنبيت", feat={'calt': False}, rtl=True),
            L(g('R'), "لم لحم الحج في المخ  ببببب تتنبيت", feat={'dlig': True}, rtl=True),
            L(g('R'), "0O 100 default"), L(g('R'), "0O 100 ss02", feat={'ss02': True}), L(g('R'), "0O 100 zero", feat={'zero': True}),
            L(g('R'), ''.join(chr(c) + ' ' for c in range(0xE130, 0xE144)), 64),
            L(g('ML'), "Light mono  fn main() := x |> y  مرحبا"), L(g('M'), "Regular mono := |> != => مرحبا", feat={'dlig': True}),
            L(g('MX'), "ExtraBold mono 0O1lI مرحبا بالعالم")]
    page(rows, out)
