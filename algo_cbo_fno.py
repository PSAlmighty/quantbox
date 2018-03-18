#!/usr/bin/python
import re
import logging
from kiteconnect import KiteConnect, KiteTicker
import constants as const
import sys
import os
import utils
import kite_utils
import ConfigParser


fno_dict = {}
base_dict = {}
config_dict = {}
orders = {}
NO_OF_PARAMS = 2
sub_list = []
# This is index into 
#TODO: move this to const
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
def get_order_string(scrip, action, price):
    outstring = ""

    if action == "BUY":
        trigger_price = float(utils.get_floating_value(price)) +  float(0.10)
        price = trigger_price
        target = float(utils.get_floating_value(float(trigger_price) * float(config_dict['target_lock'])))
        stoploss = float(utils.get_floating_value(float(trigger_price) * float(config_dict['stoploss_lock'])))
        outstring = scrip + " " + action + " " + str(trigger_price) + " " + str(price) + " " + str(target) + " " + str(stoploss) +"\n"

    if action == "SELL":
        trigger_price = float(utils.get_floating_value(price)) -  float(0.10)
        price = trigger_price
        target = float(utils.get_floating_value(float(trigger_price) * float(config_dict['target_lock'])))
        stoploss = float(utils.get_floating_value(float(trigger_price) * float(config_dict['stoploss_lock'])))
        outstring = scrip + " " + action + " " + str(trigger_price) + " " + str(price) + " " + str(target) + " " + str(stoploss) +"\n"

    return outstring

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
    
    if ret == const.OPEN_INSIDE_BODY_GREEN:
        buy_price = ohlc['close']
        sell_price = ohlc['open']

    if ret == const.OPEN_INSIDE_BODY_RED:
        buy_price = ohlc['open']
        sell_price = ohlc['close']


    if ret == const.OPEN_NEAR_HIGH_WICK_GREEN:
        buy_price = ohlc['high']
        sell_price = ohlc['open']
    
    if ret == const.OPEN_NEAR_HIGH_WICK_RED:
        buy_price = ohlc['high']
        sell_price = ohlc['close']
        
    
    if ret == const.OPEN_NEAR_LOW_WICK_GREEN:
        buy_price = ohlc['close']
        sell_price = ohlc['low']
    
    if ret == const.OPEN_NEAR_LOW_WICK_RED:
        buy_price = ohlc['open']
        sell_price = ohlc['low']
    
    buy_outstring = get_order_string(scrip, "BUY", buy_price)
    sell_outstring = get_order_string(scrip, "SELL", sell_price)
   
    
    return buy_outstring, sell_outstring
    
################################################################################
# Function: get_yesterdays_fno_ohlc()
# This function read bhavcopy file and gets the ohlc
# https://www.nseindia.com/products/content/equities/equities/archieve_eq.htm
# Format of each line contains 
# ['FUTSTK', 'WIPRO', '28-Mar-2018', '0', 'XX', '295.15', '303', '293', '293.8', '293.8', '3628', '25921.62', '30472800', '945600', '15-MAR-2018', '\n'] 
# scrip_index = 0
# open_index = 2
# high_index = 3
# low_index = 4
# close_index = 5
################################################################################
def get_yesterdays_fno_ohlc(f_name):
    #print fno_dict
    contract = config_dict['contract_date']
    fp = open(f_name)
    for each in fp:
        each = each.split(",")
        if each[0] != "FUTSTK":
            continue
        if each[2] != contract:
            continue

        if float(each[5]) < float(config_dict['start_price']):
            continue
        if float(each[5]) > float(config_dict['end_price']):
            continue
        
        if each[1] in fno_dict:
            ohlc_dict = {}
            ohlc_dict["open"] = each[5]
            ohlc_dict["high"] = each[6]
            ohlc_dict["low"] = each[7]
            ohlc_dict["close"] = each[8]
            base_dict[each[1]] = ohlc_dict

    print "-------------------------------------------------------------"
    print base_dict
    print "-------------------------------------------------------------"
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

    global fno_dict
    global base_dict
    global config_dict
    global orders

    #TODO: Add argparser for validating input
    if len(sys.argv) < NO_OF_PARAMS:
        print "Invalid number of params"
        return

    # read config file
    config_dict = utils.read_config_file()
    print config_dict
    # get list of fno
    fno_dict = utils.get_fno_dict()

    # get yesterdays high low
    base_dict = get_yesterdays_fno_ohlc(sys.argv[1])
    #simulate(sys.argv[2])

    #open kite connection 
    if len(sys.argv) == int(NO_OF_PARAMS) + int(1):
        request_token = sys.argv[2]
    else:
        request_token = None
    

    api_key, access_token, kite = kite_utils.kite_login(request_token)
    # get instrument list
    quote_list = []
    data = kite.instruments("NFO")
    for each in data:
        if each['instrument_type'] != 'FUT':
            continue

        if config_dict['contract_str'] not in each['tradingsymbol']:
            continue

        entry = "NFO:" + str(each['tradingsymbol'])
        quote_list.append(entry)
        sub_list.append(each['instrument_token']) 
    # open file to write buy/sell orders
    fp = open(config_dict['cbo_fno_seed_file'], "w")
    count = int(0)
    quotes = kite.quote(quote_list)
    order_dict = {}
    for each in quotes:
        
        scrip = each.split(":")[1].strip("\n")
        m = re.search("\d", scrip)
        if m:
            scrip = scrip[:m.start()]
        
        if float(quotes[each]["ohlc"]["open"]) < float(config_dict['start_price']):
            continue
        
        if float(quotes[each]["ohlc"]["open"]) > float(config_dict['end_price']):
            continue

        count = int(count) + int(1);
        if scrip in base_dict:
            buy, sell = generate_orders(scrip, base_dict[scrip], quotes[each]['ohlc']['open'])
            if (buy != None):
                buy_dict = {}
                each = buy.split(" ")
                buy_dict['price'] = each[2]
                buy_dict['target'] = float(utils.get_floating_value(float(each[2]) +  float(each[4])))
                buy_dict['stoploss'] = float(utils.get_floating_value(float(each[2]) - float(each[5])))
                buy_dict['trade_active'] = False
                order_dict[scrip] = {}
                order_dict[scrip]['buy'] = buy_dict
                fp.write(buy)
            if (sell != None):
                sell_dict = {}
                each = sell.split(" ")
                sell_dict['price'] = each[2]
                sell_dict['target'] = float(utils.get_floating_value(float(each[2]) -  float(each[4])))
                sell_dict['stoploss'] = float(utils.get_floating_value(float(each[2]) + float(each[5])))
                sell_dict['trade_active'] = False
                order_dict[scrip] = {}
                order_dict[scrip]['sell'] = sell_dict
                fp.write(sell)
    fp.close()
    print order_dict
    kws = KiteTicker(api_key, access_token, debug=False)
    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.on_error = on_error
    kws.on_noreconnect = on_noreconnect
    kws.on_reconnect = on_reconnect
    kws.on_order_update = on_order_update
    kws.connect()


