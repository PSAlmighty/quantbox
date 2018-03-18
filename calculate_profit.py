#!/usr/bin/python

import sys
import os
import commands
import csv
import constants as const
import utils

'''
    This program accepts filename as input. 
    The file is downloaded report which we get from zerodha.
    Make sure that this is in csv format 
'''

NO_OF_PARAMS = 2

def main():
    if len(sys.argv) != NO_OF_PARAMS:
        print "Invalid number of parameters"
        print "./calculate_profit.py csv_file"

    PL = int(0)
    lot_size_dict = utils.get_fno_dict()

    fp = open(sys.argv[1])
    count = int(0)
    #TODO: Format output
    print "------------------------------------------"
    for row in fp:
        if(count == int(0)):
            count = count + int(1)
            continue;
        li = row.split(",")
        try:
            lot_size = lot_size_dict[li[1]]
        except KeyError:
            count = count + int(1)
            continue

        lot_size = lot_size_dict[li[1]]
        current_pl = float(float(li[5]) * int(lot_size)) 

        print li[1], " = ", current_pl
        count = count + int(1)
        PL = float(PL) + float(current_pl)
    
    print "------------------------------------------"
    print "Total P/L = ", PL
    print "------------------------------------------"

if __name__ == "__main__":
    main()

