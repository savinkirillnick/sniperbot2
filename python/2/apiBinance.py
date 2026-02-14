import requests  # Подключаем модуль для работы с HTTP запросами
import json  # Подключаем модуль для работы с объектами json
import math  # Подключаем модуль для математических операций
import hmac  # Подключаем модуль шифрования HMAC
import hashlib  # Подключаем библиотеки шифрования
from time import time  # Подключаем модуль работы с временем
import urllib.parse  # Подключение модуля работы с http строкой


class apiBinance():
    """
    Класс для работы с api binance
    Класс работы с биржей должен иметь следующие методы
    getRules - получение правил торговли валютой
    getCoins - получение всех монет биржи
    getPairs - получение всех пар биржи
    getBalances - получение балансов пользователя
    getDepth - получение стакана биржи
    getTrades -получение истории ордеров
    getOrders - получение открытых ордеров
    cancelOrder - отмена ордера
    sendOrder - отправка ордера
    getPrices - получение цен торгуемой пары
    getKline - получение графика котировок для пары
    остальные методы могут быть скрыты
    """
    def __init__(self, key, secret, debug=False):
        self.key = key
        self.secret = secret
        self.deltaTime = 0.0
        self.coins = set()
        self.pairs = set()
        self.rules = dict()
        self.debug = False
        self.error = False

        response = self.__query(method='get', url='https://api.binance.com/api/v3/time')
        serverTime = float(response['serverTime'])
        self.deltaTime = time() - serverTime / 1000
        self.debug = debug

    def debug_log(self, s):
        self.error = s

    def __query(self, method, url, **req):
        # Функция отправки запроса (вспомогательная функция)
        if method == 'get':
            try:
                response = requests.get(url, params=sorted(req.items()), headers={'X-MBX-APIKEY': self.key})
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + )
                    self.debug_log('code: 201, url: ' + url)
                return False
            if response.status_code == 200 or response.status_code == 400:
                data = response.json()
                if 'code' in data:
                    self.debug_log('code ' + str(data['code']) + ': ' + data['msg'])
                    return False
                else:
                    return data  # Возвращаем JSON объект
            else:
                return False
        if method == 'post':
            try:
                response = requests.post(url, data=sorted(req.items()), headers={'X-MBX-APIKEY': self.key})
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202, url: '+url)
                    self.debug_log('code: 202, url: ' + url)
                return False
            if response.status_code == 200 or response.status_code == 400:
                data = response.json()
                if 'code' in data:
                    self.debug_log('code ' + str(data['code']) + ': ' + data['msg'])
                    return False
                else:
                    return data  # Возвращаем JSON объект
            else:
                return False
        if method == 'delete':
            try:
                response = requests.delete(url, data=sorted(req.items()), headers={'X-MBX-APIKEY': self.key})
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 203, url: '+url)
                    self.debug_log('code: 203, url: ' + url)
                return False
            if response.status_code == 200 or response.status_code == 400:
                data = response.json()
                if 'code' in data:
                    self.debug_log('code ' + str(data['code']) + ': ' + data['msg'])
                    return False
                else:
                    return data  # Возвращаем JSON объект
            else:
                return False

    def __sign(self, **req):
        # Функция для шифрования подписи
        secret = self.secret.encode()
        data = urllib.parse.urlencode(sorted(req.items())).encode()
        return hmac.new(secret, data, hashlib.sha256).hexdigest()

    def getRules(self):
        # Получение правил биржи, монет и символов
        # pairs - set()
        # coins - set()
        # rules - dict()
        response = self.__query(method='get', url='https://api.binance.com/api/v3/exchangeInfo')
        if type(response) != type(dict()):
            return False
        if response != False:

            try:
                for symbol in response['symbols']:
                    if symbol['status'] == 'TRADING':
                        baseAsset = symbol['baseAsset'].lower()
                        quoteAsset = symbol['quoteAsset'].lower()
                        pair = baseAsset + '_' + quoteAsset

                        self.coins.add(baseAsset)
                        self.coins.add(quoteAsset)
                        self.pairs.add(pair)

                        self.rules[pair] = {}
                        self.rules[pair]['symbol'] = symbol['symbol']
                        self.rules[pair]['minPrice'] = float(symbol['filters'][0]['minPrice'])
                        self.rules[pair]['maxPrice'] = float(symbol['filters'][0]['maxPrice'])
                        self.rules[pair]['minQty'] = float(symbol['filters'][2]['minQty'])
                        self.rules[pair]['maxQty'] = float(symbol['filters'][2]['maxQty'])
                        self.rules[pair]['aroundPrice'] = int(abs(math.log10(float(symbol['filters'][0]['tickSize']))))
                        self.rules[pair]['aroundQty'] = int(abs(math.log10(float(symbol['filters'][2]['stepSize']))))
                        self.rules[pair]['minSum'] = float(symbol['filters'][3]['minNotional'])
                        self.rules[pair]['maxSum'] = 0
                self.coins = list(self.coins)
                self.coins.sort()
                self.pairs = list(self.pairs)
                self.pairs.sort()
                return self.rules
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 210')
                    self.debug_log('code: 210. Get rules false')
                return False
        else:
            return False

    def getCoins(self):
        return self.coins

    def getPairs(self):
        return self.pairs

    def getDepth(self, **req):
        # Получение стакана
        # Сначала спредовые
        # depth = dict()
        depth = str(req['depth'])
        symbol = self.rules[req['pair']]['symbol']
        response = self.__query(method='get', url='https://api.binance.com/api/v3/depth', symbol=symbol, limit=depth)
        if type(response) != type(dict()):
            return False
        if response != False:
            try:
                data = {}
                data['asks'] = []
                data['bids'] = []
                num_asks = req['depth'] if req['depth'] < len(response['asks']) else len(response['asks'])
                num_bids = req['depth'] if req['depth'] < len(response['bids']) else len(response['bids'])
                for i in range(num_asks):
                    data['asks'].append([])
                    data['asks'][i].append(float(response['asks'][i][0]))
                    data['asks'][i].append(float(response['asks'][i][1]))
                for i in range(num_bids):
                    data['bids'].append([])
                    data['bids'][i].append(float(response['bids'][i][0]))
                    data['bids'][i].append(float(response['bids'][i][1]))
                return data
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 220')
                    self.debug_log('code: 220. Get depth false')
                return False
        else:
            return False

    def getPrice(self, **req):
        # Получение последней цены
        symbol = self.rules[req['pair']]['symbol']
        response = self.__query(method='get', url='https://api.binance.com/api/v3/ticker/price')
        if type(response) != type(list()):
            return False
        if response != False:
            try:
                count = len(response)
                for i in range(count):
                    if response[i]['symbol'] == symbol:
                        return float(response[i]['price'])
                return False
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
                    self.debug_log('code: 230. Get price false')
                return False
        return False

    # Авторизованные методы

    def getBalances(self, all=False):
        # Получение балансов
        correctTime = round((time() - self.deltaTime) * 1000)
        signedString = self.__sign(recvWindow=5000, timestamp=correctTime)
        response = self.__query(method='get', url='https://api.binance.com/api/v3/account', recvWindow=5000,
                                timestamp=correctTime, signature=signedString)
        if type(response) != type(dict()):
            return False
        if response != False:
            data = {}
            try:
                count = len(response['balances'])
                for i in range(count):
                    if all:
                        data[response['balances'][i]['asset'].lower()] = float(response['balances'][i]['free']) + float(response['balances'][i]['locked'])
                    else:
                        data[response['balances'][i]['asset'].lower()] = float(response['balances'][i]['free'])
                return data
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 250')
                    self.debug_log('code: 250. Get balances false')
                return False
        else:
            return False

    def getTrades(self, **req):
        # Получение истории ордеров
        # Сначала старые, в конце новые
        symbol = self.rules[req['pair']]['symbol']
        correctTime = round((time() - self.deltaTime) * 1000)
        signedString = self.__sign(recvWindow=5000, timestamp=correctTime, symbol=symbol, limit=10)
        response = self.__query(method='get', url='https://api.binance.com/api/v3/myTrades', recvWindow=5000,
                                timestamp=correctTime, symbol=symbol, limit=10, signature=signedString)
        if type(response) != type(list()):
            return False
        if response != False:
            try:
                count = len(response)
                data = []
                for i in range(count):
                    data.append({})
                    data[i]['pair'] = req['pair']
                    if response[i]['isBuyer'] == True:
                        data[i]['side'] = 'buy'
                    else:
                        data[i]['side'] = 'sell'
                    data[i]['qty'] = float(response[i]['qty'])
                    data[i]['price'] = float(response[i]['price'])
                    data[i]['time'] = response[i]['time'] / 1000 + self.deltaTime
                return data if count > 0 else False
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 260')
                    self.debug_log('code: 260. Get trades false')
                return False

        else:
            return False
        return False

    def getOrders(self, **req):
        # Получение активных ордеров
        # Сначала старые, в конце новые
        symbol = self.rules[req['pair']]['symbol']
        correctTime = round((time() - self.deltaTime) * 1000)
        signedString = self.__sign(recvWindow=5000, timestamp=correctTime, symbol=symbol)
        response = self.__query(method='get', url='https://api.binance.com/api/v3/openOrders', recvWindow=5000,
                                timestamp=correctTime, symbol=symbol, signature=signedString)
        if type(response) != type(list()):
            return False
        if response != False:
            try:
                count = len(response)
                data = []
                for i in range(count):
                    data.append({})
                    data[i]['id'] = str(response[i]['orderId'])
                    data[i]['pair'] = req['pair']
                    data[i]['side'] = response[i]['side'].lower()
                    data[i]['qty'] = float(response[i]['origQty'])
                    data[i]['fill'] = float(response[i]['executedQty'])
                    data[i]['price'] = float(response[i]['price'])
                    data[i]['time'] = response[i]['time'] / 1000 + self.deltaTime
                return data if count > 0 else False
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 270')
                    self.debug_log('code: 270. Get orders false')
                return False
        else:
            return False
        return False

    def cancelOrder(self, **req):
        # Отмена ордера
        # orderId
        symbol = self.rules[req['pair']]['symbol']
        orderId = int(req['id'])
        correctTime = round((time() - self.deltaTime) * 1000)
        signedString = self.__sign(recvWindow=5000, timestamp=correctTime, symbol=symbol, orderId=orderId)
        response = self.__query(method='delete', url='https://api.binance.com/api/v3/order', recvWindow=5000,
                                timestamp=correctTime, symbol=symbol, orderId=orderId, signature=signedString)
        if type(response) != type(dict()):
            return False
        try:
            if response['orderId'] == int(orderId) and response['status'] == 'CANCELED':
                return True
            else:
                return False
        except:
            if self.debug:
                # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 280')
                self.debug_log('code: 280. Cancel order false')
            return False
        return False

    def sendOrder(self, **req):
        # Отправка ордера
        # orderId
        aroundPrice = self.rules[req['pair']]['aroundPrice']
        aroundQty = self.rules[req['pair']]['aroundQty']

        formatPrice = '{:.' + str(aroundPrice) + 'f}'
        formatQty = '{:.' + str(aroundQty) + 'f}'

        symbol = self.rules[req['pair']]['symbol']
        side = req['side'].upper()
        qty = str(formatQty.format(req['qty']))
        price = str(formatPrice.format(req['price']))
        correctTime = round((time() - self.deltaTime) * 1000)
        signedString = self.__sign(recvWindow=5000, timestamp=correctTime, symbol=symbol, side=side, quantity=qty,
                                   price=price, type='LIMIT', timeInForce='GTC')
        response = self.__query(method='post', url='https://api.binance.com/api/v3/order', recvWindow=5000,
                                timestamp=correctTime, symbol=symbol, side=side, quantity=qty, price=price,
                                type='LIMIT', timeInForce='GTC', signature=signedString)

        if type(response) != type(dict()):
            return False
        try:
            return str(response['orderId'])
        except:
            if self.debug:
                # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
                self.debug_log('code: 290. Send order false')
            return False
        return False

# ~ https://binance-docs.github.io/apidocs/spot/en/

