

class Bot():

    def __init__(self):
        self.error = ''
        self.access_time = 0.0
        self.api_key = ''
        self.api_secret = ''
        self.opt_key = ''
        self.exchange = ''
        self.depo = 0.0
        self.pair = ''
        self.order_life = 0.0
        self.pause = 0.0
        self.upd_time = 1.0
        self.num_set = ''
        self.buy_price = 0.0
        self.buy_qty = 0.0
        self.buy_type = ''  # base, quote
        self.sell_price = 0.0
        self.sell_qty = 0.0
        self.sell_type = ''  # base, quote

    def access(self, access_time):
        self.access_time = access_time

    def upd(self, data):
        self.api_key = data['api_key'] if 'api_key' in data else self.api_key
        self.api_secret = data['api_secret'] if 'api_secret' in data else self.api_secret
        self.opt_key = data['opt_key'] if 'opt_key' in data else self.opt_key
        self.exchange = data['exchange'] if 'exchange' in data else self.exchange
        self.depo = data['depo'] if 'depo' in data else self.depo
        self.pair = data['pair'] if 'pair' in data else self.pair
        self.num_set = data['num_set'] if 'num_set' in data else self.num_set
        self.order_life = data['order_life'] if 'order_life' in data else self.order_life
        self.pause = data['pause'] if 'pause' in data else self.pause
        self.upd_time = data['upd_time'] if 'upd_time' in data else self.upd_time
        self.buy_price = data['buy_price'] if 'buy_price' in data else self.buy_price
        self.buy_qty = data['buy_qty'] if 'buy_qty' in data else self.buy_qty
        self.sell_price = data['sell_price'] if 'sell_price' in data else self.sell_price
        self.sell_qty = data['sell_qty'] if 'sell_qty' in data else self.sell_qty
        self.buy_type = data['buy_type'] if 'buy_type' in data else self.buy_type
        self.sell_type = data['sell_type'] if 'sell_type' in data else self.sell_type
        return 0

    def get_set_data(self):
        data = dict()
        data['api_key'] = self.api_key
        data['api_secret'] = self.api_secret
        data['opt_key'] = self.opt_key
        data['num_set'] = self.num_set
        data['exchange'] = self.exchange
        data['depo'] = self.depo
        data['pair'] = self.pair
        data['order_life'] = self.order_life
        data['pause'] = self.pause
        data['upd_time'] = self.upd_time
        data['buy_price'] = self.buy_price
        data['buy_qty'] = self.buy_qty
        data['buy_type'] = self.buy_type
        data['sell_price'] = self.sell_price
        data['sell_qty'] = self.sell_qty
        data['sell_type'] = self.sell_type
        return data