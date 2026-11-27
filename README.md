# Suhar  صُحار

**One typeface family for Arabic and Latin that looks like one design, from an 8‑pixel menu to a printed headline.**

![Suhar in Arabic and English](docs/images/hero.png)

Suhar is named after my home port: Suhar (Sohar), on the Batinah coast of Oman, the city the Sindbad
stories sail from. I started it as the interface font of [Retro Nim UI](https://github.com/foxoman/retroui)
and of my terminal editor ned, and it grew into a family for screens, bilingual signage and print.

- Designer: Sultan Al Isaiee ([@foxoman](https://github.com/foxoman), <https://www.foxoman.net>)
- Version 2.1 · SIL Open Font License 1.1
- Scripts: Latin (extended, Vietnamese, transliteration), Arabic (Arabic, Persian, Urdu, Kurdish, Pashto,
  Sindhi, Uyghur, Jawi, Quranic marks), Greek (monotonic and polytonic), Cyrillic, Hebrew with points
- 2,469 characters in Suhar, 13,064 in the Nerd builds

## Why I made it

Most bilingual interfaces pair a Latin font with an Arabic font drawn by someone else, at another size and
another weight. In Suhar both scripts come from the same pen and the same proportions, so a line that mixes
them keeps one colour and one height:

![Mixed paragraph](docs/images/paragraph.png)

## The families

| Family | Use it for | Styles |
|---|---|---|
| **Suhar** | interfaces, text, signage | Light to Black, with italics (14) |
| **Suhar Condensed** | signs and tight headlines, about 15 % narrower | Light to ExtraBold, with italics (12) |
| **Suhar Naskh** | books, magazines, long Arabic text | Regular to Bold, with italics (8) |
| **Suhar Naskh Display** | titles; joined words slope down to the left as in handwriting | Regular to Bold (4) |
| **Suhar Sahafa** | newspaper text: a low, wide Naskh with large open loops and a serif Latin | Regular to Bold (4) |
| **Suhar Sahafa Headline** | newspaper headlines: tighter, more contrast, deeper bowls | Regular to Bold (4) |
| **Suhar Mono** | code and terminals, 600‑unit cell | Light to ExtraBold, with italics (12) |
| **Suhar Nerd**, **Suhar Nerd Mono**, **Suhar Nerd Condensed** | the same with the Nerd Fonts 3.5.1 icons | as their base family |
| **Suhar Pixel 8–13**, **Suhar Mono Pixel 12/14** | one exact pixel size each, no blur | Regular, Bold |

Variable fonts: `Suhar[opsz,wght]`, `SuharCondensed[opsz,wght]`, `SuharNaskh[wght]`, `SuharNaskhDisplay[wght]`,
`SuharMono[wght]` and their italics (weight 400–700).

![Suhar Naskh and Naskh Display](docs/images/naskh.png)

### Suhar Naskh

The Arabic of Suhar Naskh is written with a contrasted reed pen: a heavy baseline, lighter uprights, tails
that sweep to the left, pointed terminals and slanted rhombic dots. The Latin is the Latin of Suhar, so the two
families sit together on one page. In Suhar Naskh Display a joined word starts high on the right and lands on
the baseline at its last letter, final yeh returns under the word (في، على، إلى) and toothed letters stand on
ج ح خ (نجم، بحر، تحت).

### Suhar Sahafa

![Suhar Sahafa](docs/images/sahafa.png)

Suhar Sahafa (صحافة, the press) is the newspaper cut. The Arabic is low and wide: alef is as tall as the Latin
capitals, the loops of ص ض ط ف ق و م ه are as tall as the Latin x-height, and the bowls are short, so lines can
be set close. The pen has moderate contrast (the upright is about two thirds of the baseline stroke), so the
thin strokes hold in small sizes. The Latin is a sturdy slab serif drawn with the same stem as the Arabic
baseline stroke, in Regular and in Bold. **Text** is the wider, calmer cut; **Headline** is about 5 % tighter,
with more contrast, sharper terminals and deeper bowls.

What I measured against three well-known open Naskh faces, at the same point size:

| | loop of ص (per em) | alef (per em) | length of the same line |
|---|---:|---:|---:|
| Suhar Sahafa Text | 0.47 | 0.72 | 100 % |
| Noto Naskh Arabic | 0.36 | 0.67 | 96 % |
| Scheherazade New | 0.35 | 0.70 | 97 % |
| Amiri | 0.29 | 0.70 | 88 % |

So the loops are about a third larger than in Noto Naskh and two thirds larger than in Amiri, and a line takes
4 to 14 % more room. Set one point smaller, Sahafa still has the larger loops and takes less room. I could not
compare it with Yakout, Mohammed or Traditional Arabic, because I do not have those fonts, and it has not been
printed on newsprint; see the limitations. `docs/images/sahafa-compare.png` shows the same paragraph in the
four faces.

### Suhar Mono

![Suhar Mono in an editor](docs/images/mono.png)

Every character takes one cell, Arabic included, so columns stay aligned in a terminal. Box drawing, blocks,
Braille and Powerline symbols are built on the cell and join without gaps. Code ligatures (`!=`, `=>`, `:=`,
`|>` …) are optional.

## What is inside

- **Arabic that is shaped properly**: all joining forms, lam‑alef, marks placed by anchors, kerning after
  ر ز و and against the space so words are evenly spaced, tall‑tooth alternates in long runs of teeth,
  Urdu figure forms, numbers set inside the end‑of‑ayah sign ۝.
- **The Omani rial sign** (U+20C4) from the Central Bank of Oman's own outline, with the Saudi riyal and
  UAE dirham signs.
- **An Omani touch you can switch on**: khanjar tails on y g j Q and ر ز و (`ss01`), the khanjar and crossed
  swords, a dhow, a fort, a dallah, a frankincense burner and wayfinding pictograms (U+E100–E148).
- **Typography**: small capitals, old‑style and proportional figures, fractions, superscripts and
  subscripts, slashed, dotted or plain zero.
- **Hinting** for small sizes in every static font, and hand‑drawn Arabic bitmaps in Suhar Pixel 8, 9 and 10.

| Feature | Tag |
|---|---|
| Khanjar tails | `ss01` |
| Dotted / plain / slashed zero | `ss02` / `ss03` / `zero` |
| Two‑cell ص ض س ش in Suhar Mono (editors that place glyphs by their width) | `ss05` |
| Returning yeh in Suhar Naskh | `ss06` |
| Letters standing on ج ح خ in Suhar Naskh | `ss07` |
| Arabic ligatures لم لمح لح في الله, code ligatures in Mono | `dlig` |
| Small capitals | `smcp`, `c2sc` |
| Old‑style, lining, proportional, tabular figures | `onum`, `lnum`, `pnum`, `tnum` |
| Fractions, superscript, subscript, ordinals | `frac`, `sups`, `subs`, `ordn` |

## Install

Download a release, or take the files from `dist/` in this repository.

| System | Steps |
|---|---|
| **Windows** | Select the `.ttf` files in `ttf/`, right‑click, *Install for all users*. |
| **macOS** | Open the `.ttf` files with Font Book and press *Install*. |
| **Linux** | `mkdir -p ~/.local/share/fonts/suhar && cp ttf/*.ttf ~/.local/share/fonts/suhar/ && fc-cache -f` |
| **Termux** | `cp SuharNerdMono-Regular.ttf ~/.termux/font.ttf && termux-reload-settings` |
| **Android app** | Put the `.ttf` in `res/font/`, or load it with `Typeface.createFromFile`. |
| **Web** | Use the files in `woff2/` (see below). |

Install either the static fonts or the variable fonts of a family, not both: they share their names.

```css
@font-face {
  font-family: "Suhar";
  src: url("Suhar[opsz,wght].woff2") format("woff2");
  font-weight: 400 700;
}
body { font-family: "Suhar", system-ui, sans-serif; }
h1:lang(ar) { font-family: "Suhar Naskh Display", "Suhar", serif; }
.news     { font-family: "Suhar Sahafa", serif; }
.news h2  { font-family: "Suhar Sahafa Headline", serif; }
.price { font-feature-settings: "tnum"; }
```

`specimen/device-test/index.html` is a one‑page check list: open it on a phone or a browser and it tells you
what a correct result looks like for joins, kerning, the sloping Naskh, the rial sign and the Mono grid.

### Retro Nim UI

```nim
import retroui, suhar

useSuhar()            # or useSuharMono(), useSuharNaskh()
app "Hello", 320, 120:
  label "Suhar  صُحار  " & icon(siDhow) & "  " & OmaniRialSign & " 1.500"
```

The module is in `nim/`; it embeds the fonts at compile time. See `nim/README.md`.

## Build it yourself

The fonts are not drawn in a font editor. Every glyph is a skeleton written in a small text language and
expanded by a pen, so a weight, a width or a new family is a change of parameters.

```sh
python -m pip install -r requirements.txt
cd src && python -m retrofont.build --out ../dist     # every font; about an hour on two cores
cd .. && python tools/validate.py                     # the checks, reports/validation.md
python tools/make_docs.py                             # coverage tables, specimen, glyph catalogue
```

`--only Sans-Regular,Mono-Bold` builds single styles; `--no-nerd` and `--no-vf` skip those steps.
`tools/finish.sh` runs everything in order.

| Path | Content |
|---|---|
| `src/retrofont/` | the generator: `engine.py` (skeleton language and pen), `latin*.py`, `arabic.py`, `greek_cyrillic.py`, `more_scripts.py`, `symbols.py`, `terminal.py`, `sahafa.py`, `kern.py`, `features.py`, `pixel.py`, `pixel_arabic.py`, `nerd.py`, `build.py` |
| `dist/` | the built fonts: `ttf/`, `woff2/`, `variable/`, `pixel/` (OpenType/CFF files, the Nerd builds and the UFO masters are in the release archives) |
| `tools/` | validation, documentation, proof renderer (HarfBuzz and FreeType) |
| `docs/` | design notes, coverage, icons, licensing, limitations, glyph catalogue |
| `reports/` | the validation report and rendered proofs |
| `specimen/` | HTML specimen and the device test page |
| `nim/` | Retro Nim UI module, example and test |
| `third_party/` | Nerd Fonts symbol fonts and the currency sign outlines, with their notices |

## Checked, and not checked

Each release runs 1,986 automatic checks on the built files: naming, metrics, hinting, shaping in every
script, mark placement, kerning, the space between words in every style (`reports/word-spacing.md`), the Mono grid, the pixel fonts, the variable fonts, and loading in Retro Nim
UI. The report is `reports/validation.md`.

What these checks cannot tell me is in [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md). The short version: the
outlines are generated and have not been finished by hand, Suhar Naskh is a Naskh in style and not a
calligrapher's hand, and readers of Pashto, Sindhi, Uyghur and Hebrew have not reviewed those letters yet.
If you read one of these languages, or you see a wrong shape anywhere, please open an issue with a
screenshot.

## Licence

The fonts are under the [SIL Open Font License 1.1](OFL.txt): use them, embed them, change them and
redistribute them, also commercially; keep the licence with them and do not sell the fonts on their own.
The generator in `src/` and `tools/` is under the same licence. The Nerd builds contain icon sets under
their own licences, and the currency signs follow their central banks' guidelines; see
[`docs/LICENSING.md`](docs/LICENSING.md) and `LICENSES/`.

Copyright © 2026 Sultan Al Isaiee.
