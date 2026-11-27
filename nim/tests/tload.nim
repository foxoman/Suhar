## Headless check: the toolkit's own TrueType reader accepts every Suhar
## style and measures Latin and Arabic text with it.
import std/os
import retroui
import ../suhar
import harness

fakeDriver()
let before = textWidth("Suhar Hamburgefonstiv")
useSuhar()
let sans = textWidth("Suhar Hamburgefonstiv")
let ar = textWidth("مرحباً بكم في صحار")
let bold = textWidth("Suhar Hamburgefonstiv", bold = true)
doAssert sans > 0 and ar > 0, "no width measured"
doAssert sans != before, "the UI font did not change"
doAssert bold >= sans, "bold is not wider or equal"
useSuharMono()
let m1 = textWidth("iiiiiiiiii")
let m2 = textWidth("MMMMMMMMMM")
doAssert m1 == m2 and m1 > 0, "Suhar Mono is not monospaced in the toolkit: " & $m1 & " " & $m2
doAssert icon(siFolder).len == 3
useSuhar()
let fullAr = textWidth("مرحباً بكم في صحار")
let fullMix = textWidth("Total: 2.500 ر.ع. — 0123456789")
useSuharApp()
let appAr = textWidth("مرحباً بكم في صحار")
doAssert appAr == fullAr, "the app font measures Arabic differently from the release font: " & $appAr & " " & $fullAr
doAssert textWidth("Total: 2.500 ر.ع. — 0123456789") == fullMix, "the app font measures mixed text differently"
doAssert textWidth("1111111111") == textWidth("8888888888"), "digits are not of one width"
doAssert textWidth("Ελληνικά Русский فارسی اردو") > 0
doAssert icon(siFolder).len == 3 and textWidth(icon(siFolder)) > 0
useSuharRead()
doAssert textWidth("مرحباً بكم في صحار") > 0 and textWidth("مرحباً بكم في صحار") != appAr, "the reading font is not in use"
useSuharApp()
echo "ok app=", appAr, " sans=", sans, " arabic=", ar, " bold=", bold, " mono10=", m1, " (builtin=", before, ")"
