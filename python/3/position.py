

class Position:

    def __init__(self, app):
        self.app = app
        self.price = 0.0
        self.qty = 0.0
        self.exchange = ''
        self.pair = ''

    def clear(self, exchange='', pair=''):
        self.exchange = exchange
        self.pair = pair
        self.price = 0.0
        self.qty = 0.0

    def edit(self, price, qty):
        self.price = price
        self.qty = qty

    def upd(self):
        if self.exchange != self.app.bot.exchange or self.pair != self.app.bot.pair:
            self.clear(self.app.bot.exchange, self.app.bot.pair)

    def reset(self):
        self.price = 0.0
        self.qty = 0.0

    def buy(self, price, qty):
        lot = self.price * self.qty + price * qty
        self.qty += qty
        self.price = lot / self.qty

    def sell(self, price, qty):
        self.qty -= qty
        if round(self.qty, 8) <= 0:
            self.reset()

    def set_data(self, data):
        self.exchange = data['exchange'] if 'exchange' in data else self.exchange
        self.pair = data['pair'] if 'pair' in data else self.pair
        self.price = data['price'] if 'price' in data else self.price
        self.qty = data['qty'] if 'qty' in data else self.qty
