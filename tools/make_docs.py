"""Generate docs/COVERAGE.md, docs/ICONS.md, specimen/index.html and the
printable glyph catalogue PDF from the compiled fonts in dist/."""
import os, sys, json, unicodedata as ud, html
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen


class CanvasPen(BasePen):
    def __init__(self, glyphSet, path):
        super().__init__(glyphSet)
        self.path = path

    def _moveTo(self, p):
        self.path.moveTo(*p)

    def _lineTo(self, p):
        self.path.lineTo(*p)

    def _curveToOne(self, a, b, c):
        self.path.curveTo(a[0], a[1], b[0], b[1], c[0], c[1])

    def _closePath(self):
        self.path.close()

from fontTools.pens.boundsPen import BoundsPen
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist')
DOCS = os.path.join(ROOT, 'docs')
os.makedirs(DOCS, exist_ok=True)
os.makedirs(os.path.join(ROOT, 'specimen'), exist_ok=True)
F = TTFont(os.path.join(DIST, 'ttf', 'Suhar-Regular.ttf'))
FN = TTFont(os.path.join(DIST, 'ttf', 'SuharNerdMono-Regular.ttf'))
cmap = F.getBestCmap()
rep = json.load(open(os.path.join(ROOT, 'reports', 'validation.json'))) if os.path.exists(os.path.join(ROOT, 'reports', 'validation.json')) else None


def ranges(cps):
    cps = sorted(cps)
    out = []
    s = p = cps[0]
    for c in cps[1:]:
        if c != p + 1:
            out.append((s, p))
            s = c
        p = c
    out.append((s, p))
    return ' '.join(('%04X' % a) if a == b else ('%04X–%04X' % (a, b)) for a, b in out)


# ---------------------------------------------------------------- COVERAGE.md
BL = [(0x0000, 0x007F, 'Basic Latin'), (0x0080, 0x00FF, 'Latin-1 Supplement'), (0x0100, 0x017F, 'Latin Extended-A'),
      (0x0180, 0x024F, 'Latin Extended-B'), (0x02B0, 0x02FF, 'Spacing Modifier Letters'), (0x0300, 0x036F, 'Combining Diacritical Marks'),
      (0x0370, 0x03FF, 'Greek and Coptic'), (0x0400, 0x04FF, 'Cyrillic'), (0x0590, 0x05FF, 'Hebrew'), (0x1F00, 0x1FFF, 'Greek Extended'), (0x0600, 0x06FF, 'Arabic'), (0x0E00, 0x0E7F, 'Thai'),
      (0x1E00, 0x1EFF, 'Latin Extended Additional'), (0x2000, 0x206F, 'General Punctuation'), (0x2070, 0x209F, 'Superscripts and Subscripts'),
      (0x20A0, 0x20CF, 'Currency Symbols'), (0x2100, 0x214F, 'Letterlike Symbols'), (0x2150, 0x218F, 'Number Forms'),
      (0x2190, 0x21FF, 'Arrows'), (0x2200, 0x22FF, 'Mathematical Operators'), (0x2300, 0x23FF, 'Miscellaneous Technical'),
      (0x2500, 0x257F, 'Box Drawing'), (0x2580, 0x259F, 'Block Elements'), (0x25A0, 0x25FF, 'Geometric Shapes'),
      (0x2600, 0x26FF, 'Miscellaneous Symbols'), (0x2700, 0x27BF, 'Dingbats'), (0x2800, 0x28FF, 'Braille Patterns'),
      (0x2B00, 0x2BFF, 'Miscellaneous Symbols and Arrows'), (0x3000, 0x303F, 'CJK Symbols and Punctuation'),
      (0xE000, 0xF8FF, 'Private Use Area'), (0xFB50, 0xFDFF, 'Arabic Presentation Forms-A'),
      (0xFE70, 0xFEFF, 'Arabic Presentation Forms-B'), (0x1FB00, 0x1FBFF, 'Symbols for Legacy Computing')]
L = ['# Unicode coverage', '', 'Generated from `dist/ttf/Suhar-Regular.ttf` by `tools/make_docs.py`. '
     'Suhar Mono has the same character set. The Nerd families add the Nerd Fonts icons (see ICONS.md).', '',
     f'**{len(cmap)} code points, {len(F.getGlyphOrder())} glyphs** (the difference is contextual Arabic forms, ligatures and components).', '',
     '| Block | Range | In font | Assigned in block | Code points |', '|---|---|---:|---:|---|']
for lo, hi, nm in BL:
    have = [c for c in cmap if lo <= c <= hi]
    if not have:
        continue
    assigned = sum(1 for c in range(lo, hi + 1) if ud.category(chr(c)) not in ('Cn', 'Co'))
    L.append(f"| {nm} | {lo:04X}–{hi:04X} | {len(have)} | {assigned if assigned else '–'} | {ranges(have)} |")
L += ['', '## What is deliberately complete', '',
      '- Basic Latin, Latin-1, Latin Extended-A; Vietnamese and the other precomposed letters of Latin Extended Additional that decompose to letters and marks the font has.',
      '- Arabic letters U+0621–064A, tashkeel U+064B–0652, Persian پ چ ژ گ ک ی, Urdu ٹ ڈ ڑ ں ھ ہ ۂ ۃ ے ۓ, both digit sets, the presentation-form code points of all of these.',
      '- Box Drawing (128), Block Elements (32), Braille Patterns (256), sextants U+1FB00–1FB3B.', '',
      '## What is a subset', '',
      '- Greek: monotonic and polytonic (precomposed U+1F00–1FFF; breathings and accents are stacked above the letter).',
      '- Cyrillic: Russian, Ukrainian, Belarusian, Bulgarian, Serbian, Macedonian and Kazakh; no other extensions.',
      '- Hebrew: the 27 letters, maqaf, geresh, gershayim; no niqqud or cantillation marks.',
      '- Arabic: Kurdish ڵ ڕ ۆ ێ and Jawi ڠ ڽ ڭ are included; no Sindhi, Pashto, Uyghur or African letters; U+06DD END OF AYAH is a plain ring that does not enclose digits.',
      '- Mathematical Operators, Arrows, Miscellaneous Technical, Geometric Shapes, Miscellaneous Symbols, Dingbats, Number Forms: the commonly used characters only (see the table).',
      '- Currency: 28 signs including U+20C4 Omani rial, U+20C1 Saudi riyal, U+20C3 UAE dirham; not every sign in the block.']
open(os.path.join(DOCS, 'COVERAGE.md'), 'w').write('\n'.join(L) + '\n')

# ---------------------------------------------------------------- ICONS.md
from retrofont import model, latin, latin_ext, arabic, terminal, symbols, greek_cyrillic, more_scripts   # noqa
ncm = FN.getBestCmap()
NERD = [('Seti-UI + Custom', 0xE5FA, 0xE6BB), ('Devicons', 0xE700, 0xE8EF), ('Font Awesome', 0xED00, 0xF2FF),
        ('Font Awesome Extension', 0xE200, 0xE2A9), ('Material Design', 0xF0001, 0xF1AF0), ('Weather', 0xE300, 0xE3E3),
        ('Octicons', 0xF400, 0xF533), ('Powerline + Extra', 0xE0A0, 0xE0D7), ('IEC Power', 0x23FB, 0x23FE),
        ('Font Logos', 0xF300, 0xF381), ('Pomicons', 0xE000, 0xE00A), ('Codicons', 0xEA60, 0xEC1E)]
L = ['# Icon and private-use mapping', '', '## Suhar interface icons (all four families)', '',
     'Original drawings in the Private Use Area. The block U+E100–E1FF is not used by Nerd Fonts 3.5.1; '
     '`tools/validate.py` checks that the Nerd build keeps these glyphs.', '', '| Code point | Glyph name | Nim (`suhar.nim`) |', '|---|---|---|']
nimnames = {0xE100: 'siOmanEmblem', 0xE101: 'siCrossedSwords', 0xE102: 'siKhanjar'}
for cp, nm in sorted(symbols.ICONS.items()):
    ni = nimnames.get(cp) or 'si' + ''.join(p.capitalize() for p in nm.split('-'))
    L.append(f'| U+{cp:04X} | retroui.{nm} | `{ni}` |')
L += ['', 'U+E100 is a simplified, original drawing of a khanjar over crossed swords. It is **not** the official artwork of the national emblem of Oman and must not be used where the official emblem is required.', '',
      '## Powerline (drawn by Suhar on the exact Mono cell)', '', '| Code points | Content |', '|---|---|',
      '| U+E0A0–E0A3 | branch, line number, lock, column number |', '| U+E0B0–E0B3 | solid and outline arrow separators |',
      '| U+E0B4–E0B7 | half-round separators |', '| U+E0B8–E0BF | corner triangles and diagonals |', '',
      '## Nerd Fonts 3.5.1 icons (Suhar Nerd and Suhar Nerd Mono only)', '',
      'Merged unchanged in shape from the official *Symbols Nerd Font* (see LICENSES). Where Suhar already has a glyph for a code point the Suhar glyph is kept. '
      'In Suhar Nerd Mono every icon is scaled to fit one 600-unit cell; in Suhar Nerd icons keep their own width.', '',
      '| Set | Range | Code points present |', '|---|---|---:|']
for nm, lo, hi in NERD:
    L.append(f'| {nm} | U+{lo:04X}–U+{hi:04X} | {sum(1 for c in ncm if lo <= c <= hi)} |')
L += ['', f'Total code points in Suhar Nerd Mono: {len(ncm)}.', '',
      'For the name of each Nerd icon use the upstream cheat sheet: https://www.nerdfonts.com/cheat-sheet']
open(os.path.join(DOCS, 'ICONS.md'), 'w').write('\n'.join(L) + '\n')

# ---------------------------------------------------------------- specimen
icons_html = ''.join(f'<span title="U+{cp:04X} {nm}">&#x{cp:X};</span>' for cp, nm in sorted(symbols.ICONS.items()))
styles = [('Light', 300, 'normal'), ('LightItalic', 300, 'italic'), ('ExtraBold', 800, 'normal'), ('ExtraBoldItalic', 800, 'italic'),
          ('Regular', 400, 'normal'), ('Italic', 400, 'italic'), ('Medium', 500, 'normal'), ('MediumItalic', 500, 'italic'),
          ('SemiBold', 600, 'normal'), ('SemiBoldItalic', 600, 'italic'), ('Bold', 700, 'normal'), ('BoldItalic', 700, 'italic')]
faces = ''
for fam, stem in (('Suhar', 'Suhar'), ('Suhar Mono', 'SuharMono'), ('Suhar Nerd Mono', 'SuharNerdMono'), ('Suhar Nerd', 'SuharNerd')):
    for sn, w, st in styles:
        faces += (f"@font-face{{font-family:'{fam}';src:url('../dist/woff2/{stem}-{sn}.woff2') format('woff2');"
                  f"font-weight:{w};font-style:{st};font-display:swap}}\n")
for sn, w, st in styles:
    if 'Light' not in sn and 'ExtraBold' not in sn:
        faces += (f"@font-face{{font-family:'Suhar Condensed';src:url('../dist/woff2/SuharCondensed-{sn}.woff2') format('woff2');"
                  f"font-weight:{w};font-style:{st};font-display:swap}}\n")
faces += ("@font-face{font-family:'Suhar VF';src:url('../dist/variable/Suhar[opsz,wght].woff2') format('woff2');font-weight:400 700;font-style:normal}\n"
          "@font-face{font-family:'Suhar VF';src:url('../dist/variable/Suhar-Italic[opsz,wght].woff2') format('woff2');font-weight:400 700;font-style:italic}\n")
EN = ("Suhar (صُحار) is one of the oldest ports of Oman. For centuries its harbour linked Arabia with India, East Africa and China, "
      "and sailors told the tales of Sindbad the Sailor about voyages that began here. Today the city is known for Sohar Fort, "
      "the corniche, the Friday souq and a modern port that handles more than 60 million tonnes of cargo a year.")
AR = ("صُحار مدينة عُمانية عريقة على ساحل بحر عُمان، وتُعرف بالإنجليزية باسم Sohar. كانت قديماً من أهم موانئ المنطقة، ومنها أبحر "
      "التجار إلى الهند والصين وشرق أفريقيا، وارتبط اسمها بحكايات السندباد البحري. تضم المدينة اليوم قلعة صحار وميناءً حديثاً "
      "يبعد نحو 240 كم عن مسقط.")
TERM = """┌──────────────┬──────────┐  ╔════════╗
│ fn main()    │ 0O 1lI | │  ║ ▁▂▃▄▅▆▇█ ║
├──────────────┼──────────┤  ╠════════╣
│ نص عربي       │ ░▒▓█ ⣿⡇ │  ║ ✓ ● ◆ ▶ ║
└──────────────┴──────────┘  ╚════════╝
  main  ~/src/ned    1  12:30 """
CODE = '''proc greet(name: string): int =   # 0O 1lI| {}[]() <>= != -> =>
  echo "Hello, " & name & "!"      # مرحبا
  result = 0xFF + 42_000'''
page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Suhar – type specimen</title>
<style>
{faces}
:root{{--ink:#14202b;--paper:#f6f1e6;--sea:#0c4a6e;--sand:#c98b3a;--line:#d8cfbd}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:'Suhar',sans-serif;line-height:1.5}}
header{{background:var(--sea);color:#fff;padding:7vw 6vw 5vw}}
header h1{{font-size:clamp(64px,17vw,230px);line-height:.95;margin:0;font-weight:700;letter-spacing:-.01em}}
header h1 span{{color:#ffd678}}
header p{{font-size:clamp(18px,2.4vw,30px);max-width:34em;margin:1.2em 0 0}}
main{{padding:0 6vw 6vw}}
section{{border-top:2px solid var(--ink);margin-top:56px;padding-top:14px}}
h2{{font-size:15px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;margin:0 0 22px;color:var(--sea)}}
.w div{{font-size:clamp(28px,5vw,64px);white-space:nowrap;overflow:hidden;line-height:1.25}}
.cols{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:40px}}
.ar{{direction:rtl;text-align:right;line-height:1.9}}
.big{{font-size:clamp(20px,2.2vw,28px)}} .txt{{font-size:17px}} .sm{{font-size:13px}}
.sizes div{{white-space:nowrap;overflow:hidden}}
pre{{font-family:'Suhar Nerd Mono','Suhar Mono',monospace;font-size:clamp(11px,1.7vw,20px);line-height:1.28;background:#10202c;color:#e9f1f5;padding:24px;overflow:auto;margin:0}}
.ui{{background:#c0c0c0;border:2px solid;border-color:#fff #555 #555 #fff;padding:3px;max-width:520px;font-size:13px}}
.ui .t{{background:#000080;color:#fff;padding:3px 8px;font-weight:700;display:flex;justify-content:space-between}}
.ui .m{{padding:3px 8px;display:flex;gap:16px}} .ui .b{{background:#fff;border:2px solid;border-color:#555 #fff #fff #555;padding:14px;min-height:70px}}
.ui button{{font:inherit;background:#c0c0c0;border:2px solid;border-color:#fff #555 #555 #fff;padding:3px 22px;margin:10px 6px 4px 0}}
.icons{{font-size:38px;line-height:1.5;word-spacing:.35em;letter-spacing:.25em}}
.glyphs{{font-size:30px;line-height:1.6;word-break:break-all}}
.vf{{font-family:'Suhar VF';font-size:clamp(40px,9vw,120px);line-height:1.1;font-optical-sizing:none}}
input[type=range]{{width:260px}} label{{font-size:14px;margin-right:24px}}
table{{border-collapse:collapse;font-size:14px}} td,th{{border-bottom:1px solid var(--line);padding:5px 14px 5px 0;text-align:left}}
footer{{padding:40px 6vw;font-size:13px;border-top:1px solid var(--line)}}
@media print{{header{{background:none;color:#000}} header h1 span{{color:#000}} pre{{background:none;color:#000;border:1px solid #000}}}}
</style></head><body>
<header><h1>Suhar <span lang="ar">صُحار</span></h1>
<p>A typeface for Latin and Arabic, named after the port of Suhar in Oman, the legendary home of Sindbad the Sailor. Four families, eight styles each, drawn from one set of parametric stroke skeletons.</p></header>
<main>
<section class="w"><h2>Styles</h2>
<div style="font-weight:400">Regular — Handgloves العربية 0123456789</div>
<div style="font-weight:400;font-style:italic">Italic — Handgloves العربية 0123456789</div>
<div style="font-weight:500">Medium — Handgloves العربية 0123456789</div>
<div style="font-weight:600">SemiBold — Handgloves العربية 0123456789</div>
<div style="font-weight:700">Bold — Handgloves العربية 0123456789</div>
<div style="font-weight:700;font-style:italic">Bold Italic — Handgloves العربية</div></section>
<section><h2>Text</h2><div class="cols"><div><p class="big">{html.escape(EN)}</p><p class="txt">{html.escape(EN)}</p><p class="sm">{html.escape(EN)}</p></div>
<div class="ar" lang="ar"><p class="big">{html.escape(AR)}</p><p class="txt">{html.escape(AR)}</p><p class="sm">{html.escape(AR)}</p></div></div></section>
<section><h2>Tashkeel, Persian, Urdu</h2><p class="ar big" lang="ar">بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ ﷲ ﷺ ﷻ ۞ ۩ ﴿قُلْ هُوَ اللَّهُ أَحَدٌ﴾</p>
<p class="ar big" lang="fa">فارسی: این یک نمونهٔ متن است — گفت‌وگو، پژوهش، چگونه ۰۱۲۳۴۵۶۷۸۹</p>
<p class="ar big" lang="ur">اردو: یہ ایک نمونہ ہے — کتاب، گھر، ٹھیک، بڑے</p></section>
<section><h2>Greek and Cyrillic</h2><p class="big">Ελληνικά: Ξεσκεπάζω την ψυχοφθόρα βδελυγμία. ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ</p><p class="big">Русский: Съешь ещё этих мягких французских булок, да выпей чаю. Українська: Їжак з’їв ґанок. Српски: Љубазни фењерџија. Қазақша: Әлемге сәлем.</p><p class="big">Ἐν ἀρχῇ ἦν ὁ λόγος. &nbsp; <span dir="rtl" lang="he">עברית: שלום עולם, ברוכים הבאים לסוחאר</span></p></section>
<section><h2>Features</h2><p class="big"><span style="font-feature-settings:'frac'">frac: 1/2 3/4 1/3</span> &nbsp; <span style="font-feature-settings:'zero'">zero: 2026 0O</span> &nbsp; <span style="font-family:'Suhar Mono';font-feature-settings:'dlig'">dlig (Mono): -&gt; =&gt; != &lt;= &gt;= == &lt;-</span> &nbsp; <i>italic a: banana</i></p></section>
<section class="sizes"><h2>Small sizes</h2>{''.join(f'<div style="font-size:{px}px">{px}px — The quick brown fox jumps over the lazy dog. نص عربي للتجربة 0123456789</div>' for px in (8,9,10,11,12,13,14,16,18,24))}</section>
<section><h2>Interface</h2><div class="ui"><div class="t"><span>&#xE113; Suhar – Glyph Specimen</span><span>&#xE110; &#xE111; &#xE114;</span></div>
<div class="m"><span>File</span><span>Edit</span><span>View</span><span>Help</span><span style="margin-inline-start:auto">ملف تحرير عرض</span></div>
<div class="b">&#xE116; Windows 3.1 style &nbsp; &#xE118; English &amp; Arabic &nbsp; &#xE120; Documents &nbsp; &#xE122; Save<br>Price: 2.500 &#x20C4; &nbsp; 10 &#x20C1; &nbsp; 10 &#x20C3; &nbsp; €12 £9 ¥100 ₹50</div>
<button><b>OK</b></button><button>Cancel</button><button>موافق</button></div></section>
<section><h2>Suhar Mono and Suhar Nerd Mono</h2><pre>{html.escape(CODE)}

{html.escape(TERM)}</pre></section>
<section><h2>New in 1.3</h2><p class="big" style="font-weight:300">Light — Suhar صحار مدينة عُمانية</p><p class="big" style="font-weight:800">ExtraBold — Suhar صحار مدينة عُمانية</p>
<p class="big" style="font-family:'Suhar Condensed'">Condensed — Sohar Port and Freezone · ميناء صحار والمنطقة الحرة</p>
<p class="big">young jogging Quay · <span style="font-feature-settings:'ss01'">young jogging Quay (ss01)</span></p>
<p class="ar big" lang="ar">دور وزير نور · <span style="font-feature-settings:'ss01'">دور وزير نور (ss01)</span> · لم الحج في · <span style="font-feature-settings:'dlig'">لم الحج في (dlig)</span></p>
<p class="big">0O · <span style="font-feature-settings:'ss02'">0O ss02</span> · <span style="font-feature-settings:'zero'">0O zero</span></p></section>
<section><h2>Suhar icons, ornaments and pictograms (U+E100–E148)</h2><div class="icons">{icons_html}</div></section>
<section><h2>Symbols</h2><div class="glyphs">€ £ ¥ ₹ ₽ ₺ ₩ ₪ ₿ &#x20C4; &#x20C1; &#x20C3; ← ↑ → ↓ ↔ ⇒ ⇔ ∞ ≈ ≠ ≤ ≥ ± × ÷ √ ∑ ∏ ∫ ∂ ∆ Ω π µ ⌘ ⌥ ⇧ ⌫ ⏎ ■ □ ▲ ▼ ◆ ● ○ ★ ☆ ✓ ✗ ☑ ☒ ♠ ♥ ♦ ♣ ♪ ⚠ ⚡</div></section>
<section><h2>Variable font (wght 400–700, opsz 8–72)</h2>
<p><label>Weight <input id="w" type="range" min="400" max="700" value="400"></label><label>Optical size <input id="o" type="range" min="8" max="72" value="14"></label></p>
<div class="vf" id="vf">Sindbad السندباد</div></section>
<section><h2>Files</h2><table><tr><th>Family</th><th>Use</th></tr>
<tr><td>Suhar</td><td>text, interfaces, signage, print</td></tr><tr><td>Suhar Mono</td><td>code and terminals, 600-unit cell</td></tr>
<tr><td>Suhar Nerd</td><td>Suhar + Nerd Fonts icons at their own width</td></tr><tr><td>Suhar Nerd Mono</td><td>Suhar Mono + Nerd Fonts icons, one cell each</td></tr></table></section>
</main>
<footer>Suhar is © 2026 The Suhar Project Authors (Sultan Al Isaiee, @foxoman), SIL Open Font License 1.1. Nerd Fonts icons © their authors, see LICENSES. This page loads the WOFF2 files from <code>../dist</code>.</footer>
<script>
const v=document.getElementById('vf'),w=document.getElementById('w'),o=document.getElementById('o');
function u(){{v.style.fontVariationSettings="'wght' "+w.value+", 'opsz' "+o.value}} w.oninput=u;o.oninput=u;u();
</script></body></html>"""
open(os.path.join(ROOT, 'specimen', 'index.html'), 'w', encoding='utf-8').write(page)

# ---------------------------------------------------------------- catalogue PDF
def catalogue(font_path, out, title):
    f = TTFont(font_path)
    gs = f.getGlyphSet()
    rev = {}
    for cp, gn in f.getBestCmap().items():
        rev.setdefault(gn, []).append(cp)
    order = f.getGlyphOrder()
    c = canvas.Canvas(out, pagesize=A4)
    pdfmetrics.registerFont(RLFont('SuharCat', font_path))
    W, H = A4
    c.setTitle(title)
    c.setFont('SuharCat', 54)
    c.drawString(50, H - 130, 'Suhar')
    c.setFont('SuharCat', 16)
    c.drawString(50, H - 165, title)
    c.setFont('SuharCat', 11)
    y = H - 210
    for line in [f'{len(order)} glyphs, {len(f.getBestCmap())} code points. Every cell is the glyph outline taken from the compiled font file',
                 f'({os.path.basename(font_path)}), with its glyph name and code point. Grey lines: baseline, x-height, cap height.',
                 'This text is set in the embedded font itself.', '',
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789',
                 'The quick brown fox jumps over the lazy dog — “Suhar”, Oman.']:
        c.drawString(50, y, line)
        y -= 17
    c.showPage()
    cols, rows = 10, 13
    mx, my = 36, 40
    cw = (W - 2 * mx) / cols
    ch = (H - 2 * my - 20) / rows
    upm = 1000
    sc = (ch - 20) / 1500
    n = 0
    page = 1
    for gn in order:
        col, row = n % cols, n // cols
        if n == 0:
            c.setFont('Helvetica', 7)
            c.drawString(mx, H - my + 8, f'{title} — page {page}')
        x0 = mx + col * cw
        y0 = H - my - 14 - (row + 1) * ch
        c.setStrokeGray(0.82)
        c.setLineWidth(0.3)
        c.rect(x0, y0, cw, ch)
        base = y0 + 16 + 380 * sc
        for lv in (0, 520, 700):
            c.line(x0 + 2, base + lv * sc, x0 + cw - 2, base + lv * sc)
        adv = f['hmtx'][gn][0]
        gx = x0 + (cw - adv * sc) / 2
        pen = CanvasPen(gs, c.beginPath())
        gs[gn].draw(pen)
        c.saveState()
        c.translate(gx, base)
        c.scale(sc, sc)
        c.setFillGray(0)
        c.drawPath(pen.path, stroke=0, fill=1)
        c.restoreState()
        c.setFillGray(0.25)
        c.setFont('Helvetica', 4.6)
        cps = rev.get(gn, [])
        c.drawString(x0 + 2, y0 + 8, gn[:22])
        c.drawString(x0 + 2, y0 + 2.5, ' '.join('U+%04X' % cp for cp in cps[:2]) + ('…' if len(cps) > 2 else ''))
        n += 1
        if n == cols * rows:
            c.showPage()
            n = 0
            page += 1
    c.showPage()
    c.save()
    return page


p1 = catalogue(os.path.join(DIST, 'ttf', 'Suhar-Regular.ttf'), os.path.join(DOCS, 'Suhar-glyph-catalogue.pdf'), 'Suhar Regular — glyph catalogue')
p2 = catalogue(os.path.join(DIST, 'ttf', 'SuharMono-Regular.ttf'), os.path.join(DOCS, 'SuharMono-glyph-catalogue.pdf'), 'Suhar Mono Regular — glyph catalogue')
print('docs written; catalogue pages', p1, p2)
