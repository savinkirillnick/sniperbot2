import requests  # Подключаем модуль для работы с HTTP запросами
import json  # Подключаем модуль для работы с объектами json
import math  # Подключаем модуль для математических операций
import hmac  # Подключаем модуль шифрования HMAC
from time import time, timezone, localtime, strftime, mktime, strptime  # Подключаем модуль работы с временем
import urllib.parse  # Подключение модуля работы с http строкой
from base64 import b64encode  # Подключаем кодирование 64


class apiOkex:
    # Класс для работы с api okex
    # Класс работы с биржей должен иметь следующие методы
    # getRules - получение правил торговли валютой
    # getCoins - получение всех монет биржи
    # getPairs - получение всех пар биржи
    # getBalances - получение балансов пользователя
    # getDepth - получение стакана биржи
    # getTrades -получение истории ордеров
    # getOrders - получение открытых ордеров
    # cancelOrder - отмена ордера
    # sendOrder - отправка ордера
    # getPrices - получение цен торгуемой пары
    # getKline - получение графика котировок для пары
    # остальные методы могут быть скрыты

    def __init__(self, key, secret, optkey, debug=False):
        self.key = key
        self.secret = secret
        self.passphrase = optkey
        self.deltaTime = 0.0
        response = self.__get('/api/general/v3/time')
        serverTime = float(response['epoch'])
        machineTime = time()
        self.coins = set()
        self.pairs = set()
        self.rules = dict()
        self.deltaTime = machineTime - serverTime
        self.debug = debug
        self.error = ''

    def debug_log(self, s):
        self.error = s

    # signature
    def __signature(self, timestamp, method, request_path, body):
        if str(body) == '{}' or str(body) == 'None':
            body = ''
        message = str(timestamp) + str.upper(method) + request_path + str(body)
        mac = hmac.new(bytes(self.secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d = mac.digest()
        return b64encode(d)

    # set request header
    def __header(self, sign, timestamp):
        header = dict()
        header['Content-Type'] = 'application/json'
        header['OK-ACCESS-KEY'] = self.key
        header['OK-ACCESS-SIGN'] = sign
        header['OK-ACCESS-TIMESTAMP'] = str(timestamp)
        header['OK-ACCESS-PASSPHRASE'] = self.passphrase
        return header

    def __parse_params_to_str(self, params):
        url = '?'
        for key, value in params.items():
            url = url + str(key) + '=' + urllib.parse.quote(str(value), safe='') + '&'
        return url[0:-1]

    def __get(self, request_path, params={}):
        correctTime = time() + timezone - self.deltaTime
        timestamp = strftime("%Y-%m-%dT%H:%M:%S", localtime(correctTime)) + '.000Z'
        base_url = 'https://www.okex.com'
        request_path = request_path + self.__parse_params_to_str(params)
        header = self.__header(self.__signature(timestamp, 'GET', request_path, None), timestamp)
        try:
            response = requests.get(base_url + request_path, headers=header)
        except:
            if self.debug:
                # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 201')
                self.debug_log('code: 201, url: ' + base_url + request_path)
            return False
        if response.status_code in [200, 400]:
            data = response.json()
            if 'error_code' in data:
                if data['error_code'] != '0':
                    self.debug_log('code ' + data['error_code'] + ': ' + data['error_message'])
                    return False
            return data  # Возвращаем JSON объект
        else:
            return False

    def __post(self, request_path, params):
        correctTime = time() + timezone - self.deltaTime
        timestamp = strftime("%Y-%m-%dT%H:%M:%S", localtime(correctTime)) + '.000Z'
        base_url = 'https://www.okex.com'
        request_path = request_path + self.__parse_params_to_str(params)
        url = base_url + request_path
        header = self.__header(self.__signature(timestamp, 'POST', request_path, json.dumps(params)), timestamp)
        body = json.dumps(params)
        try:
            response = requests.post(url, data=body, headers=header)
        except:
            if self.debug:
                # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202')
                self.debug_log('code: 202, url: ' + base_url + request_path)
            return False
        if response.status_code in [200, 400]:
            data = response.json()
            if 'error_code' in data:
                if data['error_code'] != '0':
                    self.debug_log('code ' + data['error_code'] + ': ' + data['error_message'])
                    return False
            return data  # Возвращаем JSON объект
        else:
            return False

    def getRules(self):
        # Получение правил биржи, монет и символов
        # pairs - set()
        # coins - set()
        # rules - dict()
        response = self.__get('/api/spot/v3/instruments')
        if not isinstance(response, list):
            return False
        if response:
            try:
                for i in range(len(response)):
                    baseAsset = response[i]['base_currency'].lower()
                    quoteAsset = response[i]['quote_currency'].lower()
                    pair = baseAsset + '_' + quoteAsset

                    self.coins.add(baseAsset)
                    self.coins.add(quoteAsset)
                    self.pairs.add(pair)

                    self.rules[pair] = {}
                    self.rules[pair]['symbol'] = response[i]['instrument_id']
                    self.rules[pair]['minPrice'] = 0
                    self.rules[pair]['maxPrice'] = 0
                    self.rules[pair]['minQty'] = float(response[i]['min_size'])
                    self.rules[pair]['maxQty'] = 0
                    self.rules[pair]['aroundPrice'] = int(abs(math.log10(float(response[i]['tick_size']))))
                    self.rules[pair]['aroundQty'] = int(abs(math.log10(float(response[i]['size_increment']))))
                    self.rules[pair]['minSum'] = 0
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

    def getPrice(self, **req):
        # Получение последней цены
        symbol = self.rules[req['pair']]['symbol']
        response = self.__get('/api/spot/v3/instruments/' + symbol + '/ticker')
        if not isinstance(response, dict):
            return False
        if response:
            try:
                return float(response['last'])
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
                    self.debug_log('code: 230. Get price false')
                return False
        return False

    def getDepth(self, **req):
        # Получение стакана
        # Сначала спредовые
        # depth = dict()
        params = {}
        params.update({'size': str(req['depth'])})
        symbol = self.rules[req['pair']]['symbol']
        response = self.__get('/api/spot/v3/instruments/' + symbol + '/book', params)
        if not isinstance(response, dict):
            return False
        if response:
            try:
                data = dict()
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

    # Авторизованные методы

    def getBalances(self, all=False):
        # Получение балансов
        response = self.__get('/api/spot/v3/accounts/')
        if not isinstance(response, list):
            return False
        if response:
            data = {}
            try:
                for coin in self.coins:
                    data[coin] = 0
                for i in range(len(response)):
                    coin = response[i]['currency'].lower()
                    if all:
                        data[coin] = float(response[i]['balance'])
                    else:
                        data[coin] = float(response[i]['available'])
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
        params = {'state': '7', 'instrument_id': symbol}
        params.update({'limit': '10'})
        response = self.__get('/api/spot/v3/orders', params)
        if not isinstance(response, list):
            return False
        if response:
            try:
                count = len(response)
                data = []
                j = 0
                for i in range(count):
                    if response[count - 1 - i]['filled_size'] != '0':
                        data.append({})
                        data[j]['pair'] = req['pair']
                        data[j]['side'] = response[count - 1 - i]['side']
                        data[j]['qty'] = float(response[count - 1 - i]['filled_size'])
                        data[j]['price'] = float(response[count - 1 - i]['price'])
                        data[j]['time'] = int(mktime(strptime(response[count - 1 - i]['timestamp'][:-5],
                                                              "%Y-%m-%dT%H:%M:%S"))) - timezone + self.deltaTime
                        j += 1
                return data if j > 0 else False
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 260')
                    self.debug_log('code: 260. Get trades false')
                return False

        else:
            return False

    def getOrders(self, **req):
        # Получение активных ордеров
        # Сначала старые, в конце новые
        symbol = self.rules[req['pair']]['symbol']
        params = {'state': '0', 'instrument_id': symbol}
        params.update({'limit': '10'})
        response = self.__get('/api/spot/v3/orders', params)
        if not isinstance(response, list):
            return False
        if response:
            try:
                count = len(response)
                data = []
                for i in range(count):
                    data.append({})
                    data[i]['id'] = response[count - 1 - i]['order_id']
                    data[i]['pair'] = req['pair']
                    data[i]['side'] = response[count - 1 - i]['side'].lower()
                    data[i]['qty'] = float(response[count - 1 - i]['size'])
                    data[i]['fill'] = float(response[count - 1 - i]['filled_size'])
                    data[i]['price'] = float(response[count - 1 - i]['price'])
                    data[i]['time'] = int(mktime(strptime(response[count - 1 - i]['created_at'][:-5],
                                                          "%Y-%m-%dT%H:%M:%S"))) - timezone + self.deltaTime
                return data if count > 0 else False
            except:
                if self.debug:
                    # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 270')
                    self.debug_log('code: 270. Get orders false')
                return False
        else:
            return False

    def cancelOrder(self, **req):
        # Отмена ордера
        # orderId
        symbol = self.rules[req['pair']]['symbol']
        params = {"instrument_id": symbol}
        response = self.__post('/api/spot/v3/cancel_orders/' + str(req['id']), params)

        if not isinstance(response, dict):
            return False
        try:
            return True if response['result'] is True else False
        except:
            if self.debug:
                # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 280')
                self.debug_log('code: 280. Cancel order false')
            return False

    def sendOrder(self, **req):
        # Отправка ордера
        # orderId
        symbol = self.rules[req['pair']]['symbol']
        params = {'type': 'limit', 'side': req['side'].lower(), 'size': str(req['qty']), 'price': str(req['price']),
                  'instrument_id': symbol}
        response = self.__post('/api/spot/v3/orders', params)

        if not isinstance(response, dict):
            return False
        try:
            return response['order_id'] if response['result'] is True else False
        except:
            if self.debug:
                # ~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
                self.debug_log('code: 290. Send order false')
            return False


# ~ https://www.okex.com/docs/en/
