# Changelog

## 2.4 (November 2026)

**Sizes and paper**
- Optical size axis in the variable fonts of Suhar Naskh and Suhar Sahafa (8–72), as Suhar already had.
- Suhar Sahafa Caption: the 8-point cut as static fonts, eight styles.
- Grade axis (GRAD −50 to 50) in the Suhar Sahafa variable fonts; a grade never changes an advance width.
- The variable font files are renamed: `SuharNaskh[opsz,wght]`, `SuharSahafa[GRAD,opsz,wght]`,
  `SuharSahafaHeadline[GRAD,opsz,wght]`.
- `docs/Suhar-print-proof.pdf` and `tools/print_proof.py`.

**Arabic**
- Neighbour forms in the Naskh and Sahafa families: a narrow tooth and a short ر ز after it; a raised tooth
  before final ن ي.
- Justification alternates (`jalt`) for final and isolated ب ت ث ف ك and their Persian and Urdu relatives.
- Sahafa: the dots over a tooth sit closer to it.

**Latin (Sahafa)**
- The serif brackets are curved.

## 2.3 (November 2026)

**Suhar Sahafa, completed**
- Every letter skeleton now has a drawing of its own in Sahafa: ب ت ث, س ش, ع غ, ك and the Persian, Urdu,
  Kurdish, Pashto, Sindhi, Uyghur and Jawi forms were added.
- The ligatures and alternates are redrawn: lam-meem (four forms), lam on ج ح خ, feh-yeh, the returning yeh,
  and the letters that stand on ج ح خ.
- Regular is 7 % heavier (baseline stroke 103 units); Bold is unchanged.
- Drawn italic for the Latin: a one-storey a, n and l of their own, exit strokes instead of foot serifs.
- Wedge brackets on the diagonal letters; terminals on the figures 3, 6 and 9.
- Ink traps in the variable fonts, in the 120 to 148 glyphs whose two masters match point for point.
- Nerd builds: Suhar Nerd Sahafa and Suhar Nerd Sahafa Headline.
- Fixed: marks under ا ل ك ط ص ف sat too low or too high in 2.2; small stubs under the joins of د ك ب س.

## 2.2 (November 2026)

**Suhar Sahafa, reworked after the first sketch**
- Medial ح is an arc that starts at the join and sweeps over to the left, open underneath, also in Bold.
- Teeth are wedges; final ه ة comes to a point at the top; ط ظ carry the stem on the end of the loop, so the
  small counter beside the stem is gone; the baseline is flat again.
- More letters drawn for the family: ر ز, د ذ, ن, and ع غ at the start of a word.
- Small ink traps at the inner corners between the baseline and a tooth or stem (static fonts).
- Latin: wedge brackets on the serifs; serifs on the figures 1 2 4 5 7 and on Γ Π Λ Φ Ψ.
- Italics for both cuts, and variable fonts `SuharSahafa[wght]` and `SuharSahafaHeadline[wght]` with italics.
- Sahafa is in the HTML specimen and on the device test page.

## 2.1 (November 2026)

**New: Suhar Sahafa and Suhar Sahafa Headline**
- A newspaper Naskh with a serif Latin, Regular, Medium, SemiBold and Bold in each cut.
- Arabic: alef at the cap height, loops at the Latin x-height (470), short bowls, moderate pen contrast.
  ص ض ط ظ ح ج خ ف ق و م ه ة ي ا ل لا, the teeth of ب ت ث ن ي and medial and final ع غ are drawn for this
  family; the other letters are the Suhar Naskh skeletons in the lower proportions.
- Latin: slab serifs on A–Z and a–z, the stem as thick as the Arabic baseline stroke in every weight.
- Headline: about 5 % tighter, more contrast, sharper terminals, deeper bowls, a narrower word space.
- Same cap height, ascent, descent and line height as Suhar; the x-height is 470 instead of 520.

**Word spacing**
- `tools/wordspace.py` measures the gap between two words for every word-final Arabic letter and for Latin,
  in every proportional style; the result is `reports/word-spacing.md`, and the validation fails when the gaps
  of a style are uneven.
- Suhar Condensed: the word space is 14 % narrower (239 instead of 278 units), in step with the narrower letters.
- The no-break space is as wide as the space in the optical sizes of the variable fonts.

## 2.0 (November 2026)

The first public release.

**Families**
- Suhar, Suhar Condensed, Suhar Mono, and their Nerd builds.
- Suhar Naskh for text and Suhar Naskh Display for titles.
- Suhar Pixel 8–13 and Suhar Mono Pixel 12/14.
- Variable fonts for Suhar, Suhar Condensed, Suhar Naskh, Suhar Naskh Display and Suhar Mono.

**Arabic**
- Arabic, Persian, Urdu, Kurdish, Pashto, Sindhi, Uyghur and Jawi letters; Quranic marks and honorifics.
- Kerning after ر ز و and against the space, so words are evenly spaced.
- Tall-tooth alternates, the returning yeh, letters standing on ج ح خ, optional ligatures.
- Numbers inside the end-of-ayah sign.
- Suhar Mono draws ص ض س ش for the cell; `ss05` gives them two cells in editors that allow it.
- Hand-drawn Arabic bitmaps in Suhar Pixel 8, 9 and 10.

**Latin and other scripts**
- Extended Latin with Vietnamese and transliteration letters, Greek (polytonic), Cyrillic, Hebrew with points.
- Small capitals, old-style and proportional figures, fractions, superscripts and subscripts.
- Khanjar tails as a stylistic set.

**Symbols**
- The Omani rial sign from the Central Bank of Oman's outline; Saudi riyal and UAE dirham signs.
- Interface icons, Omani ornaments and wayfinding pictograms (U+E100–E148).
- Box drawing, blocks, Braille, Powerline; Nerd Fonts 3.5.1 in the Nerd builds.

**For developers**
- A module for Retro Nim UI (`nim/`).
- A device test page (`specimen/device-test/`).
- 1,663 automatic checks on the built files (`reports/validation.md`).
