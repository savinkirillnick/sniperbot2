import requests # Подключаем модуль для работы с HTTP запросами
import hmac # Подключаем модуль шифрования HMAC
import hashlib # Подключаем библиотеки шифрования
from time import time, mktime, strptime, timezone # Подключаем модуль работы с временем
import urllib.parse #  Подключение модуля работы с http строкой


class apiDovewallet:
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
	
	def __init__(self, key, secret, debug = False):
		self.key = key
		self.secret = secret
		self.debug = debug
		self.deltaTime = 0.0
		self.signedString = ''
		self.coins = set()
		self.pairs = set()
		self.rules = dict()
		self.nonce = 0
		self.error = False
		machineTime = time()
		response = self.__query(req_method='get', url='https://api.dovewallet.com/v1.1/public/getmarketsummaries')
		serverTime = 0.0
		for i in range(len(response['result'])):
			if response['result'][i]['TimeStamp'] is not None:
				tempTime = mktime(strptime(response['result'][i]['TimeStamp'][:-3], "%Y-%m-%dT%H:%M:%S"))
				if tempTime > serverTime:
					serverTime = tempTime
		self.deltaTime = machineTime - serverTime + timezone
	
	def debug_log(self, s):
		self.error = s
	
	def __query(self, req_method, url, **req):
		# Функция отправки запроса (вспомогательная функция)
		if req_method == 'get':
			try:
				response = requests.get(url, params=sorted(req.items()), headers={'apisign': self.signedString})
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 201, url: '+url)
					self.debug_log('code: 201, url: '+url)
				return False
			if response.status_code == 200 or response.status_code == 400:
				data = response.json()
				if data['success'] is False:
					self.debug_log('code: None ' + req_method +': ' + url +': ' + data['message'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False

	def __sign(self, url, **req):
		# Функция для шифрования подписи
		secret = self.secret.encode()
		data = urllib.parse.urlencode(sorted(req.items())).encode()
		return hmac.new(secret, url.encode()+b'?'+data, hashlib.sha512).hexdigest()

	def getRules(self):
		# Получение правил биржи, монет и символов
		# pairs - set()
		# coins - set()
		# rules - dict()
		response = self.__query(req_method='get', url='https://api.dovewallet.com/v1.1/public/getmarkets')
		if not isinstance(response, dict):
			return False
		if response:
			try:
				count = len(response['result'])
				for i in range(count):
					if response['result'][i]['IsActive'] is True:
						baseAsset = response['result'][i]['BaseCurrency'].lower()
						quoteAsset = response['result'][i]['MarketCurrency'].lower()
						pair = quoteAsset + '_' + baseAsset
						
						self.coins.add(baseAsset)
						self.coins.add(quoteAsset)
						self.pairs.add(pair)
						
						self.rules[pair] = {}
						self.rules[pair]['symbol'] = response['result'][i]['MarketName']
						self.rules[pair]['minPrice'] = 0.0
						self.rules[pair]['maxPrice'] = 0.0
						self.rules[pair]['minQty'] = float(response['result'][i]['MinTradeSize'])
						self.rules[pair]['maxQty'] = 0.0
						self.rules[pair]['aroundPrice'] = 9
						self.rules[pair]['aroundQty'] = 9
						self.rules[pair]['minSum'] = 0.0
						self.rules[pair]['maxSum'] = 0.0
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
		depth = str(req['depth'])
		symbol = self.rules[req['pair']]['symbol'].lower()
		#~ value = symbol.split('-')
		response = self.__query(req_method='get',url='https://api.dovewallet.com/v1.1/public/getorderbook?market='+symbol+'&type=both')
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = dict()
				data['asks'] = []
				data['bids'] = []
				num_asks = req['depth'] if req['depth'] < len(response['result']['sell']) else len(response['result']['sell'])
				num_bids = req['depth'] if req['depth'] < len(response['result']['buy']) else len(response['result']['buy'])
				for i in range(num_asks):
					data['asks'].append([])
					data['asks'][i].append(float(response['result']['sell'][i]['Rate']))
					data['asks'][i].append(float(response['result']['sell'][i]['Quantity']))
				for i in range(num_bids):
					data['bids'].append([])
					data['bids'][i].append(float(response['result']['buy'][i]['Rate']))
					data['bids'][i].append(float(response['result']['buy'][i]['Quantity']))
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
		symbol = self.rules[req['pair']]['symbol'].lower()
		#~ value = symbol.split('-')
		response = self.__query(req_method='get',url='https://api.dovewallet.com/v1.1/public/getticker?market='+symbol)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				return response['result']['Last']
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
					self.debug_log('code: 230. Get price false')
				return False	
		return False
	
	# Авторизованные методы
	
	def getBalances(self, all=False):
		# Получение балансов
		correctTime = round(time() - self.deltaTime)
		self.signedString = self.__sign(url='https://api.dovewallet.com/v1.1/account/getbalances', apikey=self.key, nonce=str(correctTime))
		response = self.__query(req_method='get', url='https://api.dovewallet.com/v1.1/account/getbalances', apikey=self.key, nonce=str(correctTime))
		if not isinstance(response, dict):
			return False
		if response:
			data = {}
			try:
				for coin in self.coins:
					data[coin] = 0
				for i in range(len(response['result'])):
					coin = response['result'][i]['Currency'].lower()
					if all:
						data[coin] = float(response['result'][i]['Balance'])
					else:
						data[coin] = float(response['result'][i]['Available'])
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
		symbol = self.rules[req['pair']]['symbol'].lower()
		correctTime = round(time() - self.deltaTime)
		self.signedString = self.__sign(url='https://api.dovewallet.com/v1.1/account/getorderhistory', apikey=self.key, market=symbol, nonce=correctTime, count=10)
		response = self.__query(req_method='get', url='https://api.dovewallet.com/v1.1/account/getorderhistory', apikey=self.key, market=symbol, nonce=correctTime, count=10)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = []
				count = len(response['result'])
				j = 0
				for i in range(count):
					if response['result'][count-1-i]['PricePerUnit'] is not None:
						data.append({})
						data[j]['pair'] = req['pair']
						if response['result'][count-1-i]['OrderType'] == 'LIMIT_BUY':
							data[j]['side'] = 'buy'
						elif response['result'][count-1-i]['OrderType'] == 'LIMIT_SELL':
							data[j]['side'] = 'sell'
						data[j]['qty'] = response['result'][count-1-i]['Quantity'] - response['result'][count-1-i]['QuantityRemaining']
						data[j]['price'] = response['result'][count-1-i]['Limit']
						data[j]['time'] = mktime(strptime(response['result'][count-1-i]['TimeStamp'][:-3], "%Y-%m-%dT%H:%M:%S")) - timezone + self.deltaTime
						j += 1
				return data if j > 0 else False
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
		symbol = self.rules[req['pair']]['symbol'].lower()
		correctTime = round(time() - self.deltaTime)
		self.signedString = self.__sign(url='https://api.dovewallet.com/v1.1/market/getopenorders', apikey=self.key, market=symbol, nonce=correctTime)
		response = self.__query(req_method='get', url='https://api.dovewallet.com/v1.1/market/getopenorders', apikey=self.key, market=symbol, nonce=correctTime)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = []
				count = len(response['result'])
				for i in range(count):
					data.append({})
					data[i]['id'] = str(response['result'][count-1-i]['OrderUuid'])
					data[i]['pair'] = req['pair']
					if response['result'][count-1-i]['OrderType'] == 'LIMIT_BUY':
						data[i]['side'] = 'buy'
					elif response['result'][count-1-i]['OrderType'] == 'LIMIT_SELL':
						data[i]['side'] = 'sell'
					data[i]['qty'] = response['result'][count-1-i]['Quantity']
					data[i]['fill'] = response['result'][count-1-i]['Quantity'] - response['result'][count-1-i]['QuantityRemaining']
					data[i]['price'] = response['result'][count-1-i]['Limit']
					data[i]['time'] = mktime(strptime(response['result'][count-1-i]['Opened'][:-3], "%Y-%m-%dT%H:%M:%S")) - time.timezone + self.deltaTime
				return data
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
		uuid = int(req['id'])
		correctTime = round(time() - self.deltaTime)
		self.signedString = self.__sign(url='https://api.dovewallet.com/v1.1/market/cancel', apikey=self.key, uuid=uuid, nonce=correctTime)
		response = self.__query(req_method='get', url='https://api.dovewallet.com/v1.1/market/cancel', apikey=self.key, uuid=uuid, nonce=correctTime)
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
		symbol = self.rules[req['pair']]['symbol'].lower()
		#~ value = symbol.split('-')
		#~ market = value[1]+'-'+value[0]
		side = req['side'].lower()
		qty = req['qty']
		price = req['price']
		correctTime = round(time() - self.deltaTime)

		if side == 'buy':
			self.signedString = self.__sign(url='https://api.dovewallet.com/v1.1/market/buylimit', apikey=self.key, market=symbol, nonce=correctTime, quantity=qty, rate=price)
			response = self.__query(req_method='get', url='https://api.dovewallet.com/v1.1/market/buylimit', apikey=self.key, market=symbol, nonce=correctTime, quantity=qty, rate=price)
		elif side == 'sell':
			self.signedString = self.__sign(url='https://api.dovewallet.com/v1.1/market/selllimit', apikey=self.key, market=symbol, nonce=correctTime, quantity=qty, rate=price)
			response = self.__query(req_method='get', url='https://api.dovewallet.com/v1.1/market/selllimit', apikey=self.key, market=symbol, nonce=correctTime, quantity=qty, rate=price)
		else:
			response = False

		if not isinstance(response, dict):
			return False
		try:
			return str(response['result']['uuid']) if response['success'] is True else False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
				self.debug_log('code: 290. Send order false')
			return False

#~ https://developer.dovewallet.com/api/v1/
