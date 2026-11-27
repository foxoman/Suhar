# Suhar App fonts

Made by `tools/make_app_fonts.py` from the release fonts: no hinting, only the layout features an interface needs, and without box drawing, braille, Powerline and terminal symbols. The letter shapes, spacing and kerning are those of the release fonts.

| file | contents | characters | glyphs | size (KB) | release font (KB) |
|---|---|---:|---:|---:|---:|
| SuharApp-Regular.ttf | Suhar, every language | 1929 | 1959 | 255 | 511 |
| SuharApp-Bold.ttf | Suhar, every language | 1929 | 1959 | 261 | 535 |
| SuharApp-Italic.ttf | Suhar, every language | 1929 | 1959 | 262 | 516 |
| SuharApp-BoldItalic.ttf | Suhar, every language | 1929 | 1959 | 266 | 539 |
| SuharAppLite-Regular.ttf | Suhar, Arabic and Western European Latin | 644 | 632 | 80 | 511 |
| SuharAppLite-Bold.ttf | Suhar, Arabic and Western European Latin | 644 | 632 | 80 | 535 |
| SuharAppLite-Italic.ttf | Suhar, Arabic and Western European Latin | 644 | 632 | 82 | 516 |
| SuharAppLite-BoldItalic.ttf | Suhar, Arabic and Western European Latin | 644 | 632 | 83 | 539 |
| SuharAppRead-Regular.ttf | Suhar Sahafa, every language | 1929 | 2029 | 270 | 541 |
| SuharAppRead-Bold.ttf | Suhar Sahafa, every language | 1929 | 2029 | 285 | 558 |
| SuharAppRead-Italic.ttf | Suhar Sahafa, every language | 1929 | 2029 | 273 | 549 |
| SuharAppRead-BoldItalic.ttf | Suhar Sahafa, every language | 1929 | 2029 | 280 | 551 |

## Room above and below the line

The line box of the fonts is 940 above and -360 below the baseline (1000 units per em). Ink reaches these heights, in the Regular and Bold of each family:

| file | plain text: top | bottom | fully vowelled text: top | bottom |
|---|---:|---:|---:|---:|
| SuharApp-Regular.ttf | 939 | -281 | 1260 | -548 |
| SuharApp-Bold.ttf | 955 | -363 | 1277 | -638 |
| SuharAppLite-Regular.ttf | 939 | -281 | 1260 | -548 |
| SuharAppLite-Bold.ttf | 955 | -363 | 1277 | -638 |
| SuharAppRead-Regular.ttf | 936 | -363 | 1265 | -607 |
| SuharAppRead-Bold.ttf | 949 | -430 | 1281 | -709 |

Plain text is the Arabic alphabet with its hamza forms and lam-alef, and accented Latin capitals. Fully vowelled text has shadda with a vowel on tall letters and tanween under deep ones; it needs about a third of an em more room above and a quarter more below than the line box gives.
