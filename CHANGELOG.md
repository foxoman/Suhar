# Changelog

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
