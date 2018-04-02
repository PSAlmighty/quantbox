#!/usr/bin/python

import logging
from kiteconnect import KiteConnect, KiteTicker
import constants as const
import sys
import os
import utils
import ConfigParser
import time
import kite_utils

################################################################################
################################################################################
def check_if_doji(ohlc):
    if (float(ohlc['open']) > float(ohlc['close'])):
        diff = float(float(ohlc['open']) -float(ohlc['close']))
    else:
        diff = float(float(ohlc['close']) -float(ohlc['open']))

    if float(diff) < (float(ohlc['open']) * 0.0051):
        return const.DOJI
