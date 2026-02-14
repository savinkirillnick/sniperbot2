from os import path
from time import time, strftime, localtime


class Logs:

    def post(self, *args):
        try:
            post = ' '.join(args)
            dt = strftime('%y-%m-%d %H:%M:%S', localtime(time()))
            if not path.exists('logs.txt'):
                fout = open('logs.txt', 'wt')
            else:
                fout = open('logs.txt', 'at')
            fout.write(dt + ' ' + post + '\n')
            fout.close()
        except:
            return 120

    def __init__(self):
        self.post('Bot opened')


# lg = Logs()
# lg.post('exchange PAIR ORDER SEND by auto BUY 10.001 BNB at 186.99 USDT')
# lg.post('POSITION BNB/USDT add 10.001 BNB at 186.99 USDT, Avg Price = 186.99 Total Amount = 10.001')