import sys
import datetime
import urllib
from urllib.request import urlopen
from time import sleep
from win10toast import ToastNotifier


SEIZMICINTENSITY = "\\xe9\\x9c\\x87\\xe5\\xba\\xa6"
INFOSTART = "<BR>\\n<BR>\\n<pre>" # Start sign of detailed info
INFOENDS = "</pre>" # End sign of detailed info
SEIZMICMAGNITUDEINFOMARK = "\\xe3\\x83\\x89\\xef\\xbc\\x89\\xe3\\x81\\xaf"
TAB = "\\xe3\\x80\\x80"


# url = "http://www.jma.go.jp/jp/quake/20170921014316395-210137.html"
# url = "http://www.jma.go.jp/jp/quake/20170917070204395-170658.html"

stateName = "Tokyo"
STATENAMEUTF = "\\xe6\\x9d\\xb1\\xe4\\xba\\xac\\xe9\\x83\\xbd" # Tokyo
# cityName = "Tokyo Bunkyo ku"
cityName = "Tokyo Meguro ku"
# CITYNAMEUTF = "\\xe6\\x9d\\xb1\\xe4\\xba\\xac\\xe6\\x96\\x87\\xe4\\xba\\xac\\xe5\\x8c\\xba" # "Tokyo Bunkyo ku"
CITYNAMEUTF = "\\xe6\\x9d\\xb1\\xe4\\xba\\xac\\xe7\\x9b\\xae\\xe9\\xbb\\x92\\xe5\\x8c\\xba" # "Tokyo Meguro ku"
url = "http://www.jma.go.jp/jp/quake/"
refreshTime = 1800
toastDuration = 10

def toastAndPrint(counter, title, content, durat = toastDuration, ifToast = True):
    print("\n***"+title+"***\n"+content)
    print(datetime.datetime.now().ctime())
    print("sleeping", counter, "")
    if ifToast:
        toaster.show_toast(title, content, duration = durat)
    sleep(refreshTime)
    return 1

def Quake():
    html = oldHtml = ""
    counter = 0
    print("Fetching information every " + str(refreshTime) + " seconds for city " + str(cityName) +":")
    while True:
        try:
            with urlopen(url) as response:
                html = str(response.read())
        except urllib.error.URLError:
            counter += toastAndPrint(counter, "No Internet Connection", "", ifToast = False)
            continue

        if html == oldHtml:
            counter += toastAndPrint(counter, "Nothing", "No new quakes.")
            continue

        oldHtml = html

        start = html.index(SEIZMICMAGNITUDEINFOMARK)+36
        seizmicMagnitude = html[start:start+3]

        start = html.index(INFOSTART)
        html = html[start:]
        end = html.index(INFOENDS)
        content = html[:end] # Detailed information about every place.
        
        indexOfState = content.find(STATENAMEUTF) # Start index of the state
        if indexOfState == -1:
            counter += toastAndPrint(counter, "Earthquake", "Magnitude " + seizmicMagnitude + " earthquake, " + stateName + " uninfluenced.")
            continue

        # SI valid for Tokyo
        infoAboutState = content[indexOfState:]
        for i in range(len(infoAboutState)):
            if infoAboutState[i] == "n" and infoAboutState[i-1] == "\\":
                if(infoAboutState[i+1:i+13] != TAB): # If it goes to another state(No Tab exists)
                    break
        infoAboutState = infoAboutState[:i-1]
        # Tokyo Only

        start = infoAboutState.find(CITYNAMEUTF) # where the city exists
        if start == -1:
            counter += toastAndPrint(counter, "Earthquake", "Magnitude " + seizmicMagnitude + " earthquake, " + cityName + " senses no intensity.")
            continue
        
        while start > 0:
            if infoAboutState[start:start+24] == SEIZMICINTENSITY:
                seizmicIntensityCity = infoAboutState[start+24:start+36]
                break
            start -= 1
        SIDigitCity = seizmicIntensityCity[-1]
            
        print("SIDigitCity = ", SIDigitCity)
        counter += toastAndPrint(counter, "Earthquake!", "Magnitude " + seizmicMagnitude + " earthquake, " + cityName + " senses intensity level " + SIDigitCity)

if len(sys.argv) == 2:
    refreshTime = sys.argv[1]
toaster = ToastNotifier()
Quake()