

class Statistic:

    def __init__(self):
        self.data = list()
        self.depo = 0.0
        self.pos = 0.0
        self.start_time = 0.0

    def set_depo(self, depo):
        self.depo = depo

    def use_trades(self, trades):
        for i in range(len(trades)):
            if trades[i]['side'] == 'buy':
                self.pos += trades[i]['amount']
                self.depo -= trades[i]['cost']
            if trades[i]['side'] == 'sell':
                self.pos -= trades[i]['amount']
                if self.pos < 0:
                    delta = -self.pos
                    self.pos = 0
                    part = delta / trades[i]['amount']
                    self.depo += trades[i]['cost'] * (1 - part)
                else:
                    self.depo += trades[i]['cost']
            balance = self.depo + self.pos * trades[i]['price']
            last_time = trades[i]['timestamp'] // 86400000 * 86400
            self.upd_statistic(last_time, balance)

    def upd_statistic(self, last_time, balance):
        if len(self.data) == 0:
            self.data.append({'time': last_time, 'balance': balance})
        else:
            if self.data[-1]['time'] == last_time:
                if balance > self.data[-1]['balance']:
                    self.data[-1]['balance'] = balance
            else:
                self.data.append({'time': last_time, 'balance': balance})
        return 0

    def get_list(self):
        tmp = list()
        for i in range(len(self.data)):
            tmp.append(self.data[i]['balance'])
        return tmp

    def set_data(self, data):
        self.data = data

    def reset(self):
        self.data = list()
        self.depo = 0.0
        self.pos = 0.0
        self.start_time = 0.0
