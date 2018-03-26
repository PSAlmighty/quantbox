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

    for each in fno:
        # Green candle
        # 0 - open lower than low of previous, close higher than high of previous
        if float(fno[each]['open'][0]) <= float(fno[each]['low'][1]):
            if float(fno[each]['close'][0]) >= float(fno[each]['high'][1]):
                print "Here with bullish engulfing"
                print each

        if float(fno[each]['open'][0]) >= float(fno[each]['high'][1]):
            if float(fno[each]['close'][0]) <= float(fno[each]['low'][1]):
                print "Here with bearish engulfing"
                print each



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
