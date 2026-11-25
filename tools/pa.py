import sys; sys.path.insert(0,'tools')
from proof import Renderer, sheet
R=Renderer('build/quick/R.ttf'); B=Renderer('build/quick/B.ttf')
T=["ء آ أ ؤ إ ئ ا ب ة ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ",
"ف ق ك ل م ن ه و ى ي  پ چ ژ ک گ ی ٹ ڈ ڑ ں ھ ہ ۃ ے ۓ",
"ببب تتت ثثث ججج ححح خخخ سسس ششش صصص ضضض ططط ظظظ ععع غغغ",
"ففف ققق ككك للل ممم ننن ههه ييي ککک گگگ ہہہ ھھھ ئئئ پپپ چچچ",
"لا لأ لإ لآ بلا  السلام عليكم ورحمة الله وبركاته  مرحبا بالعالم",
"٠١٢٣٤٥٦٧٨٩ ۰۱۲۳۴۵۶۷۸۹ ، ؛ ؟ ٪ ٫ ٬ ٭ ۔ ـــ"]
sz=int(sys.argv[1]) if len(sys.argv)>1 else 60
sheet([(R,t,sz) for t in T],'proofs/a1.png')
sheet([(B,t,sz) for t in T],'proofs/a2.png')
