#!/usr/bin/env python3

import datetime
import os
import time

import holidays
import pyowm
import requests


class ContextGetter():
    HEADERS = { "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Redmi 3S MIUI/8.9.6)" }
    FRENCH_VACATION_URL = "https://www.data.gouv.fr/fr/datasets/r/000ae493-9fa8-4088-9f53-76d375204036"

    owm = None
    weather = None

    def __init__(self):
        self._init_owm()

    def _init_owm(self, owm_api_key=None):
        if not owm_api_key:
            owm_api_key = os.getenv("OWM_API_KEY")
        self.owm = pyowm.OWM(API_key=owm_api_key, version="2.5")
        self.weather = self.owm.weather_at_coords(49.135143, 2.565823).get_weather()

    def get_holidays(self, date=datetime.date.today()):
        """
        Return a dict with every Holidays at the date passed in parameters.
        If no parameter is passed, the function default to today's date.

        Expected argument type: datetime.date
        """
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
        timestamp_now = time.time()
        if self.weather.get_sunrise_time() < timestamp_now and self.weather.get_sunset_time() > timestamp_now:
            daytime = True
        elif self.weather.get_sunrise_time() > timestamp_now or self.weather.get_sunset_time() < timestamp_now:
            daytime = False
        else:
            raise Exception

        return {
            "Holidays": self.get_holidays(),
            "WeatherCode": self.weather.get_weather_code(),
            "Daytime": daytime,
            "Temperature": self.weather.get_temperature("celsius")["temp"]
        }

if __name__ == "__main__":
    from pprint import pprint
    cg = ContextGetter()
    pprint(cg.get_context())
