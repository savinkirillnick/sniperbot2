from time import time


class User:

    def __init__(self):
        self.name = 'Sniperbot'
        self.ver = '3.0.2'
        self.build = '2024-09-01.1917'
        self.shared_key = 'demo'
        self.demo_mode = False
        self.file_data = 0
        self.activation = UserActivation(self)
        self.api_is_init = False
        self.bot_is_init = False
        self.bot_is_run = False
        self.pos_is_init = False
        self.st_is_init = False
        self.kl_is_init = False
        self.stat_is_init = False
        self.settings_list = list()
        self.rules = dict()
        self.coins = set()
        self.pairs = set()
        self.balances = dict()
        self.depth = dict()
        self.depth['bids'] = list()
        self.depth['asks'] = list()
        self.orders = list()
        self.trades = list()
        self.curr_base = ''
        self.curr_quote = ''
        self.queue_id = ''
        self.queue_side = ''
        self.last_price = 0.0
        self.buy_access = self.sell_access = False
        self.last_trade_time = time()
        self.start_buy_trading = self.start_sell_trading = 0.0
        self.buy_price = self.sell_price = self.buy_qty = self.sell_qty = 0.0
        self.last_alarm_time = 0.0
        self.save_stat_time = 0.0
        self.next_time_settings = 0.0
        self.delta_time = 0.0


class UserActivation:
    # Вырезан весь функционал по проверке и активации пользователя
    def __init__(self, parent):
        self.parent = parent

    def check(self):
        return True
