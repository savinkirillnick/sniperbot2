import requests # Подключаем модуль для работы с HTTP запросами
import hmac # Подключаем модуль шифрования HMAC
import hashlib # Подключаем библиотеки шифрования
from time import time # Подключаем модуль работы с временем
import urllib.parse #  Подключение модуля работы с http строкой

class apiLivecoin:
	# Класс для работы с api binance
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
	
	def __init__(self, key, secret, debug=False):
		self.key = key
		self.secret = secret
		self.deltaTime = 0.0
		self.coins = set()
		self.pairs = set()
		self.rules = dict()
		self.signature = ''
		self.debug = debug
		self.error = False
		response = self.__query(method='get',url='https://api.livecoin.net/exchange/order_book', currencyPair='BTC/USDT', depth=1)
		serverTime = response['timestamp']
		self.deltaTime = time() - serverTime/1000

	def debug_log(self, s):
		self.error = s
		
	def __query(self, method, url, **req):
		# Функция отправки запроса (вспомогательная функция)
		if method == 'get':
			try:
				response = requests.get(url, params=sorted(req.items()), headers={'Api-key': self.key, 'Sign': self.signature})
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 201, url: '+url)
					self.debug_log('code: 201, url: '+url)
				return False
			if response.status_code in [200, 400]:
				data = response.json()
				if 'exception' in data:
					self.debug_log('code: ' + data['exception'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False
		if method == 'post':
			try:
				response = requests.post(url, data=sorted(req.items()), headers={'Api-key': self.key, 'Sign': self.signature, 'Content-type': 'application/x-www-form-urlencoded'})
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202, url: '+url)
					self.debug_log('code: 202, url: '+url)
				return False
			if response.status_code in [200, 400]:
				data = response.json()
				if 'exception' in data:
					self.debug_log('code: ' + data['exception'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False

	def __sign(self, **req):
		# Функция для шифрования подписи
		secret = self.secret.encode()
		data = urllib.parse.urlencode(sorted(req.items())).encode()
		return hmac.new(secret, data, hashlib.sha256).hexdigest().upper()
	
	def getRules(self):
		# Получение правил биржи, монет и символов
		# pairs - set()
		# coins - set()
		# rules - dict()
		response = self.__query(method='get',url='https://api.livecoin.net/exchange/restrictions')
		if not isinstance(response, dict):
			return False
		if response:
			count = len(response['restrictions'])
			try:
				for i in range(count):
					symbol = response['restrictions'][i]['currencyPair']
					values = symbol.split('/')
					baseAsset = values[0].lower()
					quoteAsset = values[1].lower()
					pair = baseAsset + '_' + quoteAsset
					
					self.coins.add(baseAsset)
					self.coins.add(quoteAsset)
					self.pairs.add(pair)
					
					self.rules[pair] = {}
					self.rules[pair]['symbol'] = symbol
					self.rules[pair]['minPrice'] = 0
					self.rules[pair]['maxPrice'] = 0
					self.rules[pair]['minQty'] = response['restrictions'][i]['minLimitQuantity']
					self.rules[pair]['maxQty'] = 0
					self.rules[pair]['aroundPrice'] = response['restrictions'][i]['priceScale']
					self.rules[pair]['aroundQty'] = 8
					self.rules[pair]['minSum'] = 0
					self.rules[pair]['maxSum'] = 0
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
		response = self.__query(method='get',url='https://api.livecoin.net/exchange/order_book', currencyPair=symbol, depth=req['depth'])
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
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 220')
					self.debug_log('code: 220. Get depth false')
				return False
		else:
			return False
	
	def getPrice(self, **req):
		# Получение последней цены
		symbol = self.rules[req['pair']]['symbol']
		response = self.__query(method='get',url='https://api.livecoin.net/exchange/ticker', currencyPair=symbol)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				return response['last']
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
					self.debug_log('code: 230. Get price false')
				return False	
		return False

	# Авторизованные методы
	
	def getBalances(self):
		# Получение балансов
		self.signature = self.__sign()
		response = self.__query(method='get', url='https://api.livecoin.net/payment/balances')
		if not isinstance(response, list):
			return False
		if response:
			data = {}
			try:
				count = len(response)
				for i in range(count):
					if response[i]['type'] == 'available':
						data[response[i]['currency'].lower()] = float(response[i]['value'])
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
		correctTime = round(time() - self.deltaTime) * 1000
		startTime = correctTime - 3600 * 24 * 1000
		self.signature = self.__sign(currencyPair=symbol, openClosed='CLOSED', issuedFrom=startTime, issuedTo=correctTime)
		response = self.__query(method='get', url='https://api.livecoin.net/exchange/client_orders', currencyPair=symbol, openClosed='CLOSED', issuedFrom=startTime, issuedTo=correctTime)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				count = len(response['data'])
				data = []
				for i in range(count):
					data.append({})
					data[i]['pair'] = req['pair']
					if response['data'][i]['type'] == 'LIMIT_BUY':
						data[i]['side'] = 'buy'
					elif response['data'][i]['type'] == 'LIMIT_SELL':
						data[i]['side'] = 'sell'
					data[i]['qty'] = response['data'][i]['quantity'] - response['data'][i]['remainingQuantity']
					data[i]['price'] = response['data'][i]['price']
					data[i]['time'] = response['data'][i]['lastModificationTime']/1000 + self.deltaTime
				return data if count > 0 else False
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 260')
					self.debug_log('code: 260. Get trades false')
				return False
		else:
			return False
		
	def getOrders(self, **req):
		# Получение активных ордеров
		# Сначала старые, в конце новые
		symbol = self.rules[req['pair']]['symbol']
		correctTime = round(time() - self.deltaTime) * 1000
		startTime = correctTime - 3600 * 24 * 1000
		self.signature = self.__sign(currencyPair=symbol, openClosed='OPEN', issuedFrom=startTime, issuedTo=correctTime)
		response = self.__query(method='get', url='https://api.livecoin.net/exchange/client_orders', currencyPair=symbol, openClosed='OPEN', issuedFrom=startTime, issuedTo=correctTime)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				count = len(response['data'])
				data = []
				for i in range(count):
					data.append({})
					data[i]['id'] = str(response['data'][i]['id'])
					data[i]['pair'] = req['pair']
					if response['data'][i]['type'] == 'LIMIT_BUY':
						data[i]['side'] = 'buy'
					elif response['data'][i]['type'] == 'LIMIT_SELL':
						data[i]['side'] = 'sell'
					data[i]['qty'] = response['data'][i]['quantity']
					data[i]['fill'] = response['data'][i]['quantity'] - response['data'][i]['remainingQuantity']
					data[i]['price'] = response['data'][i]['price']
					data[i]['time'] = response['data'][i]['issueTime']/1000 + self.deltaTime
				return data if count > 0 else False
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 270')
					self.debug_log('code: 270. Get orders false')
				return False
		else:
			return False
		
	def cancelOrder(self, **req):
		# Отмена ордера
		# orderId
		symbol = self.rules[req['pair']]['symbol']
		orderId = int(req['id'])
		self.signature = self.__sign(currencyPair=symbol, orderId=req['id'])
		response = self.__query(method='post', url='https://api.livecoin.net/exchange/cancellimit', currencyPair=symbol, orderId=orderId)
		if not isinstance(response, dict):
			return False
		try:
			return True if response['success'] is True else False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 280')
				self.debug_log('code: 280. Cancel order false')
			return False

	def sendOrder(self, **req):
		# Отправка ордера
		# orderId
		symbol = self.rules[req['pair']]['symbol']
		
		if req['side'] == 'buy':
			url = 'https://api.livecoin.net/exchange/buylimit'
		elif req['side'] == 'sell':
			url = 'https://api.livecoin.net/exchange/selllimit'
		
		self.signature = self.__sign(currencyPair=symbol, price=req['price'], quantity=req['qty'])
		response = self.__query(method='post', url=url, currencyPair=symbol, price=req['price'], quantity=req['qty'])
		if not isinstance(response, dict):
			return False
		try:
			return str(response['orderId']) if response['success'] is True else False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
				self.debug_log('code: 290. Send order false')
			return False

#~ https://www.livecoin.net/api

