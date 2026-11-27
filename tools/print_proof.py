"""Print proof: one PDF with every family from 6 to 72 point, newspaper columns, optical sizes, grades, reversed text and
ink traps.  The fonts are embedded as they are; print it at 100 % ("actual size") on the printer and paper you care about.
    python3 tools/print_proof.py [OUT.pdf]        needs Chrome or Chromium for the PDF step"""
import os, shutil, subprocess, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'dist')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'docs', 'Suhar-print-proof.pdf')
VER = '.'.join(str(x) for x in __import__('re').findall(r'VERSION = \((\d+), (\d+)\)', open(os.path.join(ROOT, 'src', 'retrofont', 'ufo.py')).read())[0])

FAMS = [('Suhar', 'Suhar'), ('Suhar Condensed', 'SuharCondensed'), ('Suhar Naskh', 'SuharNaskh'), ('Suhar Naskh Display', 'SuharNaskhDisplay'),
        ('Suhar Naskh Caption', 'SuharNaskhCaption'), ('Suhar Sahafa', 'SuharSahafa'), ('Suhar Sahafa Headline', 'SuharSahafaHeadline'), ('Suhar Sahafa Caption', 'SuharSahafaCaption'),
        ('Suhar Typewriter', 'SuharTypewriter'),
        ('Suhar Mono', 'SuharMono')]
css = []
for fam, ps in FAMS:
    for sn, w, it in (('Regular', 400, 'normal'), ('Bold', 700, 'normal'), ('Italic', 400, 'italic')):
        p = os.path.join(D, 'ttf', f'{ps}-{sn}.ttf')
        if os.path.exists(p):
            css.append(f"@font-face{{font-family:'{fam}';src:url('file://{p}');font-weight:{w};font-style:{it}}}")
for name, f in (('Sahafa VF', 'SuharSahafa[GRAD,opsz,wght].ttf'), ('Naskh VF', 'SuharNaskh[GRAD,opsz,wght].ttf'), ('Suhar VF', 'Suhar[opsz,wght].ttf')):
    css.append(f"@font-face{{font-family:'{name}';src:url('file://{os.path.join(D, 'variable', f)}');font-weight:400 700}}")

AR = ("أعلنت وزارة الاقتصاد أن الناتج المحلي الإجمالي حقق نموا ملحوظا خلال الربع الثالث من العام، مدفوعا بارتفاع الصادرات غير النفطية "
      "وتوسع قطاعي الصناعة والخدمات اللوجستية. وقال مسؤول في الوزارة إن ميناء صحار استقبل 240 سفينة في شهر واحد، وإن الحكومة تمضي "
      "في تنفيذ خطتها لتنويع مصادر الدخل وتشجيع الاستثمار في الطاقة المتجددة. وأضاف أن المنطقة الحرة جذبت استثمارات جديدة في الصناعات "
      "المعدنية والبتروكيماوية، وأن عدد العاملين فيها تجاوز خمسة عشر ألفا.")
EN = ("The ministry said output grew strongly in the third quarter, helped by non-oil exports and by industry and logistics. Sohar Port "
      "handled 240 ships in a single month, an official said, and the government is pressing on with its plan to diversify income and "
      "encourage investment in renewable energy. The free zone drew new investment in metals and petrochemicals.")
MIX = "صُحار مدينة عُمانية · Sohar Port and Freezone · 240 km · 0123456789"
TASH = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ — قُلْ هُوَ اللَّهُ أَحَدٌ"
e = html.escape
P = []


def page(title, body, note=''):
    P.append(f"<section><h1>{e(title)}</h1>{body}<p class='note'>{e(note)}</p><footer>Suhar {VER} print proof · print at 100 % · "
             f"page {len(P) + 1}</footer></section>")


def ladder(fam, mono=False):
    rows = ''.join(f"<div class='row'><span class='pt'>{pt} pt</span><span style=\"font-family:'{fam}';font-size:{pt}pt\" dir='rtl'>{e(MIX)}</span></div>"
                   for pt in (6, 7, 8, 9, 10, 12, 14, 18, 24, 36))
    rows += f"<div class='row'><span class='pt'>48 pt</span><span style=\"font-family:'{fam}';font-size:48pt;font-weight:700\" dir='rtl'>صُحار Sohar</span></div>"
    rows += f"<div class='row'><span class='pt'>10 pt</span><span style=\"font-family:'{fam}';font-size:10pt\" dir='rtl'>{e(TASH)}</span></div>"
    return rows


for fam, ps in FAMS:
    page(fam + ' — 6 to 48 point', ladder(fam), 'Look for: thin strokes that break, loops that fill in, dots that touch the letter, uneven darkness between Arabic and Latin.')

cols = ''
for fam, pt in (('Suhar Sahafa Caption', 6.5), ('Suhar Sahafa', 8), ('Suhar Sahafa', 9), ('Suhar Naskh', 9), ('Suhar', 9)):
    cols += (f"<h2>{fam}, {pt} pt</h2><div class='cols' style=\"font-family:'{fam}';font-size:{pt}pt\"><p dir='rtl' lang='ar'>{e(AR)}</p>"
             f"<p>{e(EN)}</p></div>")
page('Newspaper columns, justified', f"<p dir='rtl' style=\"font-family:'Suhar Sahafa Headline';font-weight:700;font-size:34pt;margin:0\">ميناء صحار يسجل رقما قياسيا</p>"
     f"<p style=\"font-family:'Suhar Sahafa Headline';font-size:20pt;margin:0 0 3mm\">Sohar Port sets a new record</p>" + cols,
     'Look for: which size is the smallest you read without effort; rivers of white between words; hyphen-less lines that look loose.')

ops = ''
for lab, v in (('opsz 8 (caption)', 8), ('opsz 14 (text)', 14), ('opsz 72 (display)', 72)):
    ops += (f"<h2>{lab}, set at 7 pt</h2><p dir='rtl' style=\"font-family:'Sahafa VF';font-size:7pt;font-variation-settings:'opsz' {v};font-optical-sizing:none\">{e(AR[:300])}</p>")
for lab, v in (('opsz 14', 14), ('opsz 72', 72)):
    ops += f"<h2>{lab}, set at 54 pt</h2><p dir='rtl' style=\"font-family:'Sahafa VF';font-size:54pt;font-weight:700;margin:0;font-variation-settings:'opsz' {v};font-optical-sizing:none\">صحيفة عُمان</p>"
page('Optical sizes (Suhar Sahafa variable)', ops, 'Expected: at 7 pt the caption cut is the easiest to read; at 54 pt the display cut is the finest.')

gr = ''
for lab, v in (('GRAD −50, for paper that spreads ink (newsprint)', -50), ('GRAD 0', 0), ('GRAD +50, for coated paper and laser toner', 50)):
    gr += f"<h2>{lab}</h2><p dir='rtl' class='j' style=\"font-family:'Sahafa VF';font-size:9pt;font-variation-settings:'GRAD' {v}\">{e(AR)}</p>"
page('Grades (Suhar Sahafa variable)', gr, 'Expected: the three paragraphs break their lines at the same words; only the darkness changes. Pick the one that looks right on your paper.')

rev = ''.join(f"<div class='rev' style=\"font-family:'{fam}';font-size:{pt}pt\" dir='rtl'>{pt} pt · {fam} · {e(MIX)}</div>"
              for fam in ('Suhar', 'Suhar Naskh', 'Suhar Sahafa', 'Suhar Sahafa Caption') for pt in (6, 7, 8, 10))
rev += ''.join(f"<div style=\"font-family:'{fam}';font-size:8pt;color:#888\" dir='rtl'>50 % grey · {fam} · {e(MIX)}</div>" for fam in ('Suhar', 'Suhar Naskh', 'Suhar Sahafa'))
page('Reversed and grey text', rev, 'Look for: white letters whose thin strokes close up in the black; grey letters that break into dots.')

trap = (f"<p dir='rtl' style=\"font-family:'Suhar Sahafa';font-size:150pt;margin:0;line-height:1.15\">بسط صحف</p>"
        f"<p dir='rtl' style=\"font-family:'Suhar Sahafa';font-weight:700;font-size:150pt;margin:0;line-height:1.15\">كتب عيد</p>"
        f"<p dir='rtl' style=\"font-family:'Suhar Sahafa';font-size:8pt\">{e(AR)}</p>")
page('Ink traps (Suhar Sahafa)', trap, 'At 150 pt the notches at the inner corners are visible. At 8 pt they should not be: the corners should simply look clean, not rounded.')

nb = ''
for lab, fs in (('default', "normal"), ('neighbour forms off', "'calt' 0"), ('justification alternates', "'jalt' 1"), ('returning yeh, letters on jeem, ligatures', "'ss06' 1, 'ss07' 1, 'dlig' 1")):
    nb += f"<h2>{lab}</h2><p dir='rtl' style=\"font-family:'Suhar Sahafa';font-size:22pt;margin:0;font-feature-settings:{fs}\">بر تبرير نزل بين تين نبي · كتب في ملك شريف · نجم بحر على لم</p>"
nb += f"<h2>justified with a long word space and with tatweel</h2><p dir='rtl' class='j' style=\"font-family:'Suhar Sahafa';font-size:12pt;width:70mm\">{e(AR[:260])}</p>"
nb += f"<p dir='rtl' style=\"font-family:'Suhar Sahafa';font-size:16pt\">كتـب · كتــب · كتـــب · صحيـفة · صحيــفة · الـعـربـيـة</p>"
page('Neighbour forms and justification', nb, 'Look for: joins that break where a tatweel is inserted; neighbour forms that look wrong to an Arabic reader.')

chk = ("<ol style='font-size:11pt;line-height:1.9'><li>Printer and paper: ____________________  resolution: ______ dpi</li>"
       "<li>Smallest size you read without effort — Suhar: ___  Naskh: ___  Sahafa: ___  Sahafa Caption: ___</li>"
       "<li>Letters whose loops fill in (write the letter and the size): ____________________</li>"
       "<li>Thin strokes that break (family and size): ____________________</li>"
       "<li>Dots or marks that touch the letter (family and size): ____________________</li>"
       "<li>Arabic darker or lighter than Latin on the same line? (family): ____________________</li>"
       "<li>Best grade on this paper: −50 / 0 / +50</li><li>Best cut at 7 pt: opsz 8 / 14 / 72</li>"
       "<li>Word spaces that look too wide or too tight (page and line): ____________________</li>"
       "<li>Any shape that looks wrong: ____________________</li></ol>")
page('What to report', chk, 'Send these answers back, or a phone photo of each page taken straight on in good light.')

doc = ("<!doctype html><html><head><meta charset='utf-8'><style>" + '\n'.join(css) +
       "@page{size:A4;margin:14mm 14mm 16mm}body{margin:0;font-family:'Suhar';color:#000}section{page-break-after:always;position:relative;min-height:262mm}"
       "h1{font-size:13pt;margin:0 0 4mm;border-bottom:.4pt solid #000;padding-bottom:1.5mm}h2{font-size:8pt;font-weight:400;color:#555;margin:3mm 0 1mm}"
       ".row{display:flex;align-items:baseline;gap:4mm;margin:1.2mm 0;white-space:nowrap;overflow:hidden}.pt{font-size:7pt;color:#555;width:11mm;flex:none}"
       ".cols{column-count:3;column-gap:5mm;text-align:justify;line-height:1.38}.cols p{margin:0 0 1.5mm}.j{text-align:justify;line-height:1.45}"
       ".rev{background:#000;color:#fff;padding:1mm 2mm;margin:0;white-space:nowrap;overflow:hidden}.note{font-size:8pt;color:#333;margin-top:4mm;border-top:.4pt solid #999;padding-top:1.5mm}"
       "footer{position:absolute;bottom:-6mm;left:0;font-size:6.5pt;color:#666}p{margin:0 0 2mm}</style></head><body>" + ''.join(P) + "</body></html>")
tmp = os.path.join(ROOT, 'build', 'print-proof.html')
os.makedirs(os.path.dirname(tmp), exist_ok=True)
open(tmp, 'w', encoding='utf-8').write(doc)
chrome = next((c for c in ('google-chrome', 'chromium', 'chromium-browser', 'chrome') if shutil.which(c)), None)
if not chrome:
    sys.exit('Chrome or Chromium is needed to write the PDF; the HTML is at ' + tmp)
subprocess.run([chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer', '--allow-file-access-from-files',
                f'--print-to-pdf={OUT}', 'file://' + tmp], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
print(OUT, os.path.getsize(OUT) // 1024, 'KB', len(P), 'pages')
