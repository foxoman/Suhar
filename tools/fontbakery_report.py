"""reports/fontbakery.md: Fontbakery's universal checks on one font of each family."""
import json, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = ['Suhar-Regular', 'Suhar-Bold', 'SuharCondensed-Regular', 'SuharMono-Regular', 'SuharNaskh-Regular', 'SuharNaskhDisplay-Regular',
         'SuharSahafa-Regular', 'SuharSahafa-Italic', 'SuharSahafaHeadline-Bold', 'SuharSahafaCaption-Regular', 'SuharTypewriter-Regular']
rows, detail = [], {}
for f in FONTS:
    p = os.path.join(ROOT, 'dist', 'ttf', f + '.ttf')
    if not os.path.exists(p):
        continue
    out = os.path.join(tempfile.gettempdir(), f + '.fb.json')
    subprocess.run(['fontbakery', 'check-universal', '--json', out, '-q', '-n', p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1200)
    if not os.path.exists(out):
        rows.append((f, 'did not run', '', '', '', ''))
        continue
    r = json.load(open(out)).get('result', {})
    rows.append((f, r.get('PASS', 0), r.get('WARN', 0), r.get('FAIL', 0), r.get('ERROR', 0), r.get('SKIP', 0)))
    for sec in json.load(open(out)).get('sections', []):
        for c in sec.get('checks', []):
            if c.get('result') in ('FAIL', 'ERROR'):
                detail.setdefault((c.get('result'), (c.get('key', ['', '', ''])[1] if isinstance(c.get('key'), list) else str(c.get('key'))).replace('<FontBakeryCheck:', '').rstrip('>')), []).append(f)
L = ['# Suhar – Fontbakery', '', 'Fontbakery ' + subprocess.run(['fontbakery', '--version'], capture_output=True, text=True).stdout.strip() +
     ', profile `universal`, on one font of each family. These are another tool\'s checks, run as they are; nothing was switched off.', '',
     '| font | pass | warn | fail | error | skip |', '|---|---:|---:|---:|---:|---:|'] + ['| ' + ' | '.join(str(x) for x in r) + ' |' for r in rows]
if detail:
    L += ['', '## Failing checks', ''] + [f'- **{k[0]}** `{k[1]}` — {len(v)} of {len(rows)} fonts' for k, v in sorted(detail.items())]
open(os.path.join(ROOT, 'reports', 'fontbakery.md'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L[4:]))