def on_ticks(ws, ticks):
    print "Hello"


def on_connect(ws, response):
     
    sub_list = []
    print "============================================"
    print sub_list
    print "============================================"

    ws.subscribe([2800641, 2752769, 1207553, 3735553, 356865, 5444865, 302337, 779521, 3905025, 103425, 2939649, 359937, 738561, 87297, 8042241, 1837825, 415745, 2905857, 315393, 2763265, 548353, 4995329, 857857, 884737, 340481, 173057, 784129, 2955009, 737793, 2865921, 108033, 134657, 1076225, 3876097, 101121, 492033, 681985, 41729, 2953217, 25601, 3832833, 873217, 1850625, 2889473, 245249, 140033, 2672641, 633601, 878593, 4278529, 3365633, 3431425, 2883073, 1895937, 969473, 1041153, 900609, 584449, 2952193, 2911489, 348929, 4488705, 1270529, 49409, 1346049, 5633, 1215745, 871681, 6054401, 3513601, 2997505, 4343041, 2747905, 98049, 3861249, 60417, 3400961, 2079745, 1510401, 40193, 951809, 3529217, 141569, 837889, 1195009, 1256193, 3789569, 94977, 975873, 70401, 424961, 4314113, 408065, 3675137, 319233, 7670273, 2714625, 387841, 895745, 2796801, 325121, 519937, 3834113, 215553, 160001, 85761, 952577, 364545, 160769, 897537, 177665, 2513665, 5215745, 511233, 4632577, 197633, 486657, 1921537, 112129, 3465729, 3663105, 320001, 731905, 4159745, 3050241, 806401, 7455745, 2170625, 7458561, 1102337, 2730497, 3932673])
    ws.set_mode(ws.MODE_FULL, [2800641, 2752769, 1207553, 3735553, 356865, 5444865, 302337, 779521, 3905025, 103425, 2939649, 359937, 738561, 87297, 8042241, 1837825, 415745, 2905857, 315393, 2763265, 548353, 4995329, 857857, 884737, 340481, 173057, 784129, 2955009, 737793, 2865921, 108033, 134657, 1076225, 3876097, 101121, 492033, 681985, 41729, 2953217, 25601, 3832833, 873217, 1850625, 2889473, 245249, 140033, 2672641, 633601, 878593, 4278529, 3365633, 3431425, 2883073, 1895937, 969473, 1041153, 900609, 584449, 2952193, 2911489, 348929, 4488705, 1270529, 49409, 1346049, 5633, 1215745, 871681, 6054401, 3513601, 2997505, 4343041, 2747905, 98049, 3861249, 60417, 3400961, 2079745, 1510401, 40193, 951809, 3529217, 141569, 837889, 1195009, 1256193, 3789569, 94977, 975873, 70401, 424961, 4314113, 408065, 3675137, 319233, 7670273, 2714625, 387841, 895745, 2796801, 325121, 519937, 3834113, 215553, 160001, 85761, 952577, 364545, 160769, 897537, 177665, 2513665, 5215745, 511233, 4632577, 197633, 486657, 1921537, 112129, 3465729, 3663105, 320001, 731905, 4159745, 3050241, 806401, 7455745, 2170625, 7458561, 1102337, 2730497, 3932673])

def on_close(ws, code, reason):
    logging.error("closed connection on close: {} {}".format(code, reason))


def on_error(ws, code, reason):
    logging.error("closed connection on error: {} {}".format(code, reason))


def on_noreconnect(ws):
    logging.error("Reconnecting the websocket failed")


def on_reconnect(ws, attempt_count):
    logging.debug("Reconnecting the websocket: {}".format(attempt_count))


def on_order_update(ws, data):
    print("order update: ", data)




if __name__ == "__main__":
    main()
