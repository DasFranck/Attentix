#!/usr/bin/env python3

import datetime
import json
import logging
import os
import time

from dateutil import tz


import holidays
import pyowm
import requests


class ContextGetter():
    HEADERS = { "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Redmi 3S MIUI/8.9.6)" }
    FRENCH_VACATION_URL = "https://www.data.gouv.fr/fr/datasets/r/000ae493-9fa8-4088-9f53-76d375204036"
    CALENDAR_JSON_PATH =  "data/calendar.json"
    DAY_TYPES_JSON_PATH = "data/day_types.json"

    local_now = None
    now = None
    owm = None
    weather = None

    def __init__(self, now):
        """
        now must be UTC time!
        """

        self.now = now
        self.local_now = now.astimezone(tz.gettz("Europe/Paris"))
        self._init_owm()

    def _init_owm(self, owm_api_key=None):
        if not owm_api_key:
            owm_api_key = os.getenv("OWM_API_KEY")
        self.owm = pyowm.OWM(API_key=owm_api_key, version="2.5")
        self.weather = self.owm.weather_at_coords(49.135143, 2.565823).get_weather()

    def get_holidays(self, date=None):
        """
        Return a dict with every Holidays at the date passed in parameters.
        If no parameter is passed, the function default to today's date.

        Expected argument type: datetime.date
        """

        if not date:
            date = self.local_now.date()

        holidays_today = {
            "French Holiday A Zone": False,
            "French Holiday B Zone": False,
            "French Holiday C Zone": False
        }

        holidays_today["French Public Holiday"] = True if date in holidays.France() else False

        # Get french public holidays per zone
        holidays_dict = requests.get(self.FRENCH_VACATION_URL, headers=self.HEADERS).json()
        holidays_dict = [holidays_item["fields"] for holidays_item in holidays_dict if "Zone" in holidays_item["fields"]["zones"]]
        for holidays_period in holidays_dict:
            if datetime.date.fromisoformat(holidays_period["start_date"]) <= date < datetime.date.fromisoformat(holidays_period["end_date"]):
                for zone in ("A", "B", "C"):
                    if zone in holidays_period["zones"]:
                        holidays_today[f"French Holiday {zone} Zone"] = True

        return holidays_today

    def get_context(self):
        if self.weather.get_sunrise_time() < self.now.timestamp() and self.weather.get_sunset_time() > self.now.timestamp():
            daytime = True
        elif self.weather.get_sunrise_time() > self.now.timestamp() or self.weather.get_sunset_time() < self.now.timestamp():
            daytime = False
        else:
            raise Exception

        return {
            "Holidays": self.get_holidays(),
            "WeatherCode": self.weather.get_weather_code(),
            "Daytime": daytime,
            "Temperature": self.weather.get_temperature("celsius")["temp"]
        }

    def _get_day_info(self):
        """
        A = 10h - 18h
        B = 10h - 18h
        C = 10h - 22h
        D = X
        E = 9h - 18h puis 19h - 01h
        F = 10h - 22h
        G = 11h-18h
        """
        with open(self.CALENDAR_JSON_PATH) as calendar_file:
            calendar = json.load(calendar_file)

        target_date = self.local_now.date()
        target_time = self.local_now.time()

        previous_calendar_day = calendar[str(target_date - datetime.timedelta(days=1))]
        calendar_day = calendar[str(target_date)]
        # next_calendar_day = calendar[str(target_date + datetime.timedelta(days=1))]

        # Weird piece code due to weird data
        is_open = False
        if target_time <= datetime.time(1, 0):
            day_type = previous_calendar_day["type"] 
            if day_type == "E": 
                is_open = True
        else:
            day_type = calendar_day["type"]
            if day_type == "A" or day_type == "B":
                if datetime.time(10, 0) <= target_time and target_time <= datetime.time(18, 0):
                    is_open = True

            elif day_type == "C" or day_type == "E":
                if datetime.time(10, 0) <= target_time and target_time <= datetime.time(22, 0):
                    is_open = True

            elif day_type == "D":
                pass

            elif day_type == "E":
                if datetime.time(9, 0) <= target_time and target_time <= datetime.time(18, 0) or datetime.time(19, 0) <= target_time:
                    is_open = True

            elif day_type == "G":
                if datetime.time(11, 0) <= target_time and target_time <= datetime.time(18, 0):
                    is_open = True

            else:
                logging.critical(f"Day Type UNKNOWN: {day_type}")

        return is_open, day_type

    def is_the_park_open(self):
        return self._get_day_info()[0]

    def get_day_type(self):
        with open(self.DAY_TYPES_JSON_PATH) as day_types_file:
            day_types = json.load(day_types_file)
        
        return day_types[self._get_day_info()[1]]

if __name__ == "__main__":
    from pprint import pprint

    now = datetime.datetime.now(tz.tzutc())
    cg = ContextGetter(now)
    pprint(cg.get_context())
