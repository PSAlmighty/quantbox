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


fno_dict = {}
base_dict = {}
config_dict = {}
orders = {}
NO_OF_PARAMS = 2

# This is index into 
SCRIP_ID    = 0
ACTION_ID   = 1
TRIGGER_ID  = 2
PRICE_ID    = 3
TARGET_ID   = 4
STOPLOSS_ID = 5

################################################################################
# Function: check_open_price()
# This function is the crux of this algorithm
# TODO: Write all the cases 
################################################################################
def check_open_price(scrip, ohlc, open_price):

    if float(open_price) > float(ohlc['high']):
        #print scrip, " GAP UP - ignore"
        return const.OPEN_GAP_UP

    if float(open_price) < float(ohlc['low']):
        #print scrip, "GAP DOWN - ignore"
        return const.OPEN_GAP_DOWN

    #green candle
    if float(ohlc['open']) < float(ohlc['close']):

        if ((float(open_price) >= float(ohlc['open'])) and
            (float(open_price) <= float(ohlc['close']))):
            #print scrip, " BETWEEN BODY"
            return const.OPEN_INSIDE_BODY_GREEN
            
        if float(open_price) > float(ohlc['close']):
            #print scrip, " BETWEEN HIGH WICK"
            return const.OPEN_NEAR_HIGH_WICK_GREEN
    
        else:
            return const.OPEN_NEAR_LOW_WICK_GREEN
    #red candle
    else:

        if ((float(open_price) >= float(ohlc['close'])) and
            (float(open_price) <= float(ohlc['open']))):
            #print scrip, " BETWEEN BODY"
            return const.OPEN_INSIDE_BODY_RED
        
        if float(open_price) > float(ohlc['open']):
            #print scrip, " BETWEEN HIGH WICK"
            return const.OPEN_NEAR_HIGH_WICK_RED
    
        else: 
            return const.OPEN_NEAR_LOW_WICK_RED

################################################################################
# Function: get_order_string()
# This function will return the 
################################################################################
def get_order_string(scrip, action, price, stoploss_buy, stoploss_sell):
    outstring = ""
    
    if (price == None):
        return None

    if action == "BUY":
        trigger_price = float(utils.get_floating_value(price)) +  float(0.10)
        price = trigger_price
        target = float(utils.get_floating_value(float(trigger_price) * float(config_dict['target_lock'])))
        if (stoploss_buy == None):
            stoploss = float(utils.get_floating_value(float(trigger_price) * float(config_dict['stoploss_lock'])))
        else:
            stoploss = float(utils.get_floating_value(float(price) - float(stoploss_buy)))
        outstring = scrip + " " + action + " " + str(trigger_price) + " " + str(price) + " " + str(target) + " " + str(stoploss) +"\n"

    if action == "SELL":
        trigger_price = float(utils.get_floating_value(price)) -  float(0.10)
        price = trigger_price
        target = float(utils.get_floating_value(float(trigger_price) * float(config_dict['target_lock'])))
        if (stoploss_sell == None):
            stoploss = float(utils.get_floating_value(float(trigger_price) * float(config_dict['stoploss_lock'])))
        else:
            stoploss = float(utils.get_floating_value(float(stoploss_sell) - float(price)))
        outstring = scrip + " " + action + " " + str(trigger_price) + " " + str(price) + " " + str(target) + " " + str(stoploss) +"\n"

    return outstring


################################################################################
################################################################################
def check_if_doji(ohlc):
    if (float(ohlc['open']) > float(ohlc['close'])):
        diff = float(float(ohlc['open']) -float(ohlc['close']))
    else:
        diff = float(float(ohlc['close']) -float(ohlc['open']))

    if float(diff) < (float(ohlc['open']) * 0.0051):
        return const.DOJI

################################################################################
#
################################################################################
def generate_orders(scrip, ohlc, open_price):
    buy_order = None
    sell_order = None
    #check open price from quote
    ret = check_open_price(scrip, ohlc, open_price)

    if ((ret == const.OPEN_GAP_UP) or (ret == const.OPEN_GAP_DOWN)):
        return buy_order, sell_order
    
    #check if doji
    ret1 = check_if_doji(ohlc)
    if ret1 == const.DOJI:
        print "doji  ", scrip
        buy_price = ohlc['high']
        sell_price = ohlc['low']
        stoploss_buy = None
        stoploss_sell = None
    else:

        if ret == const.OPEN_INSIDE_BODY_GREEN:
            buy_price = ohlc['close']
            sell_price = ohlc['open']
            stoploss_buy = None
            stoploss_sell = None

        if ret == const.OPEN_INSIDE_BODY_RED:
            buy_price = ohlc['open']
            sell_price = ohlc['close']
            stoploss_buy = None
            stoploss_sell = None
            #stoploss_buy = open_price
            #stoploss_sell = open_price


        if ret == const.OPEN_NEAR_HIGH_WICK_GREEN:
            buy_price = ohlc['high']
            #sell_price = ohlc['open']
            sell_price = None
            stoploss_buy = ohlc['close']
            stoploss_sell = None
        
        if ret == const.OPEN_NEAR_HIGH_WICK_RED:
            buy_price = ohlc['high']
            sell_price = None
            #sell_price = ohlc['close']
            stoploss_buy = ohlc['open']
            stoploss_sell = None
            
        
        if ret == const.OPEN_NEAR_LOW_WICK_GREEN:
            #buy_price = ohlc['close']
            buy_price = None
            sell_price = ohlc['low']
            stoploss_buy = None
            stoploss_sell = ohlc['open']

        if ret == const.OPEN_NEAR_LOW_WICK_RED:
            #uy_price = ohlc['open']
            buy_price = None
            sell_price = ohlc['low']
            stoploss_buy = None
            stoploss_sell = ohlc['close']
    
    buy_outstring =  get_order_string(scrip, "BUY", buy_price, stoploss_buy, stoploss_sell)
    sell_outstring = get_order_string(scrip, "SELL", sell_price, stoploss_buy, stoploss_sell)
    
    return buy_outstring, sell_outstring
    
