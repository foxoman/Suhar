"""Images for the README, rendered from the built fonts in dist/ttf with HarfBuzz and FreeType."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proof import Renderer
from layout import line, paragraph
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'dist', 'ttf')
OUT = os.path.join(ROOT, 'docs', 'images')
BG, INK, MUTE, ACC = (247, 244, 236), (24, 26, 29), (98, 104, 112), (11, 110, 117)


def F(name):
    return Renderer(os.path.join(D, name + '.ttf'))


def sheet(rows, path, width=1600, pad=56, gap=22, bg=BG):
    h = pad * 2 + sum(im.height for im, _, _ in rows) + gap * (len(rows) - 1)
    pg = Image.new('RGB', (width, h), bg)
    y = pad
    for im, col, right in rows:
        x = width - pad - im.width if right else pad
        pg.paste(Image.new('RGB', im.size, col), (x, y), im)
        y += im.height + gap
    pg.save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    R, B, L, K = F('Suhar-Regular'), F('Suhar-Bold'), F('Suhar-Light'), F('Suhar-Black')
    N, NB, ND = F('SuharNaskh-Regular'), F('SuharNaskh-Bold'), F('SuharNaskhDisplay-Bold')
    M, MB = F('SuharMono-Regular'), F('SuharMono-Bold')
    sheet([(line(K, "Suhar", 150), INK, False), (line(ND, "صُحار، مدينة السندباد", 120, rtl=True), ACC, True),
           (line(R, "A typeface family for Arabic and Latin, from Oman", 44), MUTE, False),
           (line(L, "Light", 40), INK, False), (line(R, "Regular  Medium  SemiBold", 40), INK, False), (line(B, "Bold  ExtraBold", 40), INK, False),
           (line(R, "ميناء صحار والمنطقة الحرة · Sohar Port and Freezone · 240 km · ⃄ 1.500", 40, rtl=True), INK, True)],
          os.path.join(OUT, 'hero.png'))
    ar = ("تقع صُحار (Sohar) على ساحل بحر عُمان، على بعد 240 كم من مسقط. كانت قديماً من أهم موانئ المنطقة، "
          "ومنها أبحر التجار إلى الهند والصين وشرق أفريقيا، وارتبط اسمها بحكايات السندباد البحري.")
    en = ("Suhar lies on the Sea of Oman, 240 km from Muscat. It was once among the busiest ports of the region; "
          "its merchants sailed to India, China and East Africa, and the Sindbad stories are tied to its name.")
    sheet([(paragraph(R, ar, 34, 1480, rtl=True, leading=1.7), INK, True), (paragraph(R, en, 34, 1480, leading=1.5), INK, False),
           (paragraph(B, "صُحار Suhar: نفس الوزن ونفس الارتفاع في السطر الواحد — one weight and one height on the same line.", 34, 1480, rtl=True, leading=1.7), ACC, True)],
          os.path.join(OUT, 'paragraph.png'))
    sheet([(line(ND, "أصل الكتابة العربية", 130, rtl=True), INK, True), (line(N, "في على إلى · نجم بحر تحت · صُحار مدينة عُمانية عريقة", 60, rtl=True), ACC, True),
           (paragraph(N, ar, 32, 1480, rtl=True, leading=1.75), INK, True), (line(NB, "Suhar Naskh — the same Latin beside a pen-written Arabic", 36), MUTE, False)],
          os.path.join(OUT, 'naskh.png'))
    S, SB, SH, SHB = F('SuharSahafa-Regular'), F('SuharSahafa-Bold'), F('SuharSahafaHeadline-Regular'), F('SuharSahafaHeadline-Bold')
    news = ("أعلنت وزارة الاقتصاد أن الناتج المحلي الإجمالي حقق نموا ملحوظا خلال الربع الثالث من العام، مدفوعا بارتفاع الصادرات غير النفطية "
            "وتوسع قطاعي الصناعة والخدمات اللوجستية. وقال مسؤول في الوزارة إن ميناء صحار (Sohar Port) استقبل 240 سفينة في شهر واحد.")
    newse = ("The ministry said output grew strongly in the third quarter, helped by non-oil exports and by industry and logistics. "
             "Sohar Port handled 240 ships in a single month, an official said.")
    sheet([(line(SHB, "ميناء صحار يسجل رقما قياسيا", 118, rtl=True), INK, True), (line(SH, "Sohar Port sets a new record", 70), ACC, False),
           (paragraph(S, news, 30, 1480, rtl=True, leading=1.6), INK, True), (paragraph(S, newse, 30, 1480, leading=1.45), INK, False),
           (line(SB, "Suhar Sahafa Text Bold — صحيفة عُمان اليومية", 40), INK, False),
           (line(S, "8 pt at 150 dpi: " + news[:96], 17, rtl=True), MUTE, True)],
          os.path.join(OUT, 'sahafa.png'))
    code = ['proc greet(name: string): string =', '  ## تحية بالعربية', '  result = "مرحباً يا " & name & "!"', '',
            'echo greet("صُحار")', '# != => := |> 0O 1lI {} [] ()', '┌─ Suhar Mono ─────────┐  ░▒▓█ ▁▂▃▄▅▆▇']
    rows = [(line(M, c if c else ' ', 34), (226, 232, 240) if i not in (1,) else (120, 200, 170), False) for i, c in enumerate(code)]
    sheet(rows, os.path.join(OUT, 'mono.png'), width=1200, gap=0, bg=(22, 26, 32))


if __name__ == '__main__':
    main()
