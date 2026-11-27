"""An npm package of the web fonts (woff2 and one CSS file per family), for `npm pack` / `npm publish`.
    python3 tools/make_npm.py [OUTDIR]        writes OUTDIR/package (default build/npm)"""
import json, os, re, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'build', 'npm'), 'package')
VER = '.'.join(re.findall(r'VERSION = \((\d+), (\d+)\)', open(os.path.join(ROOT, 'src', 'retrofont', 'ufo.py')).read())[0]) + '.0'
W = {'Light': 300, 'Regular': 400, 'Medium': 500, 'SemiBold': 600, 'Bold': 700, 'ExtraBold': 800, 'Black': 900}
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(os.path.join(OUT, 'files'))
fams = {}
src = os.path.join(ROOT, 'dist', 'woff2')
for f in sorted(os.listdir(src)):
    m = re.match(r'(Suhar[A-Za-z]*)-([A-Za-z]+)\.woff2$', f)
    if not m or 'Nerd' in f:
        continue
    ps, sn = m.groups()
    it = sn.endswith('Italic')
    wn = sn[:-6] if it else sn
    wn = wn or 'Regular'
    if wn not in W:
        continue
    shutil.copy(os.path.join(src, f), os.path.join(OUT, 'files', f))
    fam = re.sub(r'(?<!^)([A-Z])', r' \1', ps)
    fams.setdefault((fam, ps), []).append((W[wn], it, f))
for f in sorted(os.listdir(os.path.join(ROOT, 'dist', 'variable'))):
    if f.endswith('.woff2'):
        shutil.copy(os.path.join(ROOT, 'dist', 'variable', f), os.path.join(OUT, 'files', f))
css_all = []
for (fam, ps), faces in sorted(fams.items()):
    css = ''.join(f"@font-face{{font-family:\"{fam}\";src:url(\"./files/{f}\") format(\"woff2\");font-weight:{w};font-style:{'italic' if it else 'normal'};font-display:swap}}\n"
                  for w, it, f in sorted(faces))
    name = ps.lower().replace('suhar', 'suhar-').rstrip('-') + '.css'
    open(os.path.join(OUT, name), 'w').write(css)
    css_all.append(name)
open(os.path.join(OUT, 'index.css'), 'w').write(''.join(f'@import "./{n}";\n' for n in css_all))
for f in ('OFL.txt', 'CHANGELOG.md'):
    if os.path.exists(os.path.join(ROOT, f)):
        shutil.copy(os.path.join(ROOT, f), OUT)
open(os.path.join(OUT, 'README.md'), 'w').write(
    "# Suhar web fonts\n\nSuhar, a typeface family for Arabic and Latin by Sultan Al Isaiee (www.foxoman.net), as woff2 files with one CSS file per family.\n\n"
    "```js\nimport \"@foxoman/suhar/suhar.css\";          // Suhar\nimport \"@foxoman/suhar/suhar-sahafa.css\";   // Suhar Sahafa\n```\n\n"
    "```css\nbody { font-family: \"Suhar\", sans-serif; }\n```\n\nCSS files: " + ', '.join(f'`{n}`' for n in css_all) +
    ". The variable fonts are in `files/` as well.\n\nLicence: SIL Open Font License 1.1 (`OFL.txt`).\n")
json.dump({'name': '@foxoman/suhar', 'version': VER, 'description': 'Suhar: a typeface family for Arabic and Latin (web fonts)',
           'keywords': ['font', 'arabic', 'naskh', 'typeface', 'woff2', 'suhar'], 'author': 'Sultan Al Isaiee (https://www.foxoman.net)',
           'license': 'OFL-1.1', 'style': 'index.css', 'files': ['files', '*.css', 'OFL.txt', 'CHANGELOG.md', 'README.md'], 'publishConfig': {'access': 'public'}},
          open(os.path.join(OUT, 'package.json'), 'w'), indent=2)
print(OUT, len(css_all), 'families', len(os.listdir(os.path.join(OUT, 'files'))), 'files', VER)
