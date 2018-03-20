#!/usr/bin/python
import sys
import csv
import operator


def main():
    stocks_list = []
    count = int(0)
    max_trades = int(0)
    fp = open(sys.argv[1])
    for each in fp:
        each = each.split(",")
        if each[3] not in stocks_list:
            print "Adding --- ", each[3]
            stocks_list.append(each[3])
            count = int(count) + int(1)
            if (int(max_trades) < int(count)):
                max_trades = int(count)
            print "count = ", count
            print "max_trades = ", max_trades
    
        else:
            print "removing --- ", each[3]
            print "count = ", count
            print "max_trades = ", max_trades
            count = int(count) - int(1)
            stocks_list.remove(each[3])

    print "Max Trades = ", max_trades
        

if __name__ == "__main__":
    main()
