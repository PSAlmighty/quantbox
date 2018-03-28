#!/usr/bin/python

import logging
from kiteconnect import KiteConnect, KiteTicker
import constants as const
import sys
import os
import utils
import ConfigParser
import time

NO_OF_PARAMS = 2
config_dict = {}
################################################################################
# Function: main()
# This is the main entry function for CBO algorithm
################################################################################
def main():
    print "Cancelling orders"
    print "-----------------"

    global fno_dict
    global base_dict
    global config_dict
    global orders

    inst_token = []
    config_dict = utils.read_config_file()
    print config_dict

    #open kite connection 
    if len(sys.argv) == int(NO_OF_PARAMS):
        request_token = sys.argv[1]
    else:
        request_token = None
    
    #kite = kite_utils.kite_login(request_token)
    config = ConfigParser.ConfigParser()
    config.read(config_dict['data_access'])
    access_token = config.get('MAIN','DATA_ACCESS_TOKEN')
   
    my_api = str(config_dict['kite_api_key'])
    my_api_secret = str(config_dict['kite_api_secret'])
    
    kite = KiteConnect(api_key=my_api)
    url = kite.login_url()
    # Redirect the user to the login url obtained
    # from kite.login_url(), and receive the request_token
    # from the registered redirect url after the login flow.
    # Once you have the request_token, obtain the access_token
    # as follows.
    # sys.argv[1] is access token that we get from login
    if request_token == None:
        kite.set_access_token(access_token)
    else:
        data = kite.generate_session(request_token, api_secret=my_api_secret)
        kite.set_access_token(data["access_token"])
        access_token = data["access_token"]
        config.set('MAIN','DATA_ACCESS_TOKEN', data["access_token"])

        with open(config_dict['data_access'], 'wb') as configfile:
            config.write(configfile)
    print kite
    
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
