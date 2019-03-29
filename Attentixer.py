import csv
import locale
import os
import requests

import holidays
import pyowm

from collections import OrderedDict
from datetime import datetime, date
from pprint import  pprint

ATTRACTION_LIST = {
 '11': 'Goudurix',
 '12': 'La Trace du Hourra',
 '13': 'Les Petits Drakkars',
 '25': 'Oziris',
 '68': 'Le Défi de César',
 '70': 'SOS Numérobis',
 '613': 'Les Chevaux du Roy',
 '616': 'Le Carrousel de César',
 '619': 'Les Espions de César',
 '622': 'Epidemaïs Croisière',
 '625': "La Rivière d'Elis",
 '628': 'Nationale 7',
 '631': 'La Petite Tempête',
 '636': "Le Vol d'Icare",
 '639': "L'Hydre de Lerne",
 '642': 'Le Transdemonium',
 '645': "L'Oxygénarium",
 '648': 'Les Chaudrons',
 '658': 'Le Cheval de Troie',
 '661': 'La Galère',
 '664': 'Les Chaises Volantes',
 '667': 'Le Petit Train',
 '670': 'Les Petites Chaises Volantes',
 '673': "L'Escadrille des As",
 '676': 'Le Mini Carrousel',
 '679': 'Les Petits Chars tamponneurs',
 '2482': 'Enigmatix',
 '2483': 'Aérodynamix',
 '2484': 'Lavomatix',
 '2485': 'Hydrolix',
 '2486': 'Etamine',
 '63760': 'Discobélix',
 '92214': 'Pégase Express',
 '113319': 'Mission perdue'
}

ATTRACTION_LIST_ORDERED = OrderedDict(sorted(ATTRACTION_LIST.items(), key=lambda t: t[0]))

HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Redmi 3S MIUI/8.9.6)"
}

ATTRACTION_URL = "https://www.parcasterix.fr/webservices/api/attractions.json?device=android&version=320&apiversion=1&lang=fr"
ATTENTIX_URL = "https://www.parcasterix.fr/webservices/api/attentix.json?device=android&version=320&apiversion=1&lang=fr"
FRENCH_VACATION_URL = "https://www.data.gouv.fr/fr/datasets/r/000ae493-9fa8-4088-9f53-76d375204036"

def get_holidays(today_date):
    if today_date in holidays.France():
        return "Férié"
    else:
        holidays_check = {"A": False, "B": False, "C": False}
        holidays_dict = requests.get(FRENCH_VACATION_URL, headers=HEADERS).json()
        holidays_dict = [holidays_item["fields"] for holidays_item in holidays_dict if "Zone" in holidays_item["fields"]["zones"]]
        for holidays_period in holidays_dict:
            if date.fromisoformat(holidays_period["start_date"]) <= today_date < date.fromisoformat(holidays_period["end_date"]):
                for zone in ("A", "B", "C"):
                    if zone in holidays_period["zones"]:
                        holidays_check[zone] = True
        return ",".join([zone[0] for zone in holidays_check.items() if zone[1]])

def check_integrity():
    attraction_response = requests.get(ATTRACTION_URL, headers=HEADERS).json()["result"]["attractions"]
    for item in attraction_response:
        if item["code"] in ATTRACTION_LIST_ORDERED:
            if ATTRACTION_LIST_ORDERED[item["code"]].lower() != item["title"].lower():
                print(f"Attraction name doesn't march in {item['code']}")


def main():
    owm = pyowm.OWM(API_key='9191a5ce1f1716d8c08bd07d9230fae3', language="fr")
    weather = owm.weather_at_coords(49.135143, 2.565823).get_weather()
    check_integrity()

    attentix_dict = OrderedDict()
    attentix_response = requests.get(ATTENTIX_URL, headers=HEADERS).json()["latency"]["latency"]

    for item in ATTRACTION_LIST_ORDERED.items():
        attraction = next(attentix_item for attentix_item in attentix_response if attentix_item["attractionid"] == item[0])
        try:
            attentix_dict[item[1]] = int(attraction["latency"])
        except:
#            print(f"Can't translate {attraction['latency'] if 'latency' in attraction else 'NOTHING'}")
            attentix_dict[item[1]] = None

    fieldnames = ["Date", "Weekday", "Holidays", "Weather", "Temperature"] + [item[0] for item in attentix_dict.items()]

    locale.setlocale(category=locale.LC_ALL, locale="French")

    attentix_dict["Date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    attentix_dict["Weekday"] = datetime.now().strftime("%A")
    attentix_dict["Weather"] = weather.get_detailed_status()
    attentix_dict["Temperature"] = weather.get_temperature("celsius")["temp"]   
    attentix_dict["Holidays"] = get_holidays(date.today())

    if not os.path.exists("attentixer.csv"):
        with open("attentixer.csv", mode='w', encoding="utf-8", newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(attentix_dict)
    else:
        with open("attentixer.csv", mode='a', encoding="utf-8", newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow(attentix_dict)

if __name__ == "__main__":
    main()