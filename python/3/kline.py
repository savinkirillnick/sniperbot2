from time import time


class Kline:

    class Bar:
        def __init__(self, t, price):
            self.t = t
            self.l = self.o = self.c = self.h = price

        def upd(self, price):
            self.c = price
            self.l = price if price < self.l else self.l
            self.h = price if price > self.h else self.h

    def __init__(self):
        self.kline_1m = list()
        self.kline_5m = list()
        self.kline_30m = list()
        self.start_time = self.delta_time = 0

    def add(self, price):
        t = time()
        if self.start_time == 0:
            self.start_time = t - self.delta_time
            s60 = self.start_time // 60 * 60
            s300 = self.start_time // 300 * 300
            s1800 = self.start_time // 1800 * 1800
            self.kline_1m.append(self.Bar(s60, price))
            self.kline_5m.append(self.Bar(s300, price))
            self.kline_30m.append(self.Bar(s1800, price))
        for kline, period in zip([self.kline_1m, self.kline_5m, self.kline_30m], [60, 300, 1800]):
            delta = t - self.start_time
            if (delta // period + (delta % period > 0)) > len(kline):
                kline.append(self.Bar((kline[-1].t + period), price))
            else:
                kline[-1].upd(price)

    def get(self, period):
        if period == 60:
            return self.__get_data(self.kline_1m)
        if period == 300:
            return self.__get_data(self.kline_5m)
        if period == 1800:
            return self.__get_data(self.kline_30m)

    @staticmethod
    def __get_data(kline):
        kline = kline[-30:]
        data = dict()
        data['time'] = list()
        data['open'] = list()
        data['high'] = list()
        data['low'] = list()
        data['close'] = list()
        for i in range(len(kline)):
            data['time'].append(kline[i].t)
            data['open'].append(kline[i].o)
            data['high'].append(kline[i].h)
            data['low'].append(kline[i].l)
            data['close'].append(kline[i].c)
        return data

    def reset(self):
        self.kline_1m = list()
        self.kline_5m = list()
        self.kline_30m = list()
        self.start_time = 0

    def upd(self, delta):
        self.delta_time = delta
