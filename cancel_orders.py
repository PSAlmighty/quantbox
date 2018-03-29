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

config_dict = {}

################################################################################
# Function: main()
# This is the main entry function for CBO algorithm
################################################################################
def main():

    print "Cancelling orders"
    print "-----------------"

    global config_dict

    inst_token = []
    config_dict = utils.read_config_file()

    kite = kite_utils.kite_login()
    
    orders = kite.orders()
    print "======================================================="
    for each in orders:
        if each['parent_order_id'] != None:
            print each
            kite.cancel_order(kite.VARIETY_BO, each['order_id'], parent_order_id=each['parent_order_id'])
        else:
            kite.cancel_order(kite.VARIETY_BO, each['order_id'], parent_order_id=None)

    print "======================================================="
    

if __name__ == "__main__":
    main()
