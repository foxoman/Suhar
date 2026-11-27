"""proof sheets of Suhar Sahafa: python3 tools/sahafa_proof.py FONT.ttf OUT.png [what]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sample_v13 import L, page
F, out = sys.argv[1], sys.argv[2]
what = sys.argv[3] if len(sys.argv) > 3 else 'abc'
if what == 'abc':
    iso = "ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ي ء ة ى"
    rows = [L(F, iso, 56, rtl=True)]
    for grp in ("بببب تتت ججج ححح خخخ سسس ششش صصص ضضض", "ططط ظظظ ععع غغغ ففف ققق ككك للل ممم ننن ههه ييي",
                "صحيفة الأخبار اليومية تصدر كل صباح", "مجلس الوزراء يعتمد الموازنة العامة للدولة", "قطع عظيم كتاب لطيف شغف وهج يحيى فقط",
                "لا إله الله لأن الآن كلا ملك شكل گچپژ"):
        rows.append(L(F, grp, 56, rtl=True))
    rows += [L(F, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 50), L(F, "abcdefghijklmnopqrstuvwxyz 0123456789", 50),
             L(F, "Hamburgefonstiv quickly judged vexing Zephyrs", 50), L(F, "News صحيفة Daily عُمان 2026 fi fl — “quote” (x)", 50)]
page(rows, out)
