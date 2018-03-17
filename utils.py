#!/usr/bin/python
import ConfigParser
import constants as const

################################################################################
# Function: read_config_file
# This function reads default config file which is quantbox.config 
# It returns dictionary containing all the configuration related information 
# TODO: accept configuration file name as param
################################################################################
def read_config_file():
    config_dict = {}
    f_name = const.DEFAULT_CONFIG_FILE
    config = ConfigParser.ConfigParser()
    config.read(f_name)
    config_dict['start_price'] = config.getint('TRADE', 'START_PRICE')
    config_dict['end_price'] = config.getint('TRADE', 'END_PRICE')
    config_dict['target_lock'] = config.getfloat('TRADE', 'PROFIT_PERCENTAGE')
    config_dict['stoploss_lock'] = config.getfloat('TRADE', 'LOSS_PERENTAGE')
    
    config_dict['cbo_seed_file'] = config.get('SEEDS', 'CBO_SEED_FILE')
    config_dict['cbo_fno_seed_file'] = config.get('SEEDS', 'CBO_FNO_SEED_FILE')
    config_dict['data_access'] = config.get('FILES', 'DATA_ACCESS')

    config_dict['mkt_lotsize'] = config.get('REF', 'MKT_LOTSIZE')

    config_dict['kite_api_key'] = config.get('KITE', 'KITE_API_KEY')
    config_dict['kite_api_secret'] = config.get('KITE', 'KITE_API_SECRET')

    config_dict['nse'] = config.get('KEYWORDS', 'NSE')

    return config_dict


################################################################################
# Function: get_fno_list()
# This function reads future list file and returns the list of futurable stock
# list
# Row format 
# 3,ACC,31-May-18,400,1628,81424,32569,CALCULATE
# scrip name = 1 and lot size = 3
################################################################################
def get_fno_list():
    fno_stocks = []
    config_dict = read_config_file()

    # Open mkt lot size and return list
    fp = open(config_dict['mkt_lotsize'])
    if fp is None:
        print "Error in opening mkt lotsize ", config_dict['mkt_lotsize']
        return fno_stocks

    count = int(0) 
    for each in fp:
        row = each.split(',')
        fno_stocks.append(row[1])
        count = count + int(1)
    return fno_stocks

################################################################################
# Function:  get_fno_dict()
# This function reads future list obtained from zerodha and returns dictionary 
# of futurable stocks 
# 3,ACC,31-May-18,400,1628,81424,32569,CALCULATE
# scrip name = 1 and lot size = 3
################################################################################
def get_fno_dict():
    fno_dict = {}
    config_dict = read_config_file()

    # Open mkt lot size and return list
    fp = open(config_dict['mkt_lotsize'])
    if fp is None:
        print "Error in opening mkt lotsize ", config_dict['mkt_lotsize']
        return fno_stocks

    count = int(0) 
    for each in fp:
        row = each.split(',')
        fno_dict[row[1]] = row[3]
        count = count + int(1)

    print fno_dict
    return fno_dict

################################################################################
# Function: 
################################################################################






def main():
    print "Testing ....\n"
    '''
    config_dict = read_config_file()
    print config_dict
    '''
    get_fno_list()
    get_fno_dict()
    

if __name__ == "__main__":
    main()
