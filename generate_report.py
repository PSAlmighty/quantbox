#!/usr/bin/python

import sys
import os
import utils
import constants as const

################################################################################
# Function : get_buy_sell_price()
#
################################################################################
def get_buy_sell_price(ohlc, ret):
    
    if ret == const.OPEN_INSIDE_BODY_GREEN:
        buy_price = ohlc['close']
        sell_price = ohlc['open']
    
    if ret == const.OPEN_INSIDE_BODY_RED:
        buy_price = ohlc['open']
        sell_price = ohlc['close']


    if ret == const.OPEN_NEAR_HIGH_WICK_GREEN:
        buy_price = ohlc['high']
        sell_price = ohlc['low']
    
    if ret == const.OPEN_NEAR_HIGH_WICK_RED:
        buy_price = ohlc['high']
        sell_price = ohlc['low']
        
    
    if ret == const.OPEN_NEAR_LOW_WICK_GREEN:
        buy_price = ohlc['high']
        sell_price = ohlc['low']

    if ret == const.OPEN_NEAR_LOW_WICK_RED:
        buy_price = ohlc['high']
        sell_price = ohlc['low']

    if ret == const.OPEN_GAP_UP:
        return None, None
    
    if ret == const.OPEN_GAP_DOWN:
        return None, None
    
    return buy_price, sell_price


################################################################################
################################################################################
def calculate_stats(scrip, buy, sell, ohlc):
    outstring = scrip
    if float(ohlc['high']) > float(buy):
        diff_buy = float(utils.get_floating_value(float(ohlc['high']) - float(buy)))
        buy_percentage = float(utils.get_floating_value(float(float(diff_buy) * float(100))/float(buy))) 
        diff_stoploss = float(utils.get_floating_value(float(buy) - float(ohlc['low'])))
        buy_stoploss_percentage = float(utils.get_floating_value(float(float(diff_stoploss) * float(100))/float(buy)))
        outstring = outstring + " Buy " + str(diff_buy) + " " + str(buy_percentage) + " "
        outstring = outstring + str(diff_stoploss) + " " + str(buy_stoploss_percentage) + "\n"
        print outstring

    if float(ohlc['low']) < float(sell):
        outstring = ""
        outstring = scrip
        diff_sell = float(utils.get_floating_value(float(sell) - float(ohlc['low'])))
        sell_percentage = float(utils.get_floating_value(float(float(diff_sell) * float(100))/float(sell))) 
        diff_stoploss = float(utils.get_floating_value(float(ohlc['high']) - float(sell)))
        sell_stoploss_percentage = float(utils.get_floating_value(float(float(diff_stoploss) * float(100))/float(sell)))
        outstring = outstring + " Sell " + str(diff_sell) + " " + str(sell_percentage) + " "
        outstring = outstring + str(diff_stoploss) + " " + str(sell_stoploss_percentage) + "\n"
        print outstring


################################################################################
# main function which accepts two files one for current day and one for day 
# before that
################################################################################
def main():
    print "Executing main program"
    base_dict = {}
    new_dict = {}

    base_dict = utils.get_yesterdays_ohlc(sys.argv[1])        
    print "====================================================================" 
    print base_dict
    print "====================================================================" 

    new_dict = utils.get_yesterdays_ohlc(sys.argv[2])
    print "====================================================================" 
    print new_dict
    print "====================================================================" 


    for each in new_dict:
        
        ret = utils.check_open_price(base_dict[each], new_dict[each]['open'])
        
        buy, sell = get_buy_sell_price(base_dict[each], ret)
        
        if (buy != None) and (sell != None):
            calculate_stats(each, buy, sell, new_dict[each])

if __name__ == "__main__":
    main()
