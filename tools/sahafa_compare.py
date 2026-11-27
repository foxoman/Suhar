"""Suhar Sahafa next to reference Naskh faces: the same paragraph, the same size, the same column.
    python3 tools/sahafa_compare.py OUT.png PX WIDTH NAME=FONT.ttf ..."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proof import Renderer
from layout import paragraph, line
from PIL import Image
TXT = ("أعلنت وزارة الاقتصاد أن الناتج المحلي الإجمالي حقق نموا ملحوظا خلال الربع الثالث من العام، مدفوعا بارتفاع "
       "الصادرات غير النفطية وتوسع قطاعي الصناعة والخدمات اللوجستية. وقال مسؤول في الوزارة إن ميناء صحار استقبل عددا "
       "قياسيا من السفن، وإن الحكومة تمضي في تنفيذ خطتها لتنويع مصادر الدخل وتشجيع الاستثمار في الطاقة المتجددة.")
out, px, width = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
lab = Renderer(os.path.join(os.path.dirname(__file__), '..', 'dist', 'ttf', 'Suhar-Regular.ttf'))
rows = []
for a in sys.argv[4:]:
    name, path = a.split('=')
    r = Renderer(path)
    p = paragraph(r, TXT, px, width, rtl=True, leading=1.5)
    rows += [line(lab, f"{name}  ({p.height // max(1, round(px * 1.5))} lines)", 20), p]
W = max(r.width for r in rows) + 40
H = sum(r.height + 12 for r in rows) + 40
pg = Image.new('L', (W, H), 0)
y = 20
for r in rows:
    pg.paste(r, (W - 20 - r.width if r.width > 400 else 20, y))
    y += r.height + 12
Image.eval(pg, lambda v: 255 - v).save(out)
