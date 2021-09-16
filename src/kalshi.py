#!/usr/bin/env python
# coding: utf-8

import os

from dotenv import load_dotenv
import requests
import pandas as pd


class Kalshi:

    config_keys = ["KALSHI_EMAIL", "KALSHI_PASSWORD"]

    def __init__(self, url="https://trading-api.kalshi.com/v1/", pandas=True):

        self.url = url
        self.get_config()
        self.make_session()
        self.pandas = pandas

    def get_config(self):

        load_dotenv()
        self.config = {key: os.environ[key] for key in Kalshi.config_keys}

    def make_session(self):

        self.sess = requests.Session()
        self.sess.headers.update({"Content-Type": "application/json"})

    def login(self):
        payload = dict(
            email=self.config["KALSHI_EMAIL"], password=self.config["KALSHI_PASSWORD"]
        )

        r = self.sess.post(f"{self.url}log_in", json=payload)

        self.auth = r.json()
        self.sess.headers.update({"Authorization": self.auth["token"]})

    def get_positions(self):

        r = self.sess.get(f"{self.url}users/{self.auth['user_id']}/positions")

        data = r.json()
        if self.pandas:
            return pd.DataFrame.from_records(data["market_positions"])
        else:
            return data

    def get_trades(self):

        r = self.sess.get(f"{self.url}users/{self.auth['user_id']}/trades")

        data = r.json()
        if self.pandas:
            return pd.DataFrame.from_records(data["trades"])
        else:
            return data
