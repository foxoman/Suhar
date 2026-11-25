"""Write dist/build-report.json from what the compiled files actually contain
(used after a partial rebuild, when build.py only reported the styles it rebuilt)."""
import glob, json, os
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'dist')
rep = {'source': 'inspected from the files in dist/ by tools/inspect_build.py', 'static': [], 'variable': []}
for p in sorted(glob.glob(os.path.join(D, 'ttf', '*.ttf'))):
    b = os.path.basename(p)
    if 'Nerd' in b:
        continue
    f = TTFont(p)
    o = TTFont(os.path.join(D, 'otf', b.replace('.ttf', '.otf')))
    cs = o['CFF '].cff.topDictIndex[0].CharStrings['n']
    cs.decompile()
    rep['static'].append({'name': b[:-4], 'glyphs': len(f.getGlyphOrder()),
                          'hinted': all(t in f for t in ('fpgm', 'prep', 'cvt ')),
                          'otf_hinted': any(op in cs.program for op in ('hstem', 'vstem', 'hstemhm', 'vstemhm'))})
for p in sorted(glob.glob(os.path.join(D, 'variable', '*.ttf'))):
    b = os.path.basename(p)
    v = TTFont(p)
    stat = 'SuharMono' if 'Mono' in b else 'SuharCondensed' if 'Condensed' in b else 'Suhar'
    s = TTFont(os.path.join(D, 'ttf', f"{stat}-{'Italic' if 'Italic' in b else 'Regular'}.ttf"))
    missing = sorted(set(s.getGlyphOrder()) - set(v.getGlyphOrder()))
    rep['variable'].append({'name': b, 'axes': [a.axisTag for a in v['fvar'].axes], 'dropped_glyphs': missing})
json.dump(rep, open(os.path.join(D, 'build-report.json'), 'w'), indent=1)
print(len(rep['static']), 'static;', [(v['name'], v['dropped_glyphs']) for v in rep['variable']])
print('all ttf hinted:', all(s['hinted'] for s in rep['static']), '| all otf hinted:', all(s['otf_hinted'] for s in rep['static']))
