# Known limitations (version 2.1)

I would rather list these here than have you find them in production.

## Design

- The outlines are generated from skeletons and a pen. They have not been refined by hand in a font editor,
  and spacing and kerning are computed. A type designer's pass would improve both, most of all in the heavy
  weights.
- **Suhar's Arabic** is a simplified Naskh: clean and even, without the changes of shape a calligrapher makes
  from one neighbour to the next. The only shapes that depend on the neighbour are the tall teeth, the
  returning yeh and (in the Naskh families) letters standing on ج ح خ.
- **Suhar Naskh** is built from the same skeletons with a contrasted pen, a warp and pointed terminals.
  Fourteen letter bodies are drawn for it; the rest follow by rule. It reads as a Naskh, but it is not a
  calligrapher's hand and no calligrapher has reviewed it. Regular to Bold only, and no Nerd build.
- **Suhar Naskh Display** needs a layout engine with cursive attachment. HarfBuzz has it and is the only one
  I tested; without it the letters still join but each sits on its own level. Use it from 24 px up: at text
  sizes the slope turns into steps. It has no italics.
- The stacked ligatures (لم لمح لح في) are simple and stay optional (`dlig`). There is no stacked form of على
  beyond the returning yeh.
- Arabic cannot be justified by lengthening letters from inside a font; that needs the layout program.
  Applications can insert tatweel (U+0640), which joins correctly.
- Word spacing is evened out by kerning against the space. A renderer that does not kern spaces shows a wider
  gap after ر ز و. The gap after these letters is still a little wider than after others, more so in the
  Naskh families.
- Light, ExtraBold and Black are extrapolated from Regular and Bold, not drawn separately. Past Bold the
  Arabic pen grows more slowly so the counters stay open, which leaves heavy Arabic a little lighter than
  heavy Latin. Black exists in Suhar only.
- Italics are slanted, with a single-storey a; they are not cursive drawings. Arabic italics lean to the left.
- Small capitals and old-style figures are derived from the capitals and the lining figures, not drawn
  separately.
- In Suhar Mono, ص ض س ش are drawn for the cell; the other letters are the proportional skeletons refitted
  to it, and joins are long. That is the price of one-cell Arabic. `ss05` gives the wide letters two cells,
  but only where glyphs are placed by their width; a terminal gives every Arabic letter one cell.
- The pictograms are simple original drawings, not a designed signage system and not Oman's official road
  signs. U+E100 is a simplified drawing, not the official national emblem.
- The currency signs keep one outline at every weight. The Omani rial sign is the Central Bank of Oman's
  outline; I have not compared the Saudi riyal and UAE dirham signs with their central banks' files.

## Suhar Sahafa

- Sahafa is the newest family and has had the least use.
- I wanted it to read better in newspapers than Yakout, Mohammed and Traditional Arabic. **I cannot show
  that.** I do not have those fonts, so there is no comparison with them at all. Against Amiri, Noto Naskh
  Arabic and Scheherazade New I measured larger loops at the same point size and a longer line (the table is
  in the README). Nobody has run a reading test, and it has not been printed on newsprint or on a press.
- It is a constructed Naskh, like the rest of Suhar: one pen angle, no change of shape by neighbour except
  the features inherited from Suhar Naskh. A calligrapher would call it a Naskh in proportion and not in hand.
- The first sketch is heavier than Sahafa Regular: its strokes are close to Sahafa Bold. I kept Regular at a
  text weight, because a paragraph at the sketch's weight would fill in at 8 point.
- Ink traps are cut by rule: every sharp inner corner between the baseline and the loop height gets a notch
  of about 0.4 of the stroke's half thickness (0.3 in Headline). They are not placed by eye, they are untested
  on a press, and the variable fonts do not have them, because their outlines keep the overlaps.
