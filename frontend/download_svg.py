import urllib.request
import json
import re

url = "https://raw.githubusercontent.com/KaterinaLoup/undraw-svgs/master/illustrations/undraw_farm_girl_dnpe.svg"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    svg_data = response.read().decode('utf-8')
    with open('d:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/assets/img/illustrations/signin.svg', 'w') as f:
        f.write(svg_data)
    print("Downloaded farm girl SVG!")
except Exception as e:
    print("Failed to download farm girl:", e)

    url2 = "https://raw.githubusercontent.com/KaterinaLoup/undraw-svgs/master/illustrations/undraw_nature_m5ll.svg"
    try:
        req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
        response2 = urllib.request.urlopen(req2)
        svg_data2 = response2.read().decode('utf-8')
        with open('d:/myprojects/AMAS FARM/AMAS-FARM-Management-System/frontend/src/assets/img/illustrations/signin.svg', 'w') as f:
            f.write(svg_data2)
        print("Downloaded nature SVG instead!")
    except Exception as e2:
        print("Failed both.", e2)
