from os import path
from time import time, strftime, localtime


class Errors:

    def __init__(self):
        self.data = {
            '100': 'Load Funnymay shared key Error 100',
            '101': 'DB Save key Error 101',
            '102': 'DB Load key Error 102',
            '103': 'DB Delete bot Settings Error 103',
            '104': 'DB Save bot settings Error 104',
            '105': 'DB Load bot settings Error 105',
            '106': 'DB Get settings List Error 106',
            '107': 'Telegram send Error 107',
            '110': 'Save position Error 110',
            '111': 'Load position Error 111',
            '112': 'Save strategy Error 112',
            '113': 'Load strategy Error 113',
            '114': 'Save alarm Error 114',
            '115': 'Load alarm Error 115',
            '116': 'Init Statistic Error 116',
            '117': 'Error 117',
            '118': 'Error 118',
            '119': 'Load new strategy from file Error 119',
            '120': 'Logs post Error 120',
            '121': 'Terminal Buy scale Error 121',
            '122': 'Terminal BuSell scale Error 122',
            '123': 'Debug window Error 123',
            '124': 'Calculator window Error 124',
            '125': 'API Binance load timestamp  Error 125',
            '126': 'API Binance timestamp request Error 126',
            '127': 'API Fetch Ticker Error 127',
            '128': 'API Fetch Order book Error 128',
            '129': 'View Order book Error 129',
            '130': 'API Fetch Open orders Error 130',
            '131': 'Cancel order Error 131',
            '132': 'Check orders Error 132',
            '133': 'View orders Error 133',
            '134': 'API Fetch my trades Error 134',
            '135': 'Check trades Error 135',
            '136': 'View trades Error 136',
            '137': 'API balances Error 137',
            '138': 'Terminal View Balances Error 138',
            '139': 'Terminal View step prices Error 139',
            '140': 'Send order Error 140',
            '141': 'Trade Rules control Error 141',
            '142': 'Prepare step prices Error 142',
            '150': 'Update position thread Error 150',
            '151': 'Update date_time thread Error 151',
            '152': 'Update depth thread Error 152',
            '153': 'Update last price thread Error 153',
            '154': 'Update open orders thread Error 154',
            '155': 'Update my trades thread Error 155',
            '156': 'Update balances thread Error 156',
            '157': 'Update main thread Error 157',
        }
        self.num = 0
        self.error_exception = None
        self.post_error('Bot opened')

    def error(self, num, error_exception=None):
        if num != self.num:
            self.num = num
            self.error_exception = error_exception
            self.post_error(self.get_error())

    def get_error(self):
            return self.data[str(self.num)] + ' ' + str(self.error_exception)

    def post_error(self, *args):
        try:
            post = ' '.join(args)
            dt = strftime('%y-%m-%d %H:%M:%S', localtime(time()))
            if not path.exists('error_logs.txt'):
                fout = open('error_logs.txt', 'wt')
            else:
                fout = open('error_logs.txt', 'at')
            fout.write(dt + ' ' + post + '\n')
            fout.close()
        except Exception as e:
            print(e, e.args)
