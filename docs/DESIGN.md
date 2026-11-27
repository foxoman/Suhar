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

## Suhar Sahafa (2.1)

A newspaper face has to stay open in 8 and 9 point on poor paper and still save room. Sahafa gets there by
proportion and not by weight. In font units (1000 per em):

| | Suhar Naskh | Suhar Sahafa |
|---|---:|---:|
| alef | 800 | 715 (cap height 700) |
| loop of ص | 385 | 470 (the Latin x-height) |
| tooth | 450 | 375 |
| bowl of ن | −265 | −250 (Headline −280) |
| pen ratio | 2.6 : 1 | 1.6 : 1 (Headline 2.1 : 1) |

- `sahafa.py` holds the letters drawn for the family as replacement bodies (`ARABIC`); dots and marks of the
  shared letter definitions are moved to the new body. Letters without a body are mapped through one
  piecewise vertical scale (`_armap`), so stems, teeth and bowls land on the same heights.
- The joining line sags by 7 units between two joins (`swing`), terminals taper to 62 % (Headline 42 %),
  and strokes below the line sweep left by 16 % of their depth (Headline 20 %).
- Letters are set 7 % narrower than in Suhar Naskh (Headline a further 4 %).
- Latin: the Suhar skeletons with the x-height lowered to 470 by a vertical map (ascenders stay at 700),
  slab serifs added per letter (`SERIF`), and a e g l n s w drawn again (`LATIN`). The stem is the Arabic
  baseline half-thickness; the horizontals are 66 % of it (Headline 56 %). A serif reaches a fixed distance
  beyond the stem edge, so it does not disappear in Bold.
- The word space is 278 units in Text and 256 in Headline.

### Measuring the space between words

`tools/wordspace.py` shapes every word-final Arabic letter against fourteen word-initial letters and
measures the gap twice: between the letter bodies (baseline to loop height) and between the full outlines.
The mean of the two is the optical gap, so a tail under the line counts for half. In an italic the outlines
are set upright first, because the eye measures a gap along the slant. Across all proportional styles the
standard deviation of the gap is 8 to 14 units on a mean of about 350 to 375.

### Sahafa after the sketch (2.2)

- Medial ح: `470,k`-style join on the right, then one arc over to a cut terminal on the left. The space under
  the arc is open to the left, which is what keeps it clear in Bold.
- Wedge teeth: the top of a tooth is drawn at 60 % of the pen (Headline 50 %).
- Ink traps (`engine.ink_traps`): after the overlaps are removed, every on-curve corner where the ink turns
  inwards by 55 to 150 degrees, between 1.2 × the baseline half-thickness and 440 units, is cut with a small
  triangle along the bisector of the corner.
- Wedge brackets are filled triangles between the stem and the serif; their size follows the serif length.
- Italics use the slants of Suhar (Latin 11 degrees to the right, Arabic 9 degrees to the left).

### Sahafa completed (2.3)

- `ARABIC` has a body for every key of `RASM` (88). The ligatures and alternates have no skeleton key, so
  `_ligatures()` replaces their Suhar Naskh skeleton text by the Sahafa one.
- A body moves the marks above with `dy` and the marks below with `bdy`, so a lower alef does not pull the
  kasra down with it.
- Italic: `LATIN_IT` and `SERIF_IT` replace the foot serif of the last stem by an exit stroke.
- Variable fonts: the trapped outline of a glyph is used when both masters have the same contours, the same
  points and no point further than 150 units from its partner; 120 to 148 glyphs qualify.

## Sizes, paper and justification (2.4)

- **Optical size** for the pen-written Arabic: the caption master narrows the pen ratio (Sahafa 1.6 : 1 → 1.4 : 1,
  Naskh 2.6 : 1 → 2.2 : 1), enlarges the dots by 14 %, moves the mark anchors 24 units away from the letter,
  deepens the ink traps by half and adds 16 units to every sidebearing; the display master does the opposite.
- **Grade**: the pen is 7 % lighter or heavier. `keep_advances` then gives every glyph the advance of the
  ungraded master and moves the outline so that the joins stay where they are: not at all for a letter that
  joins to the left, by the whole difference for one that joins only to the right, by half for the others.
  Kerning is the ungraded kerning.
- **Neighbour forms**: skeletons `behr.init`, `behr.medi` and `rehr.fina`; `calt` replaces the tooth first, then
  the reh after a replaced tooth. The raised tooth before final ن ي reuses the tall tooth.
- **jalt**: the same skeleton with its x coordinates multiplied by 1.4; the pen is not stretched, so the
  stroke weight is unchanged.
- **Ink traps in the variable fonts**: a glyph uses its trapped outline when all ten masters agree; 78 to 100
  glyphs do.
- **Print proof**: `tools/print_proof.py` writes an HTML page that loads the built fonts and lets Chrome print it
  to PDF, so the PDF embeds the real fonts.

## 2.5

- **Medial ain** is a closed stroke through three corners (top left, top right, the foot on the baseline) with a
  slightly hollow top, instead of a rounded blob. In the heavy weights the counter closes, as it does in
  written Naskh.
- **Word space**: `kern.arabic_word_space` gives every word-final Arabic letter a kern of −48 against the space
  (scaled with the space in Condensed), adds up to −120 for a tail under the line, and −24 between the space and
  an initial alef. The mean optical gap between two Arabic words is about 320 units; between two Latin words 345
  to 370.
- **Grade** is a parameter of `Style`, so every family can be graded; the Arabic pen follows it.
- **Filled corners** use the ink-trap routine with the triangle added instead of removed.
- **Suhar Typewriter** is `sahafa.style(cut='typewriter')`: pen ratio 1.06 : 1, Latin horizontals at 92 % of the
  stem, no tapering, sidebearings 10 % wider, Regular 22 % heavier than Sahafa Regular.
