

class Position:

    def __init__(self, debug=False):
        self.price = 0.0
        self.qty = 0.0
        self.exchange = ''
        self.pair = ''

    def clear(self, exchange, pair):
        self.exchange = exchange
        self.pair = pair
        self.price = 0.0
        self.qty = 0.0
        return 0

    def edit(self, price, qty):
        self.price = price
        self.qty = qty
        return 0

    def upd(self, exchange, pair, price, qty):
        if self.exchange != exchange or self.pair != pair:
            self.clear(exchange, pair)
        else:
            self.price = price
            self.qty = qty
        return 0

    def reset(self):
        self.price = 0.0
        self.qty = 0.0
        return 0

    def buy(self, price, qty):
        lot = self.price * self.qty + price * qty
        self.qty += qty
        self.price = lot / self.qty
        return 0

    def sell(self, price, qty):
        self.qty -= qty
        if round(self.qty, 8) <= 0:
            self.reset()
        return 0

