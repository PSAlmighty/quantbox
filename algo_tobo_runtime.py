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
import patterns

fno_dict = {}
base_dict = {}
config_dict = {}
orders = {}
scrip_map = {}
NO_OF_PARAMS = 2
sub_list = []
order_dict = {}
my_orders = []
# This is index into 
SCRIP_ID    = 0
ACTION_ID   = 1
TRIGGER_ID  = 2
PRICE_ID    = 3
TARGET_ID   = 4
STOPLOSS_ID = 5
LIVE_PRICE_ID = 6

################################################################################
################################################################################
def main():
    print "Main"
    global kite
    global fno_dict, base_dict, config_dict, orders
    global scrip_map, sub_list
    global order_dict
    global fno_mapping
    global order_dict
    #TODO: Add argparser for validating input

    # read config file
    config_dict = utils.read_config_file()

    # get list of fno
    fno_dict = utils.get_fno_dict()
    
    #get kite object
    api_key, access_token, kite = kite_utils.login_kite(None)

    # get instrument list, create quote subscription list and 
    # mapping between instrument token and tradingsymbol
    quote_list = []
    data = kite.instruments("NSE")
    for each in fno_dict:
        for instrument in data:
            if each == instrument['tradingsymbol']:
                entry = "NSE:" + str(instrument['tradingsymbol'])
                quote_list.append(entry)
                # sub list for subscribing to the quotes
                sub_list.append(int(instrument['instrument_token']))
                #mapping dictionary for token and trading symbol
                scrip_map[int(instrument['instrument_token'])] = str(instrument['tradingsymbol'])
    
    
    # Generate order file
    count = int(0)
    quotes = kite.quote(quote_list)
    for each in quotes:
        scrip = each.split(":")[1].strip("\n")
        if scrip not in fno_dict:
            continue
        if float(quotes[each]["ohlc"]["open"]) < float(config_dict['start_price']):
            continue
        
        if float(quotes[each]["ohlc"]["open"]) > float(config_dict['end_price']):
            continue
        count = int(count) + int(1);

        if quotes[each]['ohlc']['open'] == quotes[each]['ohlc']['low']:
            diff = float(quotes[each]['ohlc']['high'])-float(quotes[each]['ohlc']['low'])
            percentage = float(quotes[each]['ohlc']['open']) * float(0.007)
            if float(percentage) < float(diff):
                print each 
                
        if quotes[each]['ohlc']['open'] == quotes[each]['ohlc']['high']:
            diff = float(quotes[each]['ohlc']['high'])-float(quotes[each]['ohlc']['low'])
            percentage = float(quotes[each]['ohlc']['open']) * float(0.007)
            if float(percentage) < float(diff):
                print each 

        
################################################################################
if __name__ == "__main__":
    main()
