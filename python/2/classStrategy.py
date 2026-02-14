

class Strategy():

    def __init__(self):
        self.last_sell_step = 0
        self.last_buy_step = 0
        self.start_price = 0.0
        self.exchange = ''
        self.pair = ''
        self.buy_price = 0.0
        self.buy_qty = 0.0
        self.buy_lot = 0.0
        self.buy_type = 'quote'  # base, quote
        self.sell_price = 0.0
        self.sell_qty = 0.0
        self.sell_lot = 0.0
        self.sell_type = 'quote'  # base, quote
        self.depo = 0.0
        self.depo_ex = 0.0
        self.last_price = 0.0

    def edit(self, depo_ex):
        self.depo_ex = depo_ex

    def upd(self, data):
        self.exchange = data['exchange'] if 'exchange' in data else self.exchange
        self.pair = data['pair'] if 'pair' in data else self.pair
        self.depo = data['depo'] if 'depo' in data else self.depo
        self.depo_ex = data['depo_ex'] if 'depo_ex' in data else self.depo_ex
        self.last_price = data['last_price'] if 'last_price' in data else self.last_price
        self.buy_price = data['buy_price'] if 'buy_price' in data else self.buy_price
        self.buy_qty = data['buy_qty'] if 'buy_qty' in data else self.buy_qty
        self.sell_price = data['sell_price'] if 'sell_price' in data else self.sell_price
        self.sell_qty = data['sell_qty'] if 'sell_qty' in data else self.sell_qty
        self.buy_type = data['buy_type'] if 'buy_type' in data else self.buy_type
        self.sell_type = data['sell_type'] if 'sell_type' in data else self.sell_type

    def reset(self):
        self.depo_ex = 0.0

    def buy(self, price, qty):
        self.last_price = price
        self.last_buy_price = price
        self.last_sell_price = 0.0
        self.depo_ex += price * qty

    def sell(self, price, qty):
        self.last_price = price
        self.last_sell_price = price
        self.depo_ex -= price * qty
        self.last_buy_price = 0.0
        if round(self.depo_ex, 8) <= 0:
            self.reset()

    def check(self, last_price):

        depo_avail = self.depo - self.depo_ex
        self.last_price = last_price

        buy_lot = sell_lot = 0.0

        # ~ Вычисляем размеры лота
        if self.buy_type == 'base':
            buy_lot = self.buy_qty * last_price
        elif self.buy_type == 'quote':
            buy_lot = self.buy_qty
        if self.sell_type == 'base':
            sell_lot = self.sell_qty * last_price
        elif self.sell_type == 'quote':
            sell_lot = self.sell_qty

        self.buy_lot = buy_lot if buy_lot < depo_avail else depo_avail
        self.sell_lot = sell_lot if sell_lot < self.depo_ex else self.depo_ex

