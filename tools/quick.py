"""quick single-style compile for design iteration"""
import sys, time
sys.path.insert(0, 'src'); sys.path.insert(0, 'tools')
from retrofont.model import Style, build_glyphs, GlyphOut
from retrofont import latin
from retrofont.ufo import make_ufo
import ufo2ft

def quick(path, family='Sans', wght=400, italic=False, opsz=0, mods=()):
    for m in mods: __import__('retrofont.' + m)
    st = Style(family, wght, italic, opsz)
    t = time.time()
    gl = build_glyphs(st)
    gl['.notdef'] = GlyphOut('.notdef', [], [], 500)
    from retrofont.features import make_features
    ufo = make_ufo(st, gl, 'RetroUI ' + family, make_features(gl) if 'arabic' in mods else '')
    ttf = ufo2ft.compileTTF(ufo, removeOverlaps=False)
    ttf.save(path)
    print(path, len(gl), 'glyphs', round(time.time() - t, 1), 's')
    return path

if __name__ == '__main__':
    import os
    os.makedirs('build/quick', exist_ok=True)
    mods = [m for m in sys.argv[1:] if not m.startswith('-')]
    quick('build/quick/R.ttf', mods=mods)
    quick('build/quick/B.ttf', wght=700, mods=mods)
    quick("build/quick/I.ttf", italic=True, mods=mods)
    quick('build/quick/M.ttf', family='Mono', mods=mods)
    quick('build/quick/MB.ttf', family='Mono', wght=700, mods=mods)
