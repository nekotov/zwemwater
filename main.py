import json
import time
import requests
import simplekml
import threading

kml = simplekml.Kml()
kml.document.name = "Zwemwater"

def dataById(id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0  uacq',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.zwemwater.nl/',
        'Origin': 'https://www.zwemwater.nl',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'Sec-GPC': '1',
        'Content-Type': 'text/xml',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': '"Edge";v="114", "Chromium";v="114", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }

    data = f'<GetFeature xmlns="http://www.opengis.net/wfs" service="WFS" version="1.1.0" outputFormat="application/json" xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.0/wfs.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Query typeName="zwr_public:zwemplekken_details" srsName="EPSG:28992" xmlns:zwr_public="https://pubgeo.zwemwater.nl/geoserver/zwr_public"><Filter xmlns="http://www.opengis.net/ogc"><PropertyIsEqualTo><PropertyName>key_id</PropertyName><Literal>{id}</Literal></PropertyIsEqualTo></Filter></Query></GetFeature>'

    return requests.post('https://pubgeo.zwemwater.nl/geoserver/zwr_public/wfs', headers=headers, data=data).text

def signs(id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0  uacq',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'text/xml',
        'Origin': 'https://www.zwemwater.nl',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://www.zwemwater.nl/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': '"Edge";v="114", "Chromium";v="114", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'Sec-GPC': '1',
    }

    data = f'<GetFeature xmlns="http://www.opengis.net/wfs" service="WFS" version="1.1.0" outputFormat="application/json" xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.0/wfs.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Query typeName="zwr_public:zwemplek_voorziening" srsName="EPSG:28992" xmlns:zwr_public="https://pubgeo.zwemwater.nl/geoserver/zwr_public"><Filter xmlns="http://www.opengis.net/ogc"><And><Or><PropertyIsEqualTo><PropertyName>taal</PropertyName><Literal>nl</Literal></PropertyIsEqualTo><PropertyIsNull><PropertyName>taal</PropertyName></PropertyIsNull></Or><PropertyIsEqualTo><PropertyName>zwemplek_id</PropertyName><Literal>{id}</Literal></PropertyIsEqualTo><PropertyIsNotEqualTo><PropertyName>groep</PropertyName><Literal>qwerty</Literal></PropertyIsNotEqualTo></And></Filter></Query></GetFeature>'

    return requests.post('https://pubgeo.zwemwater.nl/geoserver/zwr_public/wfs', headers=headers, data=data).text

data = requests.get("https://legacy.waterschapp.nl/zwemwater/zwemplekken_for_map.php").json()


def get_data(i):
    point = kml.newpoint()
    point.coords = [(i["coords"][0],i["coords"][1])]
    point.name = i["name"]
    info = json.loads(dataById(i["id"]))["features"][0]['properties']
    point.description = ""
    point.description += "status: " + info['status'] + "\n" # ['WAARSCHUWING', 'goed', 'ZWEMVERBOD', 'NEGATIEF_ZWEMADVIES']
    if type(info['toegang']) != str:
        point.description += "toegang: " + "onbekend" + "\n"
    else:
        point.description += "toegang: " + info['toegang'] + "\n"
    point.description += "tekst: " + info['tekst'] + "\n\n"
    point.description += "image: " + "https://register.zwemwater.nl/zwr/api/files/" + str(info['info_id']) + "\n\n"
    sign = json.loads(signs(i["id"]))["features"]
    for x in sign:
        x = x['properties']
        if x['aanvulling']:
            point.description += "sign: " + x['aanvulling'] + "\n"
        point.description += "omschrijving : " + x['omschrijving'] + "\n"


def train():
    maximum = 250
    threads = []
    for i in range(0, len(data), maximum):
        print(len(data), i)
        for x in data[i:i + maximum]:
            t = threading.Thread(target=get_data, args=(x,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        threads = []
        time.sleep(1)

if __name__ == '__main__':
    train()

kml.save("Zwemwater.kml")
kml.savekmz("Zwemwater.kmz")
