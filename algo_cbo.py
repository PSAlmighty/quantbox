#!/usr/bin/python

from kiteconnect import KiteConnect, KiteTicker
import constants as const
import sys
import os
import utils

fno_dict = {}
base_dict = {}
config_dict = {}

NO_OF_PARAMS = 2

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




def main():
    print "Calculating cbo params"
    global fno_dict
    global base_dict
    global config_dict
    #TODO: Add argparser for validating input
    if len(sys.argv) != NO_OF_PARAMS:
        print "Invalid number of params"
        return

    # read config file
    config_dict = utils.read_config_file()
    
    # get list of fno
    fno_dict = utils.get_fno_dict()

    # get yesterdays high low
    base_dict = get_yesterdays_ohlc(sys.argv[1])

    
    


if __name__ == "__main__":
    main()
