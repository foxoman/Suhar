import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proof import Renderer
from layout import runs
from PIL import Image
D = 'dist/ttf/'
M = Renderer(D + 'SuharNerdMono-Regular.ttf'); MB = Renderer(D + 'SuharNerdMono-Bold.ttf'); MI = Renderer(D + 'SuharNerdMono-Italic.ttf')
px = int(sys.argv[2]) if len(sys.argv) > 2 else 26
C = {'c': (120, 130, 150), 'k': (190, 150, 230), 'f': (130, 170, 255), 's': (160, 220, 150), 't': (110, 200, 190), 'n': (235, 140, 120),
     'w': (225, 228, 235), 'r': (240, 110, 130), 'g': (110, 118, 135)}
L = [
 [(" ☰  File  Edit  View  Go  Run  Git  Nim  AI  Plugins  Help   ", 'w', M), ("work", 'w', MB), ("  master     Search files   Ctrl+P       ", 'g', M)],
 [("  ", 's', M), ("showcase.nim", 'w', MB), (" ✖", 'g', M)],
 [("  87 ", 'g', M), ("# A macro that makes names: `getTitle` and `getSize` exist only after it runs.", 'c', MI)],
 [("  88 ", 'g', M), ("# (in the background), then completion, hover and F12 know them", 'c', MI)],
 [("  89 ", 'g', M), ("macro ", 'k', M), ("makeGetters", 'r', M), ("(T: ", 'w', M), ("typedesc", 't', M), (", fields: ", 'w', M), ("varargs[untyped]", 't', M), ("): ", 'w', M), ("untyped", 't', M), (" =   1 reference", 'g', M)],
 [("  90 ", 'g', M), ("│ ", 'g', M), ("result", 'r', M), (" = ", 'w', M), ("newStmtList", 'f', M), ("()", 'w', M)],
 [("  91 ", 'g', M), ("│ ", 'g', M), ("for ", 'k', M), ("f", 'w', M), (": NimNode ", 'g', M), ("in ", 'k', M), ("fields:", 'w', M)],
 [("  92 ", 'g', M), ("│ │ ", 'g', M), ("let ", 'k', M), ("name", 'w', M), (": NimNode", 'g', M), (" = ", 'w', M), ("ident", 'r', M), ('("get" ', 's', M), ("& ", 'w', M), ("capitalizeAscii", 'f', M), ("($f))", 'w', M)],
 [("  93 ", 'g', M), ("│ │ ", 'g', M), ("result", 'r', M), (".add quote do:", 'f', M)],
 [("  94 ", 'g', M), ("│ │ │ ", 'g', M), ("proc ", 'k', M), ("`name`", 'f', M), ("(x: `T`): ", 'w', M), ("auto", 't', M), (" = x.`f`", 'w', M)],
 [("  96 ", 'w', MB), ("makeGetters", 'r', M), ("(Config, title, size)", 'w', M)],
 [("     ↳ the macro makeGetters writes  · Alt+M hides it · a name: hover, click goes to it", 'g', M)],
 [("  98 ", 'g', M), ("# ── 3. Routines: type hints, parameter names ────────────────────", 'c', MI)],
 [(" 102 ", 'g', M), ("func ", 'k', M), ("area", 'f', M), ("(c: ", 'w', M), ("Circle", 't', M), ("): ", 'w', M), ("float", 't', M), (" = ", 'w', M), ("PI", 'n', M), (" * c.r * c.r   0O 1lI| {}[]() <= >= != -> => 0xFF_00", 'w', M), ("  ⣿⣶⣤⡀ ⣿⣿⠇", 'g', M)],
 [(" 103 ", 'g', M), ('let greeting = "', 'w', M), ("مرحباً بكم في صحار", 's', M), ('"   ', 'w', M), ("# نص عربي داخل الشيفرة", 'c', M)],
 [(" 104 ", 'g', M), ('echo "', 'w', M), ("السلام عليكم", 's', M), ('", " — Sohar, Oman"', 'w', M)],
 [("  1   5   Nim 2.2.12  C · ned   Terminal            Ln 96, Col 3   Spaces: 2   UTF-8   LF   Nim ", 'g', M)],
]
M.ft.set_pixel_sizes(0, px)
lh = round(M.ft.size.height / 64)
W = int(px * 0.6 * 96)
img = Image.new('RGB', (W, lh * len(L) + 40), (30, 34, 46))
for i, row in enumerate(L):
    x = 14.0
    for t, c, r in row:
        for seg, cl in runs(t, False):
            m, adv = r.line(seg, px, direction='rtl' if cl == 'R' else 'ltr')
            m = m.crop((2, 2, m.width, m.height))
            img.paste(Image.new('RGB', m.size, C[c]), (int(round(x)), 20 + i * lh), m)
            x += adv
img.save(sys.argv[1] if len(sys.argv) > 1 else 'proofs/Suhar-mono-editor.png')
