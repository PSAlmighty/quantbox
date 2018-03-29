#!/usr/bin/python

import logging
from kiteconnect import KiteConnect, KiteTicker
import constants as const
import sys
import os
import utils
import ConfigParser
import time

fno_dict = {}
base_dict = {}
config_dict = {}
orders = {}
NO_OF_PARAMS = 2

################################################################################
# Function: login_kite
################################################################################
def login_kite(request_token):

    global config_dict

    # read config file
    config_dict = utils.read_config_file()

    #kite = kite_utils.kite_login(request_token)
    config = ConfigParser.ConfigParser()
    config.read(config_dict['data_access'])
    access_token = config.get('MAIN','DATA_ACCESS_TOKEN')
   
    my_api = str(config_dict['kite_api_key'])
    my_api_secret = str(config_dict['kite_api_secret'])
    
    kite = KiteConnect(api_key=my_api)
    url = kite.login_url()
    print url
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

    return kite


def main():
    if len(sys.argv) != NO_OF_PARAMS:
        print "Invalid number of params"
        return

    login_kite(sys.argv[1])


if __name__ == "__main__":
    main()
