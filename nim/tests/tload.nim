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
echo "ok sans=", sans, " arabic=", ar, " bold=", bold, " mono10=", m1, " (builtin=", before, ")"
