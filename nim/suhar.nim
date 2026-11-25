## Suhar for Retro Nim UI (`retroui`).
##
## The four styles of the family are compiled into the program with
## `staticRead`, so an app needs no font files beside it:
##
## .. code-block:: nim
##   import retroui, suhar
##   useSuhar()                       # Suhar as the UI font (regular, bold, italic, bold italic)
##   app "Hello", 320, 120:
##     label "Suhar  صُحار  " & icon(siFolder)
##
## `useSuharMono()` makes the monospaced family the UI font (editors,
## terminals).  Build with `-d:suharNerd` to embed the Nerd variants
## (about 1.4 MB per style) so the Nerd Fonts icons are there too.
##
## The interface icons of the family live in the Private Use Area
## (U+E100..U+E148); `SuharIcon` names them and `icon()` gives the UTF-8 text.

import std/[os, unicode]
import retroui

const
  suharFontDir* {.strdefine.} = currentSourcePath().parentDir / "fonts"
    ## where the .ttf files are read from at compile time (`-d:suharFontDir=...`)
  suharNerd* {.booldefine.} = false
  sansStem = when suharNerd: "SuharNerd" else: "Suhar"
  monoStem = when suharNerd: "SuharNerdMono" else: "SuharMono"

  suharRegular* = staticRead(suharFontDir / sansStem & "-Regular.ttf")
  suharBold* = staticRead(suharFontDir / sansStem & "-Bold.ttf")
  suharItalic* = staticRead(suharFontDir / sansStem & "-Italic.ttf")
  suharBoldItalic* = staticRead(suharFontDir / sansStem & "-BoldItalic.ttf")
  suharNaskhRegular* = staticRead(suharFontDir / "SuharNaskh-Regular.ttf")
  suharNaskhBold* = staticRead(suharFontDir / "SuharNaskh-Bold.ttf")
  suharMonoRegular* = staticRead(suharFontDir / monoStem & "-Regular.ttf")
  suharMonoBold* = staticRead(suharFontDir / monoStem & "-Bold.ttf")
  suharMonoItalic* = staticRead(suharFontDir / monoStem & "-Italic.ttf")
  suharMonoBoldItalic* = staticRead(suharFontDir / monoStem & "-BoldItalic.ttf")

  SuharCredit* = "Suhar typeface by Sultan Al Isaiee (@foxoman), SIL Open Font License 1.1"
  SuharCellWidth* = 600        ## advance of every Suhar Mono glyph, in font units (1000 per em)
  SuharAscent* = 940
  SuharDescent* = -360

type
  SuharIcon* = enum            ## the family's own interface icons (same code points in all four families)
    siOmanEmblem = 0xE100, siCrossedSwords = 0xE101, siKhanjar = 0xE102,
    siWinMinimize = 0xE110, siWinMaximize = 0xE111, siWinRestore = 0xE112, siWinSystemMenu = 0xE113,
    siWinClose = 0xE114, siCheckbox = 0xE115, siCheckboxChecked = 0xE116, siRadio = 0xE117,
    siRadioSelected = 0xE118, siScrollUp = 0xE119, siScrollDown = 0xE11A, siScrollLeft = 0xE11B,
    siScrollRight = 0xE11C, siComboArrow = 0xE11D, siResizeGrip = 0xE11E, siSubmenuArrow = 0xE11F,
    siFolder = 0xE120, siDocument = 0xE121, siFloppy = 0xE122, siHourglass = 0xE123, siPointer = 0xE124,
    siGear = 0xE125, siSearch = 0xE126, siTrash = 0xE127, siWindow = 0xE128, siTerminal = 0xE129,
    siInfo = 0xE12A, siQuestion = 0xE12B, siError = 0xE12C, siProgramGroup = 0xE12D, siNimCrown = 0xE12E,
    # ornaments and wayfinding pictograms (1.3)
    siCrenellation = 0xE130, siWave = 0xE131, siDhow = 0xE132, siFrankincenseBurner = 0xE133,
    siFort = 0xE134, siPalm = 0xE135, siDallah = 0xE136, siMosque = 0xE137,
    siPort = 0xE138, siAirport = 0xE139, siHospital = 0xE13A, siParking = 0xE13B,
    siSouq = 0xE13C, siRestaurant = 0xE13D, siHotel = 0xE13E, siFuel = 0xE13F,
    siBus = 0xE140, siSun = 0xE141, siBeach = 0xE142, siSindbadShip = 0xE143,
    siToilets = 0xE144, siExit = 0xE145, siPharmacy = 0xE146, siQibla = 0xE147, siTaxi = 0xE148

const
  OmaniRialSign* = "⃄"    ## U+20C4 OMANI RIAL SIGN (Unicode 18)
  SaudiRiyalSign* = "⃁"
  UaeDirhamSign* = "⃃"

proc icon*(i: SuharIcon): string =
  ## The icon as text, to put in any label: `label icon(siFolder) & " Documents"`.
  Rune(ord(i)).toUTF8

proc useSuhar*() =
  ## Suhar as the UI's font.  Raises `FontError` if the toolkit cannot read it.
  setUiFontFile(suharRegular, suharBold, suharItalic, suharBoldItalic)

proc useSuharNaskh*() =
  ## Suhar Naskh (pen-written Arabic, same Latin) as the UI's font.  It has no italics: the uprights are used.
  setUiFontFile(suharNaskhRegular, suharNaskhBold, suharNaskhRegular, suharNaskhBold)

proc useSuharMono*() =
  ## Suhar Mono as the UI's font (code editors, terminals).
  setUiFontFile(suharMonoRegular, suharMonoBold, suharMonoItalic, suharMonoBoldItalic)