################################################################################
# Function: get_yesterdays_ohlc()
# This function read bhavcopy file and gets the ohlc
# https://www.nseindia.com/products/content/equities/equities/archieve_eq.htm
# Format of each line contains 
# 20MICRONS,EQ,51.75,52,50.5,50.65,50.65,52,68773,3502793.35,16-MAR-2018,942,INE144J01027,
# scrip_index = 0
# open_index = 2
# high_index = 3
# low_index = 4
# close_index = 5
################################################################################
def get_yesterdays_ohlc(f_name):
    
    fp = open(f_name)
    for each in fp:
        each = each.split(",")
        if each[1] != "EQ":
            continue
        if float(each[3]) < float(config_dict['start_price']):
            continue
        if float(each[3]) > float(config_dict['end_price']):
            continue
        
        if each[0] in fno_dict:
            ohlc_dict = {}
            ohlc_dict["open"] = each[2]
            ohlc_dict["high"] = each[3]
            ohlc_dict["low"] = each[4]
            ohlc_dict["close"] = each[5]
            base_dict[each[0]] = ohlc_dict

    return base_dict

################################################################################
# Function: simulate()
# This function simulates the functionality of generating orders in offline 
# market
################################################################################
def simulate(filename):
    count = int(0)
    fno_dict = utils.get_fno_dict()
    fp = open(filename)
    for each in fp:
        each = each.split(",")
        if each[1] != "EQ":
            continue
        # only take scrips whose price is greater than 100 and less than 2000
        if float(each[3]) > float(2000):
            continue
        if float(each[3]) < float(200):
            continue
        
        if each[0] in fno_dict:
            count = count + int(1)
            generate_orders(each[0], base_dict[each[0]], each[2])
            
    print "Count = ", count
################################################################################
# Function: main()
# This is the main entry function for CBO algorithm
# Arguments passed to this function
# - base file name ---> sys.argv[1]
# - request_token got it from zerodha link ---> sys.argv[2]
# ex
# ACC BUY 1100 1100 5.5 11
# Scrip id = 0
# Action  = 1
# TRIGGER_ID = 2
# PRICE_ID = 3
# TARGET_ID =4
# STOPLOSS_ID = 5
################################################################################
def main():
    print "Executing CBO Algo for Equities"
    print "-------------------------------"

    global fno_dict, base_dict, config_dict, orders

    inst_token = []

    #TODO: Add argparser for validating input
    if len(sys.argv) < NO_OF_PARAMS:
        print "Invalid number of params"
        #return

    # read config file
    config_dict = utils.read_config_file()
    
    # get list of fno
    fno_dict = utils.get_fno_dict()

    # get yesterdays high low
    base_dict = get_yesterdays_ohlc(sys.argv[1])
    
    kite = kite_utils.login_kite(None)

    # get instrument list
    quote_list = []
    data = kite.instruments("NSE")
    for each in fno_dict:
        for instrument in data:
            if each == instrument['tradingsymbol']:
                entry = "NSE:" + str(instrument['tradingsymbol'])
                quote_list.append(entry)
    
    # open file to write buy/sell orders
    fp = open(config_dict['cbo_seed_file'], "w")
  
    # write header
    utils.write_header(fp, "CBO")

    count = int(0)
    quotes = kite.quote(quote_list)
    for each in quotes:
        scrip = each.split(":")[1].strip("\n")
        if float(quotes[each]["ohlc"]["open"]) < float(config_dict['start_price']):
            continue
        
        if float(quotes[each]["ohlc"]["open"]) > float(config_dict['end_price']):
            continue

        count = int(count) + int(1);
        buy, sell = generate_orders(scrip, base_dict[scrip], quotes[each]['ohlc']['open'])
        if (buy != None):
            fp.write(buy)
        if (sell != None):
            fp.write(sell)
    fp.close()

    # create dictionary for active orders
    # write utility fuction for order management

    # push all the orders
    order_list = []
    order_dict = {}
    fp = open(config_dict['cbo_seed_file'])
    for each in fp:
        #ignore line starting with #
        if each.startswith("#"):
            continue
        each = each.rstrip()
        line = each.split(" ")
        scrip = line[SCRIP_ID]
        action = line[ACTION_ID]
        price = line[PRICE_ID]
        t_price = line[TRIGGER_ID]
        target = line[TARGET_ID]
        stoploss = line[STOPLOSS_ID]

        if line[SCRIP_ID] not in order_dict:
            order_dict[scrip] = {}
            order_dict[scrip][action] = {}
        else:
            order_dict[scrip][action] = {}

        order_dict[scrip][action]['price'] = price
        order_dict[scrip][action]['trigger_price'] = t_price
        order_dict[scrip][action]['target'] = target
        order_dict[scrip][action]['stoploss'] = stoploss
        order_dict[scrip][action]['flag'] = 0
        

    fp.close()
    
    print "----------------------------------------------------------------"
    print order_dict
    print "----------------- End of order list ----------------------------"
  
     

    '''
    for each in order_list:
        utils.place_orders(kite, str(each[SCRIP_ID]),str(each[ACTION_ID]),
                    float(each[PRICE_ID]), float(each[TRIGGER_ID]),
                    float(each[TARGET_ID]),float(each[STOPLOSS_ID]))
    '''


if __name__ == "__main__":
    main()
