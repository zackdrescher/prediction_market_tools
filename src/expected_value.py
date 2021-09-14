#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np

import itertools

def prep_prices_csv(p):

    p[['yesPrice', 'noPrice', 'myBet']] = p[['yesPrice', 'noPrice', 'myBet']] / 100
    p.date = pd.to_datetime(p.date, format='%Y%m%d')

    idx = p.groupby(['symbol'])['date'].transform(max) == p['date']
    latest_p = p[idx]
    latest_p = latest_p[~latest_p.myBet.isna()]

    latest_p['buyYes'] = latest_p.myBet > latest_p.yesPrice

    def get_probs(row):
        if row.buyYes:
            return [row.yesPrice, row.myBet]
        else:
            return [row.noPrice, 1 - row.myBet]

    latest_p[['mktp', 'myp']] = latest_p.apply(get_probs, axis=1, result_type='expand')
    latest_p[['mktq', 'myq']] = 1 - latest_p[['mktp', 'myp']]

    latest_p['expected_value'] = (latest_p.myp * latest_p.mktq) - (latest_p.myq * latest_p.mktp)

    return p, latest_p

def compute_situation_expectations(ps, qs, prices, pays, bet_weights, n_hits):
    p_ix = np.arange(len(ps))
    flip_mask = np.stack([np.isin(p_ix, i) for i in itertools.combinations(p_ix, n_hits)])
    
    bet_ps = np.where(flip_mask, ps, qs)
    bet_pays = np.where(flip_mask, pays, -prices)
    
    bet_pays = bet_pays * bet_weights
    
    outcome_ps = bet_ps.prod(axis=1)
    situation_p = outcome_ps.sum()
    outcome_pays = bet_pays.sum(axis=1)
    
    sit_outcome_ps = outcome_ps / situation_p
    
    situation_exp = (outcome_pays * sit_outcome_ps).sum()
    
    return situation_p, situation_exp

def compute_wager_expectations(latest_p):

    shares = np.ones(len(latest_p))

    situations = []

    for i in range(len(latest_p)+1):
        situation_p, situation_exp = compute_situation_expectations(
            latest_p.myp.values, latest_p.myq.values, latest_p.mktq.values, latest_p.mktp.values, shares, i)
        situations.append(
            dict(
                hits=i,
                hit_percent = i / len(latest_p),
                hits_p = situation_p,
                hits_exp = situation_exp
            )
        )

    situations = pd.DataFrame.from_records(situations)

    expected_value = (situations.hits_p * situations.hits_exp).sum()

    return expected_value, situations
