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
- Sahafa is meant for body text, and 2.6 reshapes it for that. **Whether it reads as easily as Traditional
  Arabic or Yakout I cannot show, and I do not expect it to.** Those are written Naskh hands, drawn by
  calligraphers and familiar to every reader; Sahafa is constructed from skeletons and one pen. I do not have
  those fonts, so there is no comparison with them. Against Amiri, Noto Naskh Arabic and Scheherazade New I
  measured loop size, stem height and line length (the table is in the README); those say how large and how
  economical it is, not how well it reads. Nobody has run a reading test, and it has not been printed on
  newsprint or on a press.
- The changes in 2.6 follow what makes written Naskh readable (stems against loops, teeth of different
  heights, deep bowls, close setting). They were judged by me from renderings beside Noto Naskh and Amiri, not
  by an Arabic typographer.
- It is a constructed Naskh, like the rest of Suhar: one pen angle, and seven changes of shape by neighbour
  (tall teeth, the narrow tooth before ر ز, the raised tooth before ن ي, the narrow ك, the returning yeh, ل on م,
  letters standing on ج ح خ). A written Naskh has dozens of such forms. A calligrapher would call it a Naskh in
  proportion and not in hand.
- Every letter has a Sahafa drawing now, but I can only judge the Arabic ones. The Persian, Urdu, Kurdish,
  Pashto, Sindhi, Uyghur and Jawi forms are drawn and compile; no reader of those languages has seen them.
- Regular is lighter than the first sketch, whose strokes are close to Sahafa Bold. Regular is at 103 units
  for the baseline stroke, which I judged the most a text weight can carry at 8 point.
- Ink traps are still cut by rule (every sharp inner corner between the baseline and the loop height). I have
  looked at them enlarged on the joins of ب س ص ط ح ف ك ع د ل م ن and removed the stubs I found, but they
  are untested on a press. In the variable fonts only 70 to 94 glyphs have them; the others keep overlapping
  outlines, because their sixteen masters do not match point for point once the overlaps are removed.
- The Arabic italic is the upright drawing slanted to the left; Arabic has no cursive italic to draw. In the
  Latin italic only a, n, l, w and the feet of d h i k m r u are redrawn; the other letters are slanted.
- Latin serifs have straight wedge brackets, not curved ones. 0 and 8 have no serifs, as in any serif face;
  punctuation and ß æ œ ð þ have the Sahafa pen without serifs; Cyrillic and Greek letters have serifs where
  they share a Latin shape, plus Γ Π Λ Φ Ψ.
- The x-height is 470; the Arabic loops are a little lower (about 445) and alef stands about 65 units above the
  Latin capitals. Suhar's x-height is 520. Next to Suhar at the same size the Sahafa
  lower case is smaller. Capitals, figures, ascent, descent and line height are the same.
- The khanjar tails (`ss01`) are the Suhar shapes in the Sahafa proportions, not redrawn.
- Sahafa Headline and the display end of the optical size axis fill their inner corners; the text cuts keep the
  ink traps. The curves of the Arabic joins themselves are unchanged.
- The Latin italic has its own a, f, l, n, w and exit strokes on d h i k m r u. It is still not a fully drawn
  cursive: b c e g o p q s t and the capitals are slanted roman forms.
- Punctuation, æ, œ and ð have no serifs, as in most serif faces; þ and ß have them.
- There is no Nerd build of Suhar Sahafa Caption, Suhar Naskh Caption or Suhar Typewriter.

## Suhar Typewriter

- It is the Sahafa skeleton struck with a pen of almost one thickness, with slab serifs and filled corners. It
  is **not monospaced**: Arabic cannot be set well in one cell, and Suhar Mono exists for that.
- The uneven ink of a real typewriter is not in the outlines. The preview images I made before had that
  effect added to the picture; in print the ribbon look comes from the paper and the printer, not the font.
- Two weights only, no variable font, and it has had no use yet.

## Sizes, paper and justification

- The tatweel axis lengthens every join by the same amount and with a straight stroke. A calligrapher lengthens
  a few chosen joins in a line and curves them; choosing the places is still the application's job, or that of
  `tools/kashida.py`.
- `TATW` and `CTRS` are axes of my own, not registered ones. Browsers reach them with `font-variation-settings`,
  and applications that list a font's axes show them as sliders; applications without variable font support
  cannot use them at all, and there are no static fonts for them.
- The contrast axis is small on purpose (about ±11 % of the pen's thin side); it is a correction, not a change
  of style.
- Light, ExtraBold and Black exist only as static fonts; the weight axis still runs from 400 to 700. In
  Sahafa Headline Black the small counters of م ع and of joined ه close up.
- The three stylistic sets are alternatives I drew, not forms collected from readers; ss09 changes only the
  plain alef and its hamza and madda forms.

- Optical sizes and grades exist only in the variable fonts, apart from the two Caption families. Suhar Naskh
  Display and Suhar Mono have neither axis; Suhar and Suhar Condensed have no grade axis.
- A grade is ±7 % of stroke weight. Which grade suits which paper is a guess until someone prints the proof.
- **Nobody has printed the print proof yet.** It is made and checked as a file (fonts embedded, 17 pages); the
  answers on its last page are what the next release should be built on.
- Small-screen hinting is still ttfautohint's, not tuned from screenshots, because I have no device-test
  results from Windows, Android or macOS. The larger dots and the wider mark distance apply at small optical
  sizes, that is in the variable fonts and in Sahafa Caption, not in the other static fonts.
- The kashida rules in `tools/kashida.py` are the common ones (after س ص, before final ه ة د, before final ا ل ك,
  and so on), one kashida per word. OpenType has no table an application would read them from, so they work
  only where that script or its web version is used.
- `jalt` and tatweel are what a font can offer for justification. Whether a justified column uses them depends
  on the application: Adobe InDesign (Middle East) does, most browsers and word processors only widen the
  word spaces. There is no rule in the font for where a kashida may go.
- The neighbour forms are judged by me from renderings. They are easy to switch off (`font-feature-settings:
  "calt" 0`).

## App fonts and Retro Nim UI

- The app fonts are tested in Retro Nim UI on a Linux virtual display at its default size, and their shaping is
  compared with the release fonts in HarfBuzz. They have **not been run on a phone**: I have not built or
  installed an Android or iOS app with them.
- They have no hinting. On Windows, in programs that use hinting, the release fonts will look crisper in small
  sizes; the app fonts are for programs that draw their own text.
- At the toolkit's default size (about 11 pixels) Suhar is readable but small for Arabic; that is a choice of
  size in the app, not something the font can change.
- Fully vowelled Arabic is taller than the line box by about a third of an em above and a quarter below, in
  every Suhar font. An interface row that clips its text will cut such marks unless it is made taller.
- `SuharAppLite` covers Arabic and Western European languages only. Text in another language falls back to the
  toolkit's built-in font, which looks different.
- Retro Nim UI decides whether a font has Arabic by its Arabic presentation forms, so the app fonts keep them.
- `setRtlInterface` makes mixed lines read right to left; in my test it did not mirror the layout of the
  example app. I did not look further into the toolkit.

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

- Fontbakery (universal profile) still reports these failing checks, which I have not fixed: `case_mapping`, `family/win_ascent_and_descent`, `fontdata_namecheck`, `opentype/STAT/ital_axis`, `valid_glyphnames`. Details are in `reports/fontbakery.md`.
- The specimen site is checked as a file only; I have not seen it served by GitHub Pages. The npm package is
  built and packed, not published.

- Tested: shaping with HarfBuzz, rendering with FreeType, structure with fontTools and the OpenType Sanitizer,
  PDF embedding, and loading in Retro Nim UI.
- Not tested: Windows (DirectWrite, GDI, ClearType), macOS (CoreText), Android, the major browsers, Adobe
  applications, and physical printers. `specimen/device-test/` is the page to open on those systems; reports
  with screenshots are welcome.
- A web search found no typeface named exactly "Suhar". That is not a trademark search.
