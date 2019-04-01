#!/usr/bin/env python3

import datetime
import json
import logging
import requests

from collections import OrderedDict


class WaitingTimeGetter:
    ATTRACTION_URL = "https://www.parcasterix.fr/webservices/api/attractions.json?device=android&version=320&apiversion=1&lang=fr"
    ATTENTIX_URL = "https://www.parcasterix.fr/webservices/api/attentix.json?device=android&version=320&apiversion=1&lang=fr"
    HEADERS = { "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Redmi 3S MIUI/8.9.6)" }

    attraction_list = {}

    def __init__(self):
        self._get_attraction_list()
        self._check_attractions()

    def _check_attractions(self):
        attraction_response = requests.get(self.ATTRACTION_URL, headers=self.HEADERS).json()["result"]["attractions"]
        for item in attraction_response:
            if item["code"] in self.attractions:
                if self.attractions[item["code"]].lower() != item["title"].lower():
                    logging.warning(f"Attraction name doesn't match {item['code']}\nPlease check if attractions have been modified.")

    def _get_attraction_list(self):
        with open("attractions.json") as attractions_file:
            attractions = json.load(attractions_file)
            self.attractions = OrderedDict(sorted(attractions.items(), key=lambda t: t[0]))

    def get_attraction_list(self):
        return self.attraction_list

    def get_waiting_time(self):
        waiting_time_dict = OrderedDict()
        api_response = requests.get(self.ATTENTIX_URL, headers=self.HEADERS).json()["latency"]["latency"]

        for item in self.attractions.items():
            attraction = next(waiting_time for waiting_time in api_response if waiting_time["attractionid"] == item[0])
            try:
                waiting_time_dict[item[1]] = int(attraction["latency"])
            except (ValueError, KeyError):
                logging.debug(f"Can't translate \"{attraction['latency'] if 'latency' in attraction else 'NONE'}\"")
                waiting_time_dict[item[1]] = None

        return waiting_time_dict


if __name__ == "__main__":
    from pprint import pprint
    wtg = WaitingTimeGetter()
    pprint(wtg.get_waiting_time())