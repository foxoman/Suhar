# Icon and private-use mapping

## Suhar interface icons (all four families)

Original drawings in the Private Use Area. The block U+E100–E1FF is not used by Nerd Fonts 3.5.1; `tools/validate.py` checks that the Nerd build keeps these glyphs.

| Code point | Glyph name | Nim (`suhar.nim`) |
|---|---|---|
| U+E100 | retroui.oman-emblem | `siOmanEmblem` |
| U+E101 | retroui.crossed-swords | `siCrossedSwords` |
| U+E102 | retroui.khanjar | `siKhanjar` |
| U+E110 | retroui.win-minimize | `siWinMinimize` |
| U+E111 | retroui.win-maximize | `siWinMaximize` |
| U+E112 | retroui.win-restore | `siWinRestore` |
| U+E113 | retroui.win-system-menu | `siWinSystemMenu` |
| U+E114 | retroui.win-close | `siWinClose` |
| U+E115 | retroui.checkbox | `siCheckbox` |
| U+E116 | retroui.checkbox-checked | `siCheckboxChecked` |
| U+E117 | retroui.radio | `siRadio` |
| U+E118 | retroui.radio-selected | `siRadioSelected` |
| U+E119 | retroui.scroll-up | `siScrollUp` |
| U+E11A | retroui.scroll-down | `siScrollDown` |
| U+E11B | retroui.scroll-left | `siScrollLeft` |
| U+E11C | retroui.scroll-right | `siScrollRight` |
| U+E11D | retroui.combo-arrow | `siComboArrow` |
| U+E11E | retroui.resize-grip | `siResizeGrip` |
| U+E11F | retroui.submenu-arrow | `siSubmenuArrow` |
| U+E120 | retroui.folder | `siFolder` |
| U+E121 | retroui.document | `siDocument` |
| U+E122 | retroui.floppy | `siFloppy` |
| U+E123 | retroui.hourglass | `siHourglass` |
| U+E124 | retroui.pointer | `siPointer` |
| U+E125 | retroui.gear | `siGear` |
| U+E126 | retroui.search | `siSearch` |
| U+E127 | retroui.trash | `siTrash` |
| U+E128 | retroui.window | `siWindow` |
| U+E129 | retroui.terminal | `siTerminal` |
| U+E12A | retroui.info | `siInfo` |
| U+E12B | retroui.question | `siQuestion` |
| U+E12C | retroui.error | `siError` |
| U+E12D | retroui.program-group | `siProgramGroup` |
| U+E12E | retroui.nim-crown | `siNimCrown` |
| U+E130 | retroui.crenellation | `siCrenellation` |
| U+E131 | retroui.wave | `siWave` |
| U+E132 | retroui.dhow | `siDhow` |
| U+E133 | retroui.frankincense-burner | `siFrankincenseBurner` |
| U+E134 | retroui.fort | `siFort` |
| U+E135 | retroui.palm | `siPalm` |
| U+E136 | retroui.dallah | `siDallah` |
| U+E137 | retroui.mosque | `siMosque` |
| U+E138 | retroui.port | `siPort` |
| U+E139 | retroui.airport | `siAirport` |
| U+E13A | retroui.hospital | `siHospital` |
| U+E13B | retroui.parking | `siParking` |
| U+E13C | retroui.souq | `siSouq` |
| U+E13D | retroui.restaurant | `siRestaurant` |
| U+E13E | retroui.hotel | `siHotel` |
| U+E13F | retroui.fuel | `siFuel` |
| U+E140 | retroui.bus | `siBus` |
| U+E141 | retroui.sun | `siSun` |
| U+E142 | retroui.beach | `siBeach` |
| U+E143 | retroui.sindbad-ship | `siSindbadShip` |
| U+E144 | retroui.toilets | `siToilets` |
| U+E145 | retroui.exit | `siExit` |
| U+E146 | retroui.pharmacy | `siPharmacy` |
| U+E147 | retroui.qibla | `siQibla` |
| U+E148 | retroui.taxi | `siTaxi` |

U+E100 is a simplified, original drawing of a khanjar over crossed swords. It is **not** the official artwork of the national emblem of Oman and must not be used where the official emblem is required.

## Powerline (drawn by Suhar on the exact Mono cell)

| Code points | Content |
|---|---|
| U+E0A0–E0A3 | branch, line number, lock, column number |
| U+E0B0–E0B3 | solid and outline arrow separators |
| U+E0B4–E0B7 | half-round separators |
| U+E0B8–E0BF | corner triangles and diagonals |

## Nerd Fonts 3.5.1 icons (Suhar Nerd and Suhar Nerd Mono only)

Merged unchanged in shape from the official *Symbols Nerd Font* (see LICENSES). Where Suhar already has a glyph for a code point the Suhar glyph is kept. In Suhar Nerd Mono every icon is scaled to fit one 600-unit cell; in Suhar Nerd icons keep their own width.

| Set | Range | Code points present |
|---|---|---:|
| Seti-UI + Custom | U+E5FA–U+E6BB | 194 |
| Devicons | U+E700–U+E8EF | 496 |
| Font Awesome | U+ED00–U+F2FF | 1488 |
| Font Awesome Extension | U+E200–U+E2A9 | 170 |
| Material Design | U+F0001–U+F1AF0 | 6896 |
| Weather | U+E300–U+E3E3 | 228 |
| Octicons | U+F400–U+F533 | 308 |
| Powerline + Extra | U+E0A0–U+E0D7 | 40 |
| IEC Power | U+23FB–U+23FE | 4 |
| Font Logos | U+F300–U+F381 | 130 |
| Pomicons | U+E000–U+E00A | 11 |
| Codicons | U+EA60–U+EC1E | 439 |

Total code points in Suhar Nerd Mono: 13064.

For the name of each Nerd icon use the upstream cheat sheet: https://www.nerdfonts.com/cheat-sheet
