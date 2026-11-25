import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proof import Renderer
from layout import paragraph, line
from PIL import Image
D = 'dist/ttf/'
R = Renderer(D + 'Suhar-Regular.ttf'); B = Renderer(D + 'Suhar-Bold.ttf'); I = Renderer(D + 'Suhar-Italic.ttf'); M = Renderer(D + 'SuharNerdMono-Regular.ttf')
W = 1400
parts = [(line(B, "Suhar — صُحار — Сухар — Σουχάρ", 84), 'l'),
         (paragraph(R, "English: Suhar is one of the oldest ports of Oman, the legendary home of Sindbad the Sailor.", 34, W), 'l'),
         (paragraph(R, "العربية: صُحار من أقدم موانئ عُمان، ومنها أبحر السندباد البحري إلى الهند والصين. هنا مهم هذا.", 34, W, rtl=True, leading=1.6), 'r'),
         (paragraph(R, "Русский: Сухар — один из древнейших портов Омана, легендарная родина Синдбада-морехода.", 34, W), 'l'),
         (paragraph(R, "Ελληνικά: Το Σουχάρ είναι ένα από τα αρχαιότερα λιμάνια του Ομάν, πατρίδα του Σεβάχ του Θαλασσινού.", 34, W), 'l'),
         (paragraph(R, "فارسی: صحار یکی از کهن‌ترین بندرهای عمان است.", 32, W, rtl=True, leading=1.6), 'r'),
         (paragraph(R, "اردو: صحار عمان کی قدیم ترین بندرگاہوں میں سے ایک ہے۔   کوردی: سوحار یەکێکە لە کۆنترین بەندەرەکانی عومان.", 32, W, rtl=True, leading=1.6), 'r'),
         (paragraph(R, "Tiếng Việt: Suhar là một trong những cảng cổ nhất của Oman.  Türkçe: Suhar, Umman'ın en eski limanlarından biridir.", 32, W), 'l'),
         (paragraph(R, "עברית: סוחאר היא אחד הנמלים העתיקים של עומאן, מולדתו של סינדבאד המלח.", 32, W, rtl=True, leading=1.5), 'r'),
         (paragraph(R, "Српски: Сухар је једна од најстаријих лука Омана.  Қазақша: Сухар — Оманның ең көне порттарының бірі.  Ἑλληνική: Ἐν ἀρχῇ ἦν ὁ λόγος.", 30, W), 'l'),
         (paragraph(R, "محمدؐ  علیؑ  ﷺ  ﷲ   اردو ہندسے (locl): ۴۵۶۷   AVATAR Τύπος ГАТЬ", 34, W, rtl=True, leading=1.6), 'r'),
         (paragraph(I, "Italic with its own a: a banana and a façade — наклонный — πλάγια", 34, W), 'l')]
a = line(R, "Features:  ", 34)
b = R.line("1/2 3/4 1/3  2026", 34, features={'frac': True, 'zero': True})[0]
c = M.line("   a -> b => c != d <= e >= f == g", 34, features={'dlig': True})[0]
last = Image.new('L', (a.width + b.width + c.width, max(a.height, b.height, c.height)), 0)
last.paste(a, (0, 0)); last.paste(b, (a.width, 0)); last.paste(c, (a.width + b.width, 0))
parts.append((last, 'l'))
H = sum(p.height for p, _ in parts) + 26 * len(parts) + 60
page = Image.new('L', (W + 120, H), 0); y = 30
for p, al in parts:
    page.paste(p, (60 if al == 'l' else W + 60 - p.width, y)); y += p.height + 26
Image.eval(page, lambda v: 255 - v).save(sys.argv[1] if len(sys.argv) > 1 else 'reports/samples/Suhar-languages.png')
