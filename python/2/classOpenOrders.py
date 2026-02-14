class OpenOrders():
    # {'id':{'price':'','qty':'','side':'','pair':'','status':'','desc':''}}
    open_orders = None

    def __init__(self):
        self.open_orders = dict()

    def add(self, key, data):
        if key in self.open_orders:
            self.upd(key, data)
        else:
            self.open_orders[key] = dict()
            self.open_orders[key] = data

    def upd(self, key, data):
        if key in self.open_orders:
            self.open_orders[key] = dict()
            self.open_orders[key] = data

    def rm(self, key):
        if key in self.open_orders:
            del self.open_orders[key]

    def keys(self):
        return self.open_orders.keys()

    def clear(self):
        self.open_orders = dict()

    def get_data(self, key):
        if key in self.open_orders:
            return {'price': self.open_orders[key]['price'], 'qty': self.open_orders[key]['qty'],
                    'side': self.open_orders[key]['side'], 'pair': self.open_orders[key]['pair'],
                    'desc': self.open_orders[key]['desc'], }
        else:
            return False