- Drawn for Sahafa: ص ض ط ظ, ج ح خ, ف ق و, م, ه ة, ي, ا ل, لا, ر ز, د ذ, ن, the teeth of ب ت ث ن ي, medial and
  final ع غ and ع غ at the start of a word. Still the Suhar Naskh skeleton in the Sahafa proportions: the bowls
  of ب ت ث, س ش, isolated ع غ, ك, and the Persian, Urdu, Kurdish, Pashto, Sindhi, Uyghur and Jawi letters. I
  have proofed the Arabic alphabet and news text, not those other languages.
- Ligatures: lam-alef is drawn. The optional ligatures (`dlig`), the returning yeh (`ss06`) and letters
  standing on ج ح خ (`ss07`) work and are checked for shaping, but their shapes come from Suhar Naskh; in
  Headline Bold the loop of the lam-meem ligature is nearly closed.
- The italics are slanted forms, not a drawn cursive; the Arabic leans to the left, as in Suhar.
- Latin: the serifs have straight wedge brackets, not curved ones. Diagonal letters (A K V W X Y k v w x y)
  have serifs without brackets. The figures 0 3 6 8 9, punctuation and ß æ œ ð þ have the Sahafa pen but no
  serifs; Cyrillic and Greek letters have serifs only where they share a Latin shape, plus Γ Π Λ Φ Ψ.
- The x-height is 470, to match the Arabic loops; Suhar's is 520. Next to Suhar at the same size the Sahafa
  lower case is smaller. Capitals, figures, ascent, descent and line height are the same.
- There is no Nerd build of Sahafa. A newspaper face has no use for terminal icons, so I left it out.

## Pixel fonts

- Each pixel font is right at its own size and at whole multiples of it, nowhere else. No italics.
- Suhar Pixel 8, 9 and 10 share one hand-drawn Arabic bitmap set. Urdu ہ ھ and letters with rings or four
  dots fall back to an automatic raster. Vowel marks can be a pixel off. The Bold doubles every pixel.
- Suhar Pixel 11–13 and Suhar Mono Pixel are automatic rasters. Latin is clean; in Arabic some dots merge.

## Coverage

- No Indic scripts, CJK, Thai, Armenian or Georgian.
- Polytonic Greek stacks breathings and accents above the letter, also on capitals, which is not how it is
  normally set.
- Cyrillic covers Russian, Ukrainian, Belarusian, Bulgarian, Serbian, Macedonian and Kazakh.
- Hebrew has letters and points, no cantillation marks and no rafe. The points sit at computed positions.
- The Pashto, Sindhi and Uyghur letters are assembled from existing letter bodies and dot rules. Their dot
  counts are checked against Noto Sans Arabic, but readers of those languages have not reviewed them, and
  neither has a Hebrew reader. ۍ has a simplified tail.
- Numbers go inside the end-of-ayah sign (up to three digits) in the proportional families, not in Suhar Mono.
- Honorific signs U+0610–0614 and the word ligatures U+FDF0–FDFD are composed from the font's own letters.
- There is no kerning between scripts: layout engines shape each script as a separate run.
- The symbol blocks are subsets; see `COVERAGE.md`.

## Engineering

- Hinting is automatic (ttfautohint for TrueType, otfautohint for CFF). Box drawing, symbols and icons are
  unhinted, and so are the variable fonts.
- The variable fonts keep overlapping contours and have a weight axis of 400–700. There are no variable Nerd
  fonts.
- Line spacing comes from the typo metrics (940/−360). The Windows clipping box of the proportional families
  is larger (1200/−440) so stacked marks are not cut; a Windows program that ignores `USE_TYPO_METRICS`
  spaces the lines wider. In Suhar Mono the box equals the cell, so very tall mark stacks can be clipped.
- In Suhar Nerd Mono the icons are scaled to one cell and are small.

## Testing

- Tested: shaping with HarfBuzz, rendering with FreeType, structure with fontTools and the OpenType Sanitizer,
  PDF embedding, and loading in Retro Nim UI.
- Not tested: Windows (DirectWrite, GDI, ClearType), macOS (CoreText), Android, the major browsers, Adobe
  applications, and physical printers. `specimen/device-test/` is the page to open on those systems; reports
  with screenshots are welcome.
- A web search found no typeface named exactly "Suhar". That is not a trademark search.
