#!/usr/bin/python

from kiteconnect import KiteConnect, KiteTicker
import constants as const
import sys
import os
import utils
import kite_utils

fno_dict = {}
base_dict = {}
config_dict = {}
orders = {}
NO_OF_PARAMS = 3

OPEN_INSIDE_BODY_GREEN = 1
OPEN_NEAR_HIGH_WICK_GREEN = 2
OPEN_NEAR_LOW_WICK_GREEN = 3
OPEN_GAP_UP = 4
OPEN_GAP_DOWN = 5
OPEN_INSIDE_BODY_RED = 6
OPEN_NEAR_HIGH_WICK_RED = 7
OPEN_NEAR_LOW_WICK_RED = 8


################################################################################
# Function: check_open_price()
# This function is the crux of this algorithm
# TODO: Write all the cases 
################################################################################
def check_open_price(scrip, ohlc, open_price):

    if float(open_price) > float(ohlc['high']):
        #print scrip, " GAP UP - ignore"
        return OPEN_GAP_UP

    if float(open_price) < float(ohlc['low']):
        #print scrip, "GAP DOWN - ignore"
        return OPEN_GAP_DOWN

    #green candle
    if float(ohlc['open']) < float(ohlc['close']):

        if ((float(open_price) >= float(ohlc['open'])) and
            (float(open_price) <= float(ohlc['close']))):
            #print scrip, " BETWEEN BODY"
            return OPEN_INSIDE_BODY_GREEN
            
        if float(open_price) > float(ohlc['close']):
            #print scrip, " BETWEEN HIGH WICK"
            return OPEN_NEAR_HIGH_WICK_GREEN
    
        else:
            return OPEN_NEAR_LOW_WICK_GREEN
    #red candle
    else:

        if ((float(open_price) >= float(ohlc['close'])) and
            (float(open_price) <= float(ohlc['open']))):
            #print scrip, " BETWEEN BODY"
            return OPEN_INSIDE_BODY_RED
        
        if float(open_price) > float(ohlc['open']):
            #print scrip, " BETWEEN HIGH WICK"
            return OPEN_NEAR_HIGH_WICK_RED
    
        else: 
            return OPEN_NEAR_LOW_WICK_RED

################################################################################
# Function: get_order_string()
# This function will return the 
################################################################################
def get_order_string(scrip, action, price):
    outstring = ""

    if action == "BUY":
        print "Preparing Buy"
        trigger_price = float(utils.get_floating_value(price)) +  float(0.10)
        price = trigger_price
        target = float(utils.get_floating_value(float(trigger_price) * float(config_dict['target_lock'])))
        stoploss = float(utils.get_floating_value(float(trigger_price) * float(config_dict['stoploss_lock'])))
        outstring = scrip + " " + action + " " + str(trigger_price) + " " + str(price) + " " + str(target) + " " + str(stoploss) +"\n"

    if action == "SELL":
        print "Preparing sell"
        trigger_price = float(utils.get_floating_value(price)) -  float(0.10)
        price = trigger_price
        target = float(utils.get_floating_value(float(trigger_price) * float(config_dict['target_lock'])))
        stoploss = float(utils.get_floating_value(float(trigger_price) * float(config_dict['stoploss_lock'])))
        outstring = scrip + " " + action + " " + str(trigger_price) + " " + str(price) + " " + str(target) + " " + str(stoploss) +"\n"

################################################################################
#
################################################################################
def generate_orders(scrip, ohlc, open_price):
    buy_order = None
    sell_order = None
    #check open price from quote
    ret = check_open_price(scrip, ohlc, open_price)

    if ((ret == OPEN_GAP_UP) or (ret == OPEN_GAP_DOWN)):
        return buy_order, sell_order
    
    if ret == OPEN_INSIDE_BODY_GREEN:
        buy_price = ohlc['close']
        sell_price = ohlc['open']

    if ret == OPEN_INSIDE_BODY_RED:
        buy_price = ohlc['open']
        sell_price = ohlc['close']


    if ret == OPEN_NEAR_HIGH_WICK_GREEN:
        buy_price = ohlc['high']
        sell_price = ohlc['open']
    
    if ret == OPEN_NEAR_HIGH_WICK_RED:
        buy_price = ohlc['high']
        sell_price = ohlc['close']
        
    
    if ret == OPEN_NEAR_LOW_WICK_GREEN:
        buy_price = ohlc['close']
        sell_price = ohlc['low']
    
    if ret == OPEN_NEAR_LOW_WICK_RED:
        buy_price = ohlc['open']
        sell_price = ohlc['low']
    
    buy_outstring = get_order_string(scrip, "BUY", buy_price)
    print buy_outstring
    
    sell_outstring = get_order_string(scrip, "SELL", sell_price)
    print sell_outstring
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
# Function: main()
# This is the main entry function for CBO algorithm
# Arguments passed to this function
# - base file name ---> sys.argv[1]
# - request_token got it from zerodha link ---> sys.argv[2]
################################################################################
def main():
    print "Executing CBO Algo for Equities"
    print "-------------------------------"

    global fno_dict
    global base_dict
    global config_dict
    global orders

    inst_token = []


    #TODO: Add argparser for validating input
    if len(sys.argv) < NO_OF_PARAMS:
        print "Invalid number of params"
        return

    # read config file
    config_dict = utils.read_config_file()
    
    # get list of fno
    fno_dict = utils.get_fno_dict()

    # get yesterdays high low
    base_dict = get_yesterdays_ohlc(sys.argv[1])

    #open kite connection 
    if len(sys.argv) == NO_OF_PARAMS:
        request_token = sys.argv[2]
    else:
        request_token = None
    kite = kite_utils.kite_login(request_token)

    # get instrument list
    data = kite.instruments(config_dict['nse'])
    for each in fno_dict:
        for instrument in data:
            entry = "NSE:" + str(instrument['tradingsymbol'])
            quote_list.append(entry)

    quotes = kite.quote(quote_list)
    for each in quotes:
        scrip = each.split(":")[1].strip("\n")
        if float(quotes[each]["ohlc"]["open"]) < float(config_dict['start_price']):
            continue
        
        if float(quotes[each]["ohlc"]["open"]) > float(config_dict['end_price']):
            continue

        buy, sell = generate_orders(scrip, base_dict[scrip], ret[each]['ohlc']['open']



    print "Instrument list"
    print "---------------"






if __name__ == "__main__":
    main()
