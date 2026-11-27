"""docs/Suhar-specimen.pdf: a four-page specimen for printers and publishers (needs Chrome or Chromium)."""
import os, re, shutil, subprocess, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'dist', 'ttf')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'docs', 'Suhar-specimen.pdf')
VER = '.'.join(re.findall(r'VERSION = \((\d+), (\d+)\)', open(os.path.join(ROOT, 'src', 'retrofont', 'ufo.py')).read())[0])
FAMS = [('Suhar', 'Suhar', 'interfaces, text, signage', 14), ('Suhar Condensed', 'SuharCondensed', 'signs and tight headlines', 12),
        ('Suhar Naskh', 'SuharNaskh', 'books and long Arabic text', 8), ('Suhar Naskh Caption', 'SuharNaskhCaption', 'Naskh for 6 to 8 point', 8),
        ('Suhar Naskh Display', 'SuharNaskhDisplay', 'titles that slope as in handwriting', 4),
        ('Suhar Sahafa', 'SuharSahafa', 'newspaper text', 8), ('Suhar Sahafa Headline', 'SuharSahafaHeadline', 'newspaper headlines', 8),
        ('Suhar Sahafa Caption', 'SuharSahafaCaption', 'newspaper text at 6 to 8 point', 8), ('Suhar Typewriter', 'SuharTypewriter', 'typed letters and forms', 4),
        ('Suhar Mono', 'SuharMono', 'code and terminals', 12)]
css = []
for fam, ps, _, _ in FAMS:
    for sn, w, it in (('Light', 300, 'normal'), ('Regular', 400, 'normal'), ('Medium', 500, 'normal'), ('SemiBold', 600, 'normal'), ('Bold', 700, 'normal'),
                      ('ExtraBold', 800, 'normal'), ('Black', 900, 'normal'), ('Italic', 400, 'italic'), ('BoldItalic', 700, 'italic')):
        p = os.path.join(D, f'{ps}-{sn}.ttf')
        if os.path.exists(p):
            css.append(f"@font-face{{font-family:'{fam}';src:url('file://{p}');font-weight:{w};font-style:{it}}}")
e = html.escape
AR = ("تقع صُحار على ساحل بحر عُمان، على بعد 240 كم من مسقط. كانت قديماً من أهم موانئ المنطقة، ومنها أبحر التجار إلى الهند والصين "
      "وشرق أفريقيا، وارتبط اسمها بحكايات السندباد البحري.")
EN = ("Suhar lies on the Sea of Oman, 240 km from Muscat. It was once among the busiest ports of the region; its merchants sailed to "
      "India, China and East Africa, and the Sindbad stories are tied to its name.")
rows = ''.join(f"<div class='fam'><div class='lab'>{e(f)} · {n} styles · {e(u)}</div><div style=\"font-family:'{f}';font-size:{15 if 'Mono' in f else 19}pt\" dir='rtl'>"
               f"صُحار مدينة عُمانية عريقة · Sohar, an old Omani port · 0123456789</div></div>" for f, _, u, n in FAMS)
wts = ''.join(f"<div style=\"font-family:'Suhar';font-weight:{w};font-size:22pt\">{n} — صحار Suhar</div>"
              for w, n in ((300, 'Light'), (400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'), (700, 'Bold'), (800, 'ExtraBold'), (900, 'Black')))
text = ''.join(f"<h2>{f}, {pt} pt</h2><div class='two' style=\"font-family:'{f}';font-size:{pt}pt\"><p dir='rtl' lang='ar'>{e(AR)}</p><p>{e(EN)}</p></div>"
               for f, pt in (('Suhar', 10), ('Suhar Naskh', 11), ('Suhar Sahafa', 9), ('Suhar Sahafa Caption', 7), ('Suhar Typewriter', 10)))
feat = (f"<h2>Arabic</h2><p dir='rtl' style=\"font-family:'Suhar Naskh';font-size:20pt\">بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ · في على إلى · بر تبرير بين نبي · لا لأ لإ لآ</p>"
        f"<p dir='rtl' style=\"font-family:'Suhar';font-size:15pt\">فارسی: گچپژ ک ی · اردو: ٹ ڈ ڑ ں ے ہ · کوردی: ڕ ڵ ۆ ێ · پښتو: ټ ډ ړ ږ ښ ڼ · سنڌي: ٻ ڀ ٺ ڄ ڃ</p>"
        f"<h2>Latin, Greek, Cyrillic, Hebrew</h2><p style=\"font-family:'Suhar';font-size:14pt\">Ærøskøbing façade naïve Łódź Việt Nam · Ελληνικά · Русский · Українська · <span dir='rtl'>עברית</span></p>"
        f"<h2>Figures and signs</h2><p style=\"font-family:'Suhar';font-size:16pt\">0123456789 · <span style=\"font-feature-settings:'onum'\">0123456789</span> · ٠١٢٣٤٥٦٧٨٩ · "
        f"<span style=\"font-feature-settings:'frac'\">1/2 3/4</span> · € £ ¥ &#x20C4; &#x20C1; &#x20C3; · ← ↑ → ↓ ✓ ★</p>"
        f"<h2>Sahafa</h2><p dir='rtl' style=\"font-family:'Suhar Sahafa Headline';font-weight:700;font-size:30pt;margin:0\">ميناء صحار يسجل رقما قياسيا</p>"
        f"<p style=\"font-family:'Suhar Sahafa';font-size:11pt\">The Daily News — <i>Sohar Port handled 240 ships</i>, an official said. <b>Bold for emphasis.</b></p>"
        f"<h2>Mono</h2><pre style=\"font-family:'Suhar Mono';font-size:10pt\">proc greet(name: string): string =\n  result = \"مرحباً يا \" &amp; name &amp; \"!\"   # != =&gt; := |&gt; 0O 1lI</pre>")
pages = [f"<div class='cover'><div class='w'>Suhar</div><div class='a' dir='rtl'>صُحار، مدينة السندباد</div><p>A typeface family for Arabic and Latin, from Oman.<br>"
         f"Version {VER} · Sultan Al Isaiee · www.foxoman.net · SIL Open Font License 1.1</p></div>",
         "<h1>The families</h1>" + rows, "<h1>Weights</h1>" + wts + "<h1 style='margin-top:8mm'>Text</h1>" + text, "<h1>Scripts and features</h1>" + feat]
doc = ("<!doctype html><html><head><meta charset='utf-8'><style>" + '\n'.join(css) +
       "@page{size:A4;margin:16mm}body{margin:0;font-family:'Suhar';color:#111}section{page-break-after:always}h1{font-size:12pt;letter-spacing:.06em;text-transform:uppercase;"
       "color:#0b6e75;border-bottom:.5pt solid #999;padding-bottom:2mm;margin:0 0 5mm}h2{font-size:8pt;font-weight:400;color:#666;margin:4mm 0 1mm}"
       ".cover{height:250mm;display:flex;flex-direction:column;justify-content:center}.w{font:900 120pt/1 'Suhar'}.a{font:700 46pt/1.4 'Suhar Naskh Display';color:#0b6e75}"
       ".cover p{font-size:11pt;color:#444;margin-top:10mm}.fam{margin:0 0 5.2mm}.lab{font-size:7.5pt;color:#666;letter-spacing:.03em}"
       ".two{display:grid;grid-template-columns:1fr 1fr;gap:8mm;line-height:1.5}.two p{margin:0;text-align:justify}p{margin:0 0 2mm}</style></head><body>" +
       ''.join(f"<section>{p}</section>" for p in pages) + "</body></html>")
tmp = os.path.join(ROOT, 'build', 'specimen-print.html')
os.makedirs(os.path.dirname(tmp), exist_ok=True)
open(tmp, 'w', encoding='utf-8').write(doc)
chrome = next((c for c in ('google-chrome', 'chromium', 'chromium-browser', 'chrome') if shutil.which(c)), None)
if not chrome:
    sys.exit('Chrome or Chromium is needed; the HTML is at ' + tmp)
subprocess.run([chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer', '--allow-file-access-from-files',
                f'--print-to-pdf={OUT}', 'file://' + tmp], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
print(OUT, os.path.getsize(OUT) // 1024, 'KB')
