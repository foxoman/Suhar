## A two-language app with Suhar as its font.
##   nim c -r -d:release -d:useMalloc example_app.nim
##   retroapk example_app.nim --name:"Suhar Demo" --id:net.foxoman.suhardemo      # Android
import retroui, suhar

var arabic = true
var name = ""
var count = 3
var reading = false

proc tr(ar, en: string): string =
  if arabic: ar else: en

useSuharApp()
setRtlInterface(arabic)

app "Suhar", 380, 300:
  row:
    if button(tr("English", "العربية")):
      arabic = not arabic
      setRtlInterface(arabic)
    if checkbox(tr("خط القراءة", "Reading font"), reading):
      if reading: useSuharRead() else: useSuharApp()
  heading tr("مرحباً بكم في صُحار", "Welcome to Sohar")
  form(90):
    field(tr("الاسم:", "Name:")):
      edit name
    field(tr("العدد:", "Count:")):
      spin count, 0, 99
  paragraph tr("تقع صُحار على ساحل بحر عُمان، على بعد 240 كم من مسقط، وكانت من أهم موانئ المنطقة.",
               "Sohar lies on the Sea of Oman, 240 km from Muscat, and was once among the busiest ports of the region.")
  label icon(siPort) & "  " & tr("الإجمالي: ", "Total: ") & $(count * 2500) & " " & OmaniRialSign
  row:
    spring()
    if button(tr("إغلاق", "Close"), isDefault = true): quitApp()
