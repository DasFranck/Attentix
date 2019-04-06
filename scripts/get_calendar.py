from datetime import datetime
import json
import requests

from pprint import pprint

CALENDAR_URL = "https://www.parcasterix.fr/webservices/03/fr?device=android&version=320&apiversion=1&lang=fr"
HEADERS = { "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Redmi 3S MIUI/8.9.6)" }

calendar = requests.get(CALENDAR_URL, headers=HEADERS).json()["agenda"]
calendar_formatted = {
                        str(datetime.strptime(item["jour"], "%d-%m-%Y").date()): {"horaire": item["horaire"],
                                                                      "type": item["type"]}
                        for item in calendar}

pprint(calendar_formatted)