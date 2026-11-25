# Design notes

## Idea

Suhar is a port: goods and languages meet there. The family is built so that Arabic and Latin
sit in one line at the same size, weight and rhythm, on a road sign, in a magazine column, or in an
8-pixel menu.

## One engine, two pens

Glyphs are not drawn as outlines. Each is a *skeleton* (centre lines) written in a small text
language (`src/retrofont/engine.py`) and expanded by a pen:

- **Latin pen**: an upright ellipse, 88 units wide and 76 high in Regular (150 x 122 in Bold). Verticals
  are a little heavier than horizontals, as in classic grotesques.
- **Arabic pen**: an ellipse rotated 65°, like a reed pen. Horizontals carry the weight, uprights are
  lighter and end in a natural slanted cut. Dots are the rhombus a pen nib makes.

Weight, width, slant, optical size and the Mono fitting are parameters of the expansion, so all 16
styles and the variable masters come from the same drawings and stay point-compatible.

## Latin details

- Curves use a rounded-corner construction with tension 0.70: bowls are soft squares, which keeps
  counters open at small sizes and echoes screen fonts of the 1990s.
- Apertures of a c e s C G S 2 3 5 6 9 are open and cut perpendicular to the stroke.
- Stems of b d h k l i j m n p r u t are cut at 14° on top.
- `l` has a tail, `y` a straight tail, figures are tabular (same width in every weight of a style).
- Mono has its own forms for `i j l r f t I 1 0`; other glyphs are fitted to the 600-unit cell by
  compressing the *skeleton*, so stroke weights are not squeezed.

## Arabic details

- A simplified Naskh for reading sizes, not a calligraphic Naskh: one baseline, no stacked ligatures
  other than lam-alef.
- Drawn on its own grid and enlarged by 1.28 so teeth and loops match the Latin x-height zone; alef and
  lam reach 768 units (Latin capitals: 700).
- Every joined form ends exactly on the glyph edge (with an 8-unit overlap), so joins are seamless.
- Medial meem hangs below the baseline, medial heh is a bow above and below it, sad and tah have a long
  leaf-shaped loop, so they cannot be confused in running text.
- Italic Arabic leans 9° to the left. Change `AR_ITALIC_TAN` in `arabic.py` for a rightward slant.
- In Suhar Mono each Arabic glyph occupies one cell; the baseline stroke is extended to the cell edges.

## Metrics

1000 units per em. Cap height 700, x-height 520, descender -200. Line: ascent 940, descent -360
(1.30 em) in all families and all three metric sets (typo, hhea, win), so line spacing is the same on
every platform. Mono cell: 600 x 1300.

## Optical size (variable fonts only)

`opsz` 8 is sturdier (+5 % stem, +11 % horizontals), wider and looser; `opsz` 72 is finer and tighter.
The static fonts are the `opsz` 14 design.

## Kerning

Computed from the outlines (`kern.py`): the gap profile of each pair is compared with H-H; about 4,000
pairs for Latin letters and punctuation. Accented letters share their base letter's values, with
reduced values after T V W Y F P.

## Greek and Cyrillic

Letters that share a form with Latin reuse its skeleton. Other Cyrillic lower-case letters are the capital
skeleton refitted to the x-height with the lower-case pen, so the weight matches a e o. Greek lower case is
drawn separately. Both follow the Latin proportions and terminals.

## OpenType features

`kern`, `mark`, `mkmk` (all scripts); `init`, `medi`, `fina`, `rlig` (Arabic); `dlig` (the word Allah; code
ligatures in Mono); `frac`; `zero`. Italics use a single-storey a.

Added in 1.3:
- `ss01` "Khanjar tails": y, g, j, Q, J end in a hooked tail; Arabic reh, zain, waw and their relatives end in a
  long tapering blade instead of a flat stroke. Off by default, meant for headlines and signage.
- `ss02` dotted zero, `ss03` plain zero.
- `calt`: in a run of three or more toothed letters (ب ت ث ن ي medial), the middle teeth are raised so the
  word does not read as a comb. Short words are untouched.
- `dlig` (Arabic): compact lam-meem, lam-hah/jeem/khah and feh-yeh.
- Mono `dlig`: `:=` and `|>` joined the code ligatures.

Added in 1.4:
- `smcp`/`c2sc` small capitals (also for accented letters), `pnum`/`tnum`, `sups`, `subs`, `numr`, `dnom`, `ordn`.
- End-of-ayah numbers: digits that follow U+06DD are replaced by small fixed-width figures (`rlig`) and the
  sign's advance is reduced so they land inside it (`dist`); one, two or three digits are centred.
