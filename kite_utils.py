#!/usr/bin/python

import logging
from kiteconnect import KiteConnect, KiteTicker
import sys
import constants
import utils
import ConfigParser

config_dict = {}

################################################################################
# Function: kite_login()
# This function accepts request token, this might be needed on first login of 
# the day, Later we can store the data_access in the file and read it 
# If we want to access data from the file that use request_token as None
# else pass request token passed as input on the command line for the calling 
# function
################################################################################
def kite_login(request_token):
    global config_dict
    
    # read config file 
    config_dict = utils.read_config_file()

    # read data_access_file
    config = ConfigParser.ConfigParser()
    config.read(config_dict['data_access'])
    access_token = config.get('MAIN','DATA_ACCESS_TOKEN')
    
    kite = KiteConnect(api_key=config_dict['kite_api_key'])
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
        data = kite.generate_session(request_token, api_secret=config_dict['kite_api_secret'])
        kite.set_access_token(data["access_token"])
        config.set('MAIN','DATA_ACCESS_TOKEN', data["access_token"])

        with open(config_dict['data_access'], 'wb') as configfile:
            config.write(configfile)

    return kite

