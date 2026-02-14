class Alarm:

    def __init__(self):
        self.error = ''
        self.on = 'Off'
        self.buy = False
        self.sell = False
        self.stat = False
        self.every = ''
        self.h = '00'
        self.m = '00'
        self.chat_id = ''
        self.token = ''

    def upd(self, data):
        self.on = data['on'] if 'on' in data else self.on
        self.buy = data['buy'] if 'buy' in data else self.buy
        self.sell = data['sell'] if 'sell' in data else self.sell
        self.stat = data['stat'] if 'stat' in data else self.stat
        self.every = data['every'] if 'every' in data else self.every
        self.h = data['h'] if 'h' in data else self.h
        self.m = data['m'] if 'm' in data else self.m
        self.chat_id = data['chat_id'] if 'chat_id' in data else self.chat_id
        self.token = data['token'] if 'token' in data else self.token
        return 0

    def get_set_data(self):
        data = dict()
        data['on'] = self.on
        data['buy'] = self.buy
        data['sell'] = self.sell
        data['stat'] = self.stat
        data['every'] = self.every
        data['h'] = self.h
        data['m'] = self.m
        data['chat_id'] = self.chat_id
        data['token'] = self.token
        return data
