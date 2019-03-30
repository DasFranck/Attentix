#!/usr/bin/env python3

import csv
import locale
import json
import os
import requests

import holidays
import pyowm

from collections import OrderedDict
from datetime import datetime, date


class WaitingTimeGetter:
    ATTRACTION_URL = "https://www.parcasterix.fr/webservices/api/attractions.json?device=android&version=320&apiversion=1&lang=fr"
    ATTENTIX_URL = "https://www.parcasterix.fr/webservices/api/attentix.json?device=android&version=320&apiversion=1&lang=fr"
    FRENCH_VACATION_URL = "https://www.data.gouv.fr/fr/datasets/r/000ae493-9fa8-4088-9f53-76d375204036"
    HEADERS = { "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Redmi 3S MIUI/8.9.6)" }

    owm = None
    weather = None
    attractions = {}

    def __init__(self):
        self.init_owm()
        self.get_attractions()
        self.check_attractions()

    def init_owm(self):
        self.owm = pyowm.OWM(API_key=os.getenv("OWM_API_KEY"), version="2.5")
        self.weather = self.owm.weather_at_coords(49.135143, 2.565823).get_weather()

    def get_attractions(self):
        with open("attractions.json") as attractions_file:
            attractions = json.load(attractions_file)
            self.attractions = OrderedDict(sorted(attractions.items(), key=lambda t: t[0]))

    def get_today_holidays(self):
        today_date = date.today()

        holidays_today = {
            "French Holiday A Zone": False, 
            "French Holiday B Zone": False,
            "French Holiday C Zone": False
        }

        holidays_today["French Public Holiday"] = True if today_date in holidays.France() else False

        # Get french public holidays per zone
        holidays_dict = requests.get(self.FRENCH_VACATION_URL, headers=self.HEADERS).json()
        holidays_dict = [holidays_item["fields"] for holidays_item in holidays_dict if "Zone" in holidays_item["fields"]["zones"]]
        for holidays_period in holidays_dict:
            if date.fromisoformat(holidays_period["start_date"]) <= today_date < date.fromisoformat(holidays_period["end_date"]):
                for zone in ("A", "B", "C"):
                    if zone in holidays_period["zones"]:
                        holidays_today[f"French Holiday {zone} Zone"] = True
                    
        return holidays_today

    def check_attractions(self):
        attraction_response = requests.get(self.ATTRACTION_URL, headers=self.HEADERS).json()["result"]["attractions"]
        for item in attraction_response:
            if item["code"] in self.attractions:
                if self.attractions[item["code"]].lower() != item["title"].lower():
                    print(f"Attraction name doesn't match {item['code']}\nPlease check if attractions have been modified.")

    def get_waiting_time(self):
        waiting_time_dict = OrderedDict([("WaitingTime", {})])
        api_response = requests.get(self.ATTENTIX_URL, headers=self.HEADERS).json()["latency"]["latency"]

        for item in self.attractions.items():
            attraction = next(waiting_time for waiting_time in api_response if waiting_time["attractionid"] == item[0])
            try:
                waiting_time_dict["WaitingTime"][item[1]] = int(attraction["latency"])
            except (ValueError, KeyError):
        #        print(f"Can't translate \"{attraction['latency'] if 'latency' in attraction else 'NONE'}\"")
                waiting_time_dict["WaitingTime"][item[1]] = None

        # locale.setlocale(category=locale.LC_ALL, locale="French")

        waiting_time_dict["Datetime"] = datetime.now()
        waiting_time_dict["Weather"] = self.weather.get_detailed_status()
        waiting_time_dict["Temperature"] = self.weather.get_temperature("celsius")["temp"]   
        waiting_time_dict["Holidays"] = self.get_today_holidays()

        return waiting_time_dict


if __name__ == "__main__":
    from pprint import  pprint
    wtg = WaitingTimeGetter()
    pprint(wtg.get_waiting_time())