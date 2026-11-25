import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proof import Renderer
from layout import paragraph, line
from PIL import Image
D = 'dist/ttf/'
R = Renderer(D + 'Suhar-Regular.ttf'); B = Renderer(D + 'Suhar-Bold.ttf'); I = Renderer(D + 'Suhar-Italic.ttf'); BI = Renderer(D + 'Suhar-BoldItalic.ttf')
W = 1400
EN = ("Suhar (صُحار) is one of the oldest ports of Oman. For centuries its harbour linked Arabia with India, East Africa and China, "
      "and sailors told the tales of Sindbad the Sailor (السندباد البحري) about voyages that began here. Today the city is known for "
      "Sohar Fort (قلعة صحار), the corniche, the Friday souq and a modern port — ميناء صحار — that handles more than 60 million tonnes "
      "of cargo a year. Visitors are greeted with the words “أهلاً وسهلاً” (welcome), coffee and dates.")
AR = ("صُحار مدينة عُمانية عريقة على ساحل بحر عُمان، وتُعرف بالإنجليزية باسم Sohar أو Suhar. كانت قديماً من أهم موانئ "
      "المنطقة، ومنها أبحر التجار إلى الهند والصين وشرق أفريقيا، وارتبط اسمها بحكايات السندباد البحري (Sindbad the Sailor). "
      "تضم المدينة اليوم قلعة صحار وميناءً حديثاً ومنطقة صناعية تبعد نحو 240 كم عن مسقط، ويقصدها الزوار للتعرف على "
      "تاريخها وأسواقها وكرم أهلها. وتُكتب اللافتات فيها باللغتين: العربية و English جنباً إلى جنب.")
IT_EN = "Italic: The harbour of Suhar — ميناء صحار — was praised by early geographers as “the gateway to China”."
IT_AR = "مائل: وصف الجغرافيون ميناء صحار بأنه «بوابة الصين» — the gateway to China — ومخزن الشرق."
parts = [(line(B, "Suhar — صُحار", 110), 'l'),
         (paragraph(R, EN, 36, W), 'l'), (paragraph(R, AR, 36, W, rtl=True, leading=1.6), 'r'),
         (paragraph(I, IT_EN, 36, W), 'l'), (paragraph(I, IT_AR, 36, W, rtl=True, leading=1.6), 'r'),
         (paragraph(BI, "Bold Italic: Welcome to Suhar — مرحباً بكم في صحار", 40, W), 'l'),
         (paragraph(R, EN, 20, 900), 'l'), (paragraph(R, AR, 20, 900, rtl=True, leading=1.6), 'r'),
         (paragraph(R, EN, 13, 640), 'l'), (paragraph(R, AR, 13, 640, rtl=True, leading=1.6), 'r')]
H = sum(p.height for p, _ in parts) + 36 * len(parts) + 80
page = Image.new('L', (W + 120, H), 0); y = 40
for p, al in parts:
    x = 60 if al == 'l' else W + 60 - p.width
    page.paste(p, (x, y)); y += p.height + 36
out = sys.argv[1] if len(sys.argv) > 1 else 'proofs/Suhar-mixed-paragraphs.png'
Image.eval(page, lambda v: 255 - v).save(out)
