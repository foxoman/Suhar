# Suhar for Retro Nim UI

```nim
import retroui, suhar

useSuhar()            # or useSuharMono(), useSuharNaskh()
app "Hello", 320, 120:
  label "Suhar  صُحار  " & icon(siFolder)
```

- `suhar.nim` embeds the four styles of Suhar and of Suhar Mono, and Suhar Naskh Regular and Bold, with `staticRead` from `nim/fonts`
  and hands them to the toolkit with `setUiFontFile`. `-d:suharNerd` embeds the Nerd variants instead;
  `-d:suharFontDir=/path` reads the files from another folder.
- `SuharIcon` / `icon()` give the family's interface icons (U+E100–E148), `OmaniRialSign` etc. the new
  currency signs.
- `example.nim` is a small window; `tests/tload.nim` is the headless test that was run for
  `reports/nim-test.txt`:

```sh
nim c -r --path:<retroui>/src --path:<retroui>/tests -d:useMalloc tests/tload.nim
```

To make Suhar Mono the font of a terminal editor such as ned, install `SuharNerdMono-*.ttf` on the
system and select "Suhar Nerd Mono" in the terminal emulator (Termux: copy
`SuharNerdMono-Regular.ttf` to `~/.termux/font.ttf` and run `termux-reload-settings`).
