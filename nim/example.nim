## nim c -r -d:release -d:useMalloc example.nim
import retroui, suhar

var name = "صُحار"
var mono = false

app "Suhar", 420, 220:
  if checkbox("Mono&spaced", mono):
    if mono: useSuharMono() else: useSuhar()
  heading "Suhar — صُحار"
  row([70, -1]):
    label "&Name:"
    edit name
  label icon(siFolder) & " Documents   " & icon(siFloppy) & " Save   " & icon(siOmanEmblem)
  label "Price: 2.500 " & OmaniRialSign
  row:
    spring()
    if button("&Close", isDefault = true): quitApp()
