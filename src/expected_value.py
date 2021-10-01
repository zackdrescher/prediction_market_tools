#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

import itertools


def prep_prices_csv(p):

    p[["yesPrice", "noPrice", "myBet"]] = p[["yesPrice", "noPrice", "myBet"]] / 100
    p["symbol"] = p["symbol"].str.upper()
    p.date = pd.to_datetime(p.date, format="%Y%m%d")
    p['age'] = pd.to_datetime("today") - p.date

    p_bet = p[~p.myBet.isna()]
    idx = p_bet.groupby(["symbol"])["date"].transform(max) == p_bet["date"]
    latest_p = p_bet[idx]

    latest_p["buyYes"] = latest_p.myBet > latest_p.yesPrice

    def get_probs(row):
        if row.buyYes:
            return [row.yesPrice, row.myBet]
        else:
            return [row.noPrice, 1 - row.myBet]

    latest_p[["mktp", "myp"]] = latest_p.apply(get_probs, axis=1, result_type="expand")
    latest_p[["mktq", "myq"]] = 1 - latest_p[["mktp", "myp"]]

    latest_p["expected_value"] = (latest_p.myp * latest_p.mktq) - (
        latest_p.myq * latest_p.mktp
    )

    return p, latest_p


def compute_situation_expectations(ps, qs, prices, pays, n_hits):
    p_ix = np.arange(len(ps))
    flip_mask = np.stack(
        [np.isin(p_ix, i) for i in itertools.combinations(p_ix, n_hits)]
    )

    bet_ps = np.where(flip_mask, ps, qs)
    bet_pays = np.where(flip_mask, pays, -prices)

    outcome_ps = bet_ps.prod(axis=1)
    situation_p = outcome_ps.sum()
    outcome_pays = bet_pays.sum(axis=1)

    sit_outcome_ps = outcome_ps / situation_p

    situation_exp = (outcome_pays * sit_outcome_ps).sum()

    return situation_p, situation_exp


def compute_wager_expectations(proababilities, prices, qtys):

    qs = 1 - proababilities
    payouts = qtys - prices

    situations = []

    for i in range(len(proababilities) + 1):
        situation_p, situation_exp = compute_situation_expectations(
            proababilities, qs, prices, payouts, i
        )
        situations.append(
            dict(
                hits=i,
                hit_percent=i / len(proababilities),
                hits_p=situation_p,
                hits_exp=situation_exp,
            )
        )

    situations = pd.DataFrame.from_records(situations)

    expected_value = (situations.hits_p * situations.hits_exp).sum()

    return expected_value, situations
