#!/usr/bin/env python
# coding: utf-8

import os

from dotenv import load_dotenv
import requests
import pandas as pd


def merge_bets_into_postions(positions, bets):

    positions = positions.merge(
        bets[["symbol", "myBet"]],
        how="left",
        left_on="ticker_name",
        right_on="symbol",
    )
    positions["myBet"] = positions.myBet.where(
        positions.position > 0, 1 - positions.myBet
    )

    return positions


def prep_market_columns(markets):

    price_col = [
        "yes_bid",
        "yes_ask",
        "last_price",
        "previous_yes_bid",
        "previous_yes_ask",
        "previous_price",
    ]
    markets[price_col] = markets[price_col] / 100
    markets["no_ask"] = 1 - markets.yes_bid

    return markets


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
            df = pd.DataFrame.from_records(data["market_positions"])
            df["qty"] = df.position.where(df.position > 0, -df.position)
            df.position_cost = df.position_cost / 100
            return df
        else:
            return data

    def get_trades(self):

        r = self.sess.get(f"{self.url}users/{self.auth['user_id']}/trades")

        data = r.json()
        if self.pandas:
            return pd.DataFrame.from_records(data["trades"])
        else:
            return data

    def get_market(self, market_id):

        r = self.sess.get(f"{self.url}markets/{market_id}")

        return r.json()

    def get_market_by_ticker(self, ticker):

        r = self.sess.get(f"{self.url}markets_by_ticker/{ticker}")

        return r.json()

    def select_markets_by_ticker(self, tickers):

        out = [self.get_market_by_ticker(ticker)["market"] for ticker in tickers]

        if self.pandas:
            df = pd.DataFrame.from_records(out)
            df = prep_market_columns(df)
            return df
        else:
            return out

    def select_markets(self, market_ids):

        out = [self.get_market(market_id)["market"] for market_id in market_ids]

        if self.pandas:
            df = pd.DataFrame.from_records(out)
            df = prep_market_columns(df)
            return df
        else:
            return out

    def get_open_positions(self):

        positions = self.get_positions()
        markets = self.select_markets(positions.market_id)

        positions = positions.merge(
            markets[["id", "ticker_name", "last_price", "status"]],
            how="left",
            left_on="market_id",
            right_on="id",
        )
        positions = positions[positions.status == "active"]
        positions["mrkt_prob"] = positions.last_price.where(
            positions.position > 0, 1 - positions.last_price
        )

        return positions
