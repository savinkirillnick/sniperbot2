import requests # Подключаем модуль для работы с HTTP запросами
import hmac # Подключаем модуль шифрования HMAC
import hashlib # Подключаем библиотеки шифрования
from time import time, mktime, strptime # Подключаем модуль работы с временем


class apiCex:
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
	
	def __init__(self, key, secret, optkey, debug = False):
		self.key = key
		self.secret = secret
		self.username = optkey
		self.deltaTime = 0.0
		self.nonce = 0
		self.coins = set()
		self.pairs = set()
		self.rules = dict()
		self.error = False
		self.debug = debug
		response = self.__query(method='get',url='https://cex.io/api/order_book/BTC/USD/')
		serverTime = float(response['timestamp'])
		self.deltaTime = time() - serverTime

	def debug_log(self, s):
		self.error = s
		
	def __query(self, method, url, **req):
		# Функция отправки запроса (вспомогательная функция)
		if method == 'get':
			try:
				response = requests.get(url, params=sorted(req.items()))
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 201, url: '+url)
					self.debug_log('code: 201, url: '+url)
				return False
			if response.status_code in [200, 400]:
				data = response.json()
				if 'error' in data:
					self.debug_log('code: ' + data['error'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False
		if method == 'post':
			try:
				response = requests.post(url, data=sorted(req.items()), headers={'User-agent': 'bot-cex.io-' + self.username})
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202, url: '+url)
					self.debug_log('code: 202, url: '+url)
				return False
			if response.status_code in [200, 400]:
				data = response.json()
				if 'error' in data:
					self.debug_log('code: ' + data['error'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False
		
	def __sign(self, nonce):
		# Функция для шифрования подписи
		#~ secret = self.secret.encode()
		#~ data = urllib.parse.urlencode(sorted(req.items())).encode()
		#~ return hmac.new(secret, data, hashlib.sha256).hexdigest()
		string = nonce + self.username + self.key
		return hmac.new(self.secret.encode(), string.encode(), digestmod=hashlib.sha256).hexdigest().upper()
	
	def getRules(self):
		# Получение правил биржи, монет и символов
		# pairs - set()
		# coins - set()
		# rules - dict()
		response = self.__query(method='get', url='https://cex.io/api/currency_limits')
		if not isinstance(response, dict):
			return False
		if response:
			try:
				count = len(response['data']['pairs'])
				for i in range(count):
					baseAsset = response['data']['pairs'][i]['symbol1'].lower()
					quoteAsset = response['data']['pairs'][i]['symbol2'].lower()
					pair = baseAsset + '_' + quoteAsset
					symbol = response['data']['pairs'][i]['symbol1'] + '/' +response['data']['pairs'][i]['symbol2']
					
					self.coins.add(baseAsset)
					self.coins.add(quoteAsset)
					self.pairs.add(pair)
					
					self.rules[pair] = {}
					self.rules[pair]['symbol'] = symbol
					self.rules[pair]['minPrice'] = 0.0 if response['data']['pairs'][i]['minPrice'] is None else float(response['data']['pairs'][i]['minPrice'])
					self.rules[pair]['maxPrice'] = 0.0 if response['data']['pairs'][i]['maxPrice'] is None else float(response['data']['pairs'][i]['maxPrice'])
					self.rules[pair]['minQty'] = 0.0 if response['data']['pairs'][i]['minLotSize'] is None else float(response['data']['pairs'][i]['minLotSize'])
					self.rules[pair]['maxQty'] = 0.0 if response['data']['pairs'][i]['maxLotSize'] is None else float(response['data']['pairs'][i]['maxLotSize'])
					self.rules[pair]['aroundPrice'] = 8
					self.rules[pair]['aroundQty'] = 8
					self.rules[pair]['minSum'] = 0.0 if response['data']['pairs'][i]['minLotSizeS2'] is None else float(response['data']['pairs'][i]['minLotSizeS2'])
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

	def __upd(self, **req):
		pair = req['pair']
		self.rules[pair] = {}
		
		if req['ask'] < 0.001:
			aroundPrice = 8
		elif req['ask'] >= 0.001 and req['ask'] < 0.01:
			aroundPrice = 7
		elif req['ask'] >= 0.01 and req['ask'] < 0.1:
			aroundPrice = 6
		elif req['ask'] >= 0.1 and req['ask'] < 1:
			aroundPrice = 5
		elif req['ask'] >= 1 and req['ask'] < 10:
			aroundPrice = 4
		elif req['ask'] >= 10 and req['ask'] < 100:
			aroundPrice = 3
		else:
			aroundPrice = 2

		self.rules[pair]['aroundPrice'] = aroundPrice

	def getDepth(self, **req):
		# Получение стакана
		# Сначала спредовые
		# depth = dict()
		symbol = self.rules[req['pair']]['symbol']
		response = self.__query(method='get', url='https://cex.io/api/order_book/'+symbol+'/')
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
				self.__upd(pair=req['pair'], ask=data['asks'][0][0])
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
		response = self.__query(method='get',url='https://cex.io/api/ticker/'+symbol)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				return float(response['last'])
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
					self.debug_log('code: 230. Get price false')
				return False	
		return False

	# Авторизованные методы
	
	def getBalances(self, all=False):
		# Получение балансов
		nonce = str(round(time() - self.deltaTime))
		signedString = self.__sign(nonce)
		response = self.__query(method='post', url='https://cex.io/api/balance/', key=self.key, signature=signedString, nonce=nonce)
		if not isinstance(response, dict):
			return False
		if response:
			data = {}
			try:
				coins = self.getCoins()
				for item in coins:
					if all:
						data[item] = float(response[item.upper()]['available']) + float(response[item.upper()]['orders'])
					else:
						data[item] = float(response[item.upper()]['available'])
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
		nonce = str(round(time() - self.deltaTime))
		signedString = self.__sign(nonce)
		dateTo = round(time() - self.deltaTime)
		dateFrom = dateTo - 86400
		
		response = self.__query(method='get', url='https://cex.io/api/archived_orders/'+symbol, key=self.key, nonce=nonce, signature=signedString, dateTo=dateTo, dateFrom=dateFrom, lastTxDateTo=dateTo, lastTxDateFrom=dateFrom, limit=10)
		if not isinstance(response, list):
			return False
		if response:
			try:
				count = len(response)
				data = []
				j = 0
				for i in range(count):
					if response[i]['status'] == 'd' or response[i]['status'] == 'cd':
						data.append({})
						data[j]['pair'] = req['pair']
						data[j]['side'] = response[i]['type']
						data[j]['qty'] = float(response[i]['amount']) - float(response[i]['remains'])
						data[j]['price'] = float(response[i]['price'])
						data[j]['time'] = mktime(strptime(response[i]['lastTxTime'][:-5], "%Y-%m-%dT%H:%M:%S")) + self.deltaTime
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
		symbol = self.rules[req['pair']]['symbol']
		nonce = str(round(time() - self.deltaTime))
		signedString = self.__sign(nonce)
		response = self.__query(method='get', url='https://cex.io/api/open_orders/'+symbol, key=self.key, nonce=nonce, signature=signedString)
		if not isinstance(response, list):
			return False
		if response:
			try:
				count = len(response)
				data = []
				j = 0
				for i in range(count):
					if float(response[i]['pending']) > 0:
						data.append({})
						data[j]['id'] = response[i]['id']
						data[j]['pair'] = req['pair']
						data[j]['side'] = response[i]['type']
						data[j]['qty'] = float(response[i]['amount'])
						data[j]['fill'] = float(response[i]['amount']) - float(response[i]['pending'])
						data[j]['price'] = float(response[i]['price'])
						data[j]['time'] = response[i]['time']/1000 + self.deltaTime
						j += 1
				return data if j > 0 else False
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
		orderId = int(req['id'])
		nonce = str(round(time() - self.deltaTime))
		signedString = self.__sign(nonce)
		response = self.__query(method='post', url='https://cex.io/api/cancel_order/', key=self.key, nonce=nonce, id=orderId, signature=signedString)
		try:
			return True if response is True and isinstance(response, bool) else False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 280')
				self.debug_log('code: 280. Cancel order false')
			return False

	def sendOrder(self, **req):
		# Отправка ордера
		# orderId
		symbol = self.rules[req['pair']]['symbol']
		side = req['side'].lower()
		qty = req['qty']
		price = req['price']
		nonce = str(round(time() - self.deltaTime))
		signedString = self.__sign(nonce)
		response = self.__query(method='post', url='https://cex.io/api/place_order/'+symbol, key=self.key, nonce=nonce, type=side, amount=qty, price=price, signature=signedString)
		if not isinstance(response, dict):
			return False
		try:
			return response['id']
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
				self.debug_log('code: 290. Send order false')
			return False


#~ https://cex.io/rest-api