- Kerning after tailed Arabic letters (ر ز و and relatives), measured from the outlines like the Latin kerning
  and limited by the closest approach, so رر does not collide.
- Letters for Pashto, Sindhi, Uyghur; U+0649 joins on both sides as Unicode specifies.

## Suhar Naskh (1.6)

The Arabic of Suhar Naskh is produced from the same skeletons as Suhar by four changes in the generator:
a contrasted reed pen (long axis at 62 degrees, ratio about 2.6 : 1) so the baseline is heavy, uprights lighter
and up-strokes thin; a warp of the skeleton (below the baseline strokes sweep left by 0.30 of their depth, above
it uprights lean right by 0.055); rounder corners (tension 0.57 instead of 0.70); and pointed terminals where
the pen leaves the paper (free stroke ends, feet of uprights, tops of teeth). Dots become slanted rhombs through
the same warp. Proportions, joins, features and the Latin are those of Suhar, which is what keeps the two
families recognisably one design. It is a Naskh-style text and title face, not a copy of a calligrapher's hand.

Added in 1.7. Ten skeletons are drawn separately for the Naskh families (`NSPEC` in `arabic.py`): the wavy head
and round bowl of ج ح خ, the head of ع, a pointed ه, the looped لا and the swept top of ك. By rule, the bowls of
ن س ص ق ل end in an inward curl, the boat of ب ف ك rises in a curve, and the loops of ف ق و ه come to a point.

Suhar Naskh Display adds a sloping line: letters that join forward are sheared so they fall 4 % to the left, and
cursive attachment (`curs`, entry and exit anchors) stacks them, so a word starts high on the right and lands on
the baseline at its last letter. Use it for titles; at text sizes the slope turns into stair-steps, which is why
Suhar Naskh itself stays level.

Added in 1.8. م and ي are drawn for the Naskh as well (a long tapering meem tail, a wider yeh bowl with a curl).
The top of ك ends in a point instead of a flat cut. A returning yeh (the tail sweeps back to the right under the
previous letter, as in في على إلى) replaces final ي ى after a letter that has nothing under the line: by default
in Naskh Display (`calt`), on request in Suhar Naskh (`ss06`). `dlig` gained lam standing on a medial meem (لمح).
Suhar Naskh has italics, and both Naskh families have variable fonts.

Added in 1.9. Word spacing: a word-final letter whose body stands to the right of a tail under the line (ر ز و and
final م) is kerned against the space by 0.6 of that overhang, at most 110 units, so the gap the eye sees is close to
the gap after other letters while the tail still covers less than half of the space. Alef and lam carry smaller
side bearings, which closes the gap inside ال. In the Naskh families ن ت ث can stand on the head of ج ح خ (`calt` in
Display, `ss07` in Suhar Naskh), and the loop of the lam-meem ligature grows with the weight.

Added in 2.0. Suhar Mono draws ص ض س ش for the cell (`MSPEC`): closer teeth, a long low loop and a narrower bowl, so
they are no longer the proportional drawings squeezed to 600 units. ب ي پ also stand on ج ح خ, with their dots under
the raised letter. The loop of ص ض ط ظ is a little higher. Suhar has a Black weight. Hebrew is kerned from its
outlines like Latin. Suhar Pixel 8, 9 and 10 share the hand-drawn Arabic, which now includes ک گ چ ے and a Bold
made by doubling each pixel to the right.

## Hand-drawn pixel Arabic (1.6)

`src/retrofont/pixel_arabic.py` holds one bitmap per letter body and form (72 drawings, one-pixel strokes,
alef 7 px, teeth 3 px, descenders 3 px). Dots and hamza are placed by rule from the letter table, so the set
covers 204 glyphs. Suhar Pixel 8 and 9 use these in place of the automatic raster; letters outside the set
(for example گ چ ک ے) fall back to the raster.

## Weights, widths and pixel fonts (1.3)

Light (300) and ExtraBold (800) are extrapolated from the same Regular and Bold parameters; they are static
fonts. Suhar Condensed scales the Latin skeleton widths to 82 % (Arabic to about 90 %) while keeping stem weight,
so it is redrawn, not squeezed. The pixel fonts are made by `src/retrofont/pixel.py`: FreeType renders each
glyph of the hinted font at one size in 1 bit, and that bitmap becomes the outline (100 units per pixel).
At the design size, or a whole multiple, every renderer shows the same pixels with no grey blur. Kerning is
dropped and advances are whole pixels; Arabic shaping and marks are kept.
