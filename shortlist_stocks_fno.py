import constants as const
import sys
import os
import utils
import ConfigParser
import time
from os import listdir
from os.path import isfile, join


DEFAULT_DIR="bhavcopy"
fno_dict = {}
bullish_engulfing = []
bearing_engulfing = []
open_low = []
open_high = []
close_low = []
close_high = []
bar = []
close_wicks = []

def get_list_of_files(dir_name):
    print "Directory name: ", dir_name
    onlyfiles = [f for f in listdir(dir_name) if isfile(join(dir_name, f))]
    print onlyfiles

def getfiles(dirpath):
    a = [s for s in os.listdir(dirpath)
        if os.path.isfile(os.path.join(dirpath, s))]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)), reverse=True)
    return a

def populate_base(files, fno):
    global fno_dict
    fno_dict = {}
    for each in fno:
        fno_dict[each] = {}
        fno_dict[each]['open'] = []
        fno_dict[each]['high'] = []
        fno_dict[each]['low'] = []
        fno_dict[each]['close'] = []

    for f in files:
        file_name = "bhavcopy/" + f
        fp = open(file_name)
        for each in fp:
            each = each.split(",")
            if each[0] not in fno_dict:
                continue
            if each[1] != "EQ":
                continue
             
            fno_dict[each[0]]['open'].append(each[2])
            fno_dict[each[0]]['high'].append(each[3])
            fno_dict[each[0]]['low'].append(each[4])
            fno_dict[each[0]]['close'].append(each[5])
    return fno_dict
    
def get_overlapping_candle(fno):
    global bullish_engulfing
    global bearing_engulfing
    global open_low, open_high, close_low, close_high
    global bar, close_wicks

    for each in fno:
        # Green candle
        # 0 - open lower than low of previous, close higher than high of previous
        if float(fno[each]['open'][0]) <= float(fno[each]['low'][1]):
            if float(fno[each]['close'][0]) >= float(fno[each]['high'][1]):
                bullish_engulfing.append(each)

        if float(fno[each]['open'][0]) >= float(fno[each]['high'][1]):
            if float(fno[each]['close'][0]) <= float(fno[each]['low'][1]):
                bearing_engulfing.append(each)


        if float(fno[each]['open'][0]) == float(fno[each]['high'][0]):
            low_wick = utils.get_floating_value(float(fno[each]['low'][0]) * float(0.005))
            if (float(fno[each]['close'][0]) - float(fno[each]['low'][0])) <= float(low_wick):
                open_high.append(each)

        if float(fno[each]['open'][0]) == float(fno[each]['low'][0]):
            high_wick = utils.get_floating_value(float(fno[each]['high'][0]) * float(0.005))
            if (float(fno[each]['high'][0]) - float(fno[each]['close'][0])) <= float(high_wick):
                open_low.append(each)

        if float(fno[each]['open'][0]) > float(fno[each]['close'][0]):
            low_wick = utils.get_floating_value(float(fno[each]['low'][0]) * float(0.005))
            if (float(fno[each]['close'][0]) - float(fno[each]['low'][0])) <= float(low_wick):
                close_wicks.append(each)
            
        if float(fno[each]['open'][0]) < float(fno[each]['close'][0]):
            high_wick = utils.get_floating_value(float(fno[each]['high'][0]) * float(0.005))
            if (float(fno[each]['high'][0]) - float(fno[each]['close'][0])) <= float(high_wick):
                close_wicks.append(each)

        if float(fno[each]['close'][0]) == float(fno[each]['low'][0]):
            close_low.append(each)

        if float(fno[each]['close'][0]) == float(fno[each]['high'][0]):
            close_high.append(each)


        if float(fno[each]['open'][0]) == float(fno[each]['low'][0]):
            if float(fno[each]['close'][0]) == float(fno[each]['high'][0]):
                bar.append(each)
        
        if float(fno[each]['open'][0]) == float(fno[each]['high'][0]):
            if float(fno[each]['close'][0]) == float(fno[each]['low'][0]):
                bar.append(each)


    print "---------------------------------------------------------------------------"
    print "Bar\n"
    print bar

    print "---------------------------------------------------------------------------"
    print "Open high and close within 0.5%"
    print open_high

    print "---------------------------------------------------------------------------"
    print "Open low and close within 0.5%"
    print open_low

    print "---------------------------------------------------------------------------"
    print "Bullish Engulfing"
    print bullish_engulfing

    print "---------------------------------------------------------------------------"
    print "Bearish Engulfing"
    print bearing_engulfing

    print "---------------------------------------------------------------------------"
    print "close == low"
    print close_low

    print "---------------------------------------------------------------------------"
    print "close == high"
    print close_high

    print "---------------------------------------------------------------------------"
    print "Close near 0.5% wicks"
    print close_wicks
    print "---------------------------------------------------------------------------"



def main():
    print "Shortlisting stocks"
    print "-------------------"
    #get_list_of_files(DEFAULT_DIR) 
    file_list = getfiles(DEFAULT_DIR)
    
    #get the list of fno 
    fno = utils.get_fno_list()

    base = populate_base(file_list, fno)

    get_overlapping_candle(base)




if __name__ == "__main__":
    main()
