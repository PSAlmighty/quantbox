#!/usr/bin/python
import ConfigParser
import constants as const

################################################################################
# Function: check_open_price()
# This function is the crux of this algorithm
# TODO: Write all the cases 
################################################################################
def check_open_price(ohlc, open_price):

    if float(open_price) > float(ohlc['high']):
        return const.OPEN_GAP_UP

    if float(open_price) < float(ohlc['low']):
        return const.OPEN_GAP_DOWN

    #green candle
    if float(ohlc['open']) < float(ohlc['close']):

        if ((float(open_price) >= float(ohlc['open'])) and
            (float(open_price) <= float(ohlc['close']))):
            return const.OPEN_INSIDE_BODY_GREEN
            
        if float(open_price) > float(ohlc['close']):
            return const.OPEN_NEAR_HIGH_WICK_GREEN
    
        else:
            return const.OPEN_NEAR_LOW_WICK_GREEN
    #red candle
    else:

        if ((float(open_price) >= float(ohlc['close'])) and
            (float(open_price) <= float(ohlc['open']))):
            return const.OPEN_INSIDE_BODY_RED
        
        if float(open_price) > float(ohlc['open']):
            return const.OPEN_NEAR_HIGH_WICK_RED
    
        else: 
            return const.OPEN_NEAR_LOW_WICK_RED

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
    config_dict['contract_date'] = config.get('FNO', 'CONTRACT_DATE')
    config_dict['contract_str'] = config.get('FNO', 'CONTRACT_STR')

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

    return fno_dict

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
    base_dict = {}
    config_dict = read_config_file()
    fno_dict = get_fno_dict()
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

################################################################################

################################################################################
def get_watchlist_dict(fname):
    fno_dict = {}
    watchlist = []
    config_dict = read_config_file()
    fq = open(config_dict['mkt_lotsize'])
    fp = open(fname)
    for each in fp:
        each = each.strip()
        watchlist.append(each)

    for each in fq:
        row = each.split(',')
        if row[1] in watchlist:
            fno_dict[row[1]] = row[3]

    return fno_dict

################################################################################
################################################################################
def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def get_floating_value(number):
    number = truncate(number, 2)
    i, p, d = str(number).partition(".") 
    r = int(d)%10
    if (r == 1):
        d = int(d) - r
    if (r == 2):
        d = int(d) - r
    if (r == 3):
        d = int(d) + 2
    if (r == 4):
        d = int(d) + 1
    if (r == 6):
        d = int(d) - 1
    if (r == 7):
        d = int(d) - 2
    if (r == 8):
        d = int(d) + 2
    if (r == 9):
        d = int(d) + 1

    number = float(str(i) + str(".") + str(d))
    return number

################################################################################
################################################################################
def get_closet_support(number):
    number = truncate(number, 2)
    i, p, d  = str(number).partition(".")
    r = int(d)%10
    if (r == 0):
        d = int(d) + 10
    if (r == 1):
        d = int(d) + 14
    if (r == 2):
        d = int(d) + 13
    if (r == 3):
        d = int(d) + 12
    if (r == 4):
        d = int(d) + 11
    if (r == 5):
        d = int(d) + 10
    if (r == 6):
        d = int(d) + 9
    if (r == 7):
        d = int(d) + 8
    if (r == 8):
        d = int(d) + 7
    if (r == 9):
        d = int(d) + 6

    number = str(i) + str(".") + str(d)
    number = truncate(number, 2)
    return number

################################################################################
################################################################################
def get_closet_restistance(number):
    number = truncate(number, 2)
    i, p, d  = str(number).partition(".")
    r = int(d)%10
    if (r == 0):
        d = int(d) + 10
    if (r == 1):
        d = int(d) + 14
    if (r == 2):
        d = int(d) + 13
    if (r == 3):
        d = int(d) + 12
    if (r == 4):
        d = int(d) + 11
    if (r == 5):
        d = int(d) + 10
    if (r == 6):
        d = int(d) + 9
    if (r == 7):
        d = int(d) + 8
    if (r == 8):
        d = int(d) + 7
    if (r == 9):
        d = int(d) + 6

    number = str(i) + str(".") + str(d)
    number = truncate(number, 2)
    return number

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
