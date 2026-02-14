import requests # Подключаем модуль для работы с HTTP запросами
import json # Подключаем модуль для работы с объектами json
import math # Подключаем модуль для математических операций
import hmac # Подключаем модуль шифрования HMAC
import hashlib # Подключаем библиотеки шифрования
from time import time # Подключаем модуль работы с временем
import urllib.parse #  Подключение модуля работы с http строкой
import base64 # Подключаем кодирование 64
import uuid # Подключаем библиотеку генерации уникальных id

class apiKucoin:
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
	def __init__(self, key, secret, optkey, debug = False):
		self.key = key
		self.secret = secret
		self.passphrase = optkey
		self.correctTime = ''
		self.coins = set()
		self.pairs = set()
		self.rules = dict()
		self.debug = False
		self.error = False

		response = self.__query(method='get',url='https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT', signature=False)
		
		serverTime = response['data']['time']
		self.deltaTime = time() - serverTime/1000
		
		self.debug = debug
	
	def debug_log(self, s):
		self.error = s
		
	def __query(self, method, url, signature, **req):
		# Функция отправки запроса (вспомогательная функция)
		
		if method == 'get':
			try:
				if signature == False:
					response = requests.get(url, params=sorted(req.items()))
				else:
					data_json = json.dumps(req)
					response = requests.get(url, params=sorted(req.items()), headers={'KC-API-KEY': self.key, 'KC-API-SIGN': signature, 'KC-API-TIMESTAMP': self.correctTime, 'KC-API-PASSPHRASE': self.passphrase, 'Content-Type': 'application/json'})
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 201, url: '+url)
					self.debug_log('code: 201, url: '+url)
				return False
			if response.status_code == 200 or response.status_code == 400 or response.status_code == 401:
				data = response.json()
				if response.status_code == 401:
					self.debug_log('code ' + data['code'] + ': ' + data['msg'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False
		if method == 'post':
			try:
				response = requests.post(url=url, data=req['data_json'], headers={'KC-API-KEY': self.key, 'KC-API-SIGN': signature, 'KC-API-TIMESTAMP': self.correctTime, 'KC-API-PASSPHRASE': self.passphrase, 'Content-Type': 'application/json'})
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202, url: '+url)
					self.debug_log('code: 202, url: '+url)
				return False
			if response.status_code == 200 or response.status_code == 400 or response.status_code == 401:
				data = response.json()
				if response.status_code == 401:
					self.debug_log('code ' + data['code'] + ': ' + data['msg'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False
		if method == 'delete':
			try:
				response = requests.delete(url, data=sorted(req.items()), headers={'KC-API-KEY': self.key, 'KC-API-SIGN': signature, 'KC-API-TIMESTAMP': self.correctTime, 'KC-API-PASSPHRASE': self.passphrase, 'Content-Type': 'application/json'})
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 203, url: '+url)
					self.debug_log('code: 203, url: '+url)
				return False
			if response.status_code == 200 or response.status_code == 400 or response.status_code == 401:
				data = response.json()
				if response.status_code == 401:
					self.debug_log('code ' + data['code'] + ': ' + data['msg'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False

	def __sign(self, timestamp, method, request_path, body=False):
		# Функция для шифрования подписи
		if body != False:
			message = timestamp + method + request_path + body
		else:
			message = timestamp + method + request_path
		secret = self.secret.encode('utf-8')
		data = message.encode('utf-8')
		h = hmac.new(secret, data, hashlib.sha256).digest()
		return base64.b64encode(h)
	
	def getRules(self):
		# Получение правил биржи, монет и символов
		# pairs - set()
		# coins - set()
		# rules - dict()
		response = self.__query(method='get',url='https://api.kucoin.com/api/v1/symbols', signature=False)
		if type(response) != type(dict()):
			return False
		if response != False:
			try:
				for i in range(len(response['data'])):
					if response['data'][i]['enableTrading'] == True:
						
						baseAsset = response['data'][i]['baseCurrency'].lower()
						quoteAsset = response['data'][i]['quoteCurrency'].lower()
						pair = baseAsset + '_' + quoteAsset
						
						self.coins.add(baseAsset)
						self.coins.add(quoteAsset)
						self.pairs.add(pair)
						
						self.rules[pair] = {}
						self.rules[pair]['symbol'] = response['data'][i]['symbol']
						self.rules[pair]['minPrice'] = 0.0
						self.rules[pair]['maxPrice'] = 0.0
						self.rules[pair]['minQty'] = float(response['data'][i]['baseMinSize'])
						self.rules[pair]['maxQty'] = float(response['data'][i]['baseMaxSize'])
						self.rules[pair]['aroundPrice'] = int(abs(math.log10(float(response['data'][i]['priceIncrement']))))
						self.rules[pair]['aroundQty'] = int(abs(math.log10(float(response['data'][i]['baseIncrement']))))
						self.rules[pair]['minSum'] = float(response['data'][i]['quoteMinSize'])
						self.rules[pair]['maxSum'] = float(response['data'][i]['quoteMaxSize'])
				self.coins = list(self.coins)
				self.coins.sort()
				self.pairs = list(self.pairs)
				self.pairs.sort()
				return self.rules
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 210')
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
		symbol = self.rules[req['pair']]['symbol']
		response = self.__query(method='get',url='https://api.kucoin.com/api/v1/market/orderbook/level1', signature=False, symbol=symbol)
		if type(response) != type(dict()):
			return False
		if response != False:
			try:
				data = {}
				data['asks'] = []
				data['bids'] = []
				data['asks'].append([])
				data['asks'][0].append(float(response['data']['bestAsk']))
				data['asks'][0].append(float(response['data']['bestAskSize']))
				data['bids'].append([])
				data['bids'][0].append(float(response['data']['bestBid']))
				data['bids'][0].append(float(response['data']['bestBidSize']))
				for i in range(4):
					data['asks'].append([0.0,0.0])
					data['bids'].append([0.0,0.0])
				return data
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 220')
					self.debug_log('code: 220. Get depth false')
				return False
		else:
			return False
	
	def getPrice(self, **req):
		# Получение последней цены
		symbol = self.rules[req['pair']]['symbol']
		response = self.__query(method='get',url='https://api.kucoin.com/api/v1/market/orderbook/level1', signature=False, symbol=symbol)
		if type(response) != type(dict()):
			return False
		if response != False:
			try:
				return float(response['data']['price'])
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
					self.debug_log('code: 230. Get price false')
				return False	
		return False

	# Авторизованные методы
	
	def getBalances(self, all=False):
		# Получение балансов
		self.correctTime = str(round(time() - self.deltaTime) * 1000)
		signedString = self.__sign(timestamp=self.correctTime, method='GET', request_path='/api/v1/accounts', body=False)
		response = self.__query(method='get', url='https://api.kucoin.com/api/v1/accounts', signature=signedString)

		if type(response) != type(dict()):
			return False
		if response != False:
			data = {}
			try:
				for coin in self.coins:
					data[coin] = 0
				for i in range(len(response['data'])):
					if response['data'][i]['type'] == 'trade':
						if all:
							data[response['data'][i]['currency'].lower()] = float(response['data'][i]['balance'])
						else:
							data[response['data'][i]['currency'].lower()] = float(response['data'][i]['available'])
				return data
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 250')
					self.debug_log('code: 250. Get balances false')
				return False
		else:
			return False
		
	def getTrades(self, **req):
		# Получение истории ордеров
		# Сначала старые, в конце новые
		symbol = self.rules[req['pair']]['symbol']
		self.correctTime = str(round((time() - self.deltaTime) * 1000))
		params = {'status': 'done', 'symbol': symbol, 'type': 'limit'}
		
		data = urllib.parse.urlencode(sorted(params.items()))
		
		signedString = self.__sign(timestamp=self.correctTime, method='GET', request_path='/api/v1/orders?'+data)
		response = self.__query(method='get', url='https://api.kucoin.com/api/v1/orders', signature=signedString, status='done', symbol=symbol, type='limit')
		if type(response) != type(dict()):
			return False
		if response != False:
			try:
				data = []
				count = len(response['data']['items']) if len(response['data']['items']) < 10 else 10
				j = 0
				for i in range(count):
					if float(response['data']['items'][count-1-i]['dealSize']) > 0.0:
						data.append({})
						data[j]['pair'] = req['pair']
						data[j]['side'] = response['data']['items'][count-1-i]['side']
						data[j]['qty'] = float(response['data']['items'][count-1-i]['dealSize'])
						data[j]['price'] = float(response['data']['items'][count-1-i]['price'])
						data[j]['time'] = response['data']['items'][count-1-i]['createdAt']/1000 + self.deltaTime
						j += 1
				return data if j > 0 else False
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 260')
					self.debug_log('code: 260. Get trades false')
				return False
		else:
			return False
		return False

		
	def getOrders(self, **req):
		# Получение активных ордеров
		# Сначала старые, в конце новые
		symbol = self.rules[req['pair']]['symbol']
		self.correctTime = str(round((time() - self.deltaTime) * 1000))
		params = {'status': 'active', 'symbol': symbol, 'type': 'limit'}
		
		data = urllib.parse.urlencode(sorted(params.items()))
		
		signedString = self.__sign(timestamp=self.correctTime, method='GET', request_path='/api/v1/orders?'+data)
		response = self.__query(method='get', url='https://api.kucoin.com/api/v1/orders', signature=signedString, status='active', symbol=symbol, type='limit')
		if type(response) != type(dict()):
			return False
		if response != False:
			try:
				data = []
				count = len(response['data']['items']) if len(response['data']['items']) < 10 else 10
				for i in range(count):
					data.append({})
					data[i]['id'] = response['data']['items'][count-1-i]['id']
					data[i]['pair'] = req['pair']
					data[i]['side'] = response['data']['items'][count-1-i]['side']
					data[i]['qty'] = float(response['data']['items'][count-1-i]['size'])
					data[i]['fill'] = float(response['data']['items'][count-1-i]['dealSize'])
					data[i]['price'] = float(response['data']['items'][count-1-i]['price'])
					data[i]['time'] = response['data']['items'][count-1-i]['createdAt']/1000 + self.deltaTime
				return data if count > 0 else False
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 270')
					self.debug_log('code: 270. Get orders false')
				return False
		else:
			return False
		return False
		
	def cancelOrder(self, **req):
		# Отмена ордера
		# orderId
		orderId = req['id']
		self.correctTime = str(round((time() - self.deltaTime) * 1000))
		signedString = self.__sign(timestamp=self.correctTime, method='DELETE', request_path='/api/v1/orders/' + orderId)
		
		response = self.__query(method='delete', url='https://api.kucoin.com/api/v1/orders/'+orderId, signature=signedString)

		if type(response) != type(dict()):
			return False
		try:
			if response['data']['cancelledOrderIds'][0] == orderId:
				return True
			else:
				return False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 280')
				self.debug_log('code: 280. Cancel order false')
			return False
		return False

	def sendOrder(self, **req):
		# Отправка ордера
		# orderId
		clientOrderId = str(uuid.uuid4()).replace('-', '')
		symbol = self.rules[req['pair']]['symbol']
		
		aroundPrice = self.rules[req['pair']]['aroundPrice']
		aroundQty = self.rules[req['pair']]['aroundQty']
		
		formatPrice = '{:.'+str(aroundPrice)+'f}'
		formatQty = '{:.'+str(aroundQty)+'f}'

		amount = str(formatQty.format(req['qty']))
		price = str(formatPrice.format(req['price']))

		self.correctTime = str(round((time() - self.deltaTime) * 1000))
		params = {'clientOid': clientOrderId, 'price': price, 'side': req['side'].lower(), 'size': amount, 'symbol': symbol, 'type': 'limit'}
		data_json = json.dumps(params)
		signedString = self.__sign(timestamp=self.correctTime, method='POST', request_path='/api/v1/orders', body=data_json)
		response = self.__query(method='post', url='https://api.kucoin.com/api/v1/orders', signature=signedString, data_json=data_json)

		if type(response) != type(dict()):
			return False
		try:
			return response['data']['orderId']
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
				self.debug_log('code: 290. Send order false')
			return False
		return False


#~ https://docs.kucoin.com/
