import requests # Подключаем модуль для работы с HTTP запросами
import hmac # Подключаем модуль шифрования HMAC
import hashlib # Подключаем библиотеки шифрования
from time import time # Подключаем модуль работы с временем
import urllib.parse #  Подключение модуля работы с http строкой

class apiTidex:
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
		self.signedString = ''
		self.coins = set()
		self.pairs = set()
		self.rules = dict()
		self.error = False
		response = self.__query(req_method='get', url='https://api.tidex.com/api/3/info')
		serverTime = response['server_time']
		self.deltaTime = time() - serverTime
		self.debug = debug
	
	def debug_log(self, s):
		self.error = s
	
	def __query(self, req_method, url, **req):
		# Функция отправки запроса (вспомогательная функция)
		if req_method == 'get':
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
					self.debug_log('code ' + str(data['code']) + ': ' +  data['error'])
					return False
				else:
					return data  # Возвращаем JSON объект
			else:
				return False
		if req_method == 'post':
			try:
				response = requests.post(url, data=sorted(req.items()), headers={'Sign':self.signedString,'Key': self.key})
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202, url: '+url)
					self.debug_log('code: 202, url: '+url)
				return False
			if response.status_code in [200, 400]:
				data = response.json()
				if 'error' in data:
					self.debug_log('code ' + str(data['code']) + ': ' +  data['error'])
					return False
				else:
					return data  # Возвращаем JSON объект
			else:
				return False

	def __sign(self, **req):
		# Функция для шифрования подписи
		secret = self.secret.encode()
		data = urllib.parse.urlencode(sorted(req.items())).encode()
		return hmac.new(secret, data, hashlib.sha512).hexdigest()
	
	def getRules(self):
		# Получение правил биржи, монет и символов
		# pairs - set()
		# coins - set()
		# rules - dict()
		response = self.__query(req_method='get', url='https://api.tidex.com/api/3/info')
		if not isinstance(response, dict):
			return False
		if response:
			try:
				for symbol in response['pairs']:
					if response['pairs'][symbol]['hidden'] == 0:
						pair = symbol.lower()
						values = symbol.split('_')
						self.coins.add(values[0].lower())
						self.coins.add(values[1].lower())
						self.pairs.add(pair)
						
						self.rules[pair] = {}
						self.rules[pair]['symbol'] = symbol
						self.rules[pair]['minPrice'] = float(response['pairs'][symbol]['min_price'])
						self.rules[pair]['maxPrice'] = float(response['pairs'][symbol]['max_price'])
						self.rules[pair]['minQty'] = float(response['pairs'][symbol]['min_amount'])
						self.rules[pair]['maxQty'] = float(response['pairs'][symbol]['max_amount'])
						self.rules[pair]['aroundPrice'] = int(response['pairs'][symbol]['decimal_places'])
						self.rules[pair]['aroundQty'] = int(response['pairs'][symbol]['decimal_places'])
						self.rules[pair]['minSum'] = float(response['pairs'][symbol]['min_total'])
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
		depth = str(req['depth'])
		symbol = self.rules[req['pair']]['symbol']
		response = self.__query(req_method='get',url='https://api.tidex.com/api/3/depth/'+symbol, limit=depth)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = dict()
				data['asks'] = []
				data['bids'] = []
				num_asks = req['depth'] if req['depth'] < len(response[symbol]['asks']) else len(response[symbol]['asks'])
				num_bids = req['depth'] if req['depth'] < len(response[symbol]['bids']) else len(response[symbol]['bids'])
				for i in range(num_asks):
					data['asks'].append([])
					data['asks'][i].append(float(response[symbol]['asks'][i][0]))
					data['asks'][i].append(float(response[symbol]['asks'][i][1]))
				for i in range(num_bids):
					data['bids'].append([])
					data['bids'][i].append(float(response[symbol]['bids'][i][0]))
					data['bids'][i].append(float(response[symbol]['bids'][i][1]))
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
		response = self.__query(req_method='get',url='https://api.tidex.com/api/3/ticker/'+symbol)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				return response[symbol]['last']
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
					self.debug_log('code: 230. Get price false')
				return False	
		return False
	
	def getKline(self, **req):
		# Не поддерживается
		return False

	# Авторизованные методы
	
	def getBalances(self, all=False):
		# Получение балансов
		correctTime = round(time() - self.deltaTime)
		self.signedString = self.__sign(nonce=correctTime, method='getInfoExt')
		response = self.__query(req_method='post', url='https://api.tidex.com/tapi', nonce=correctTime, method='getInfoExt')
		if not isinstance(response, dict):
			return False
		if response:
			data = {}
			try:
				for symbol in response['return']['funds']:
					if all:
						data[symbol.lower()] = float(response['return']['funds'][symbol]['value']) + float(response['return']['funds'][symbol]['inOrders'])
					else:
						data[symbol.lower()] = float(response['return']['funds'][symbol]['value'])
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
		correctTime = round(time() - self.deltaTime)
		self.signedString = self.__sign(method='TradeHistory', nonce=correctTime, pair=symbol, count=10)
		response = self.__query(req_method='post', url='https://api.tidex.com/tapi', method='TradeHistory', nonce=correctTime, pair=symbol, count=10)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = []
				i = 0
				for item in response['return']:
					data.append({})
					data[i]['pair'] = req['pair']
					data[i]['side'] = response['return'][item]['type'].lower()
					data[i]['qty'] = response['return'][item]['amount']
					data[i]['price'] = response['return'][item]['rate']
					data[i]['time'] = response['return'][item]['timestamp'] + self.deltaTime
					i += 1
				return data if i > 0 else False
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
		correctTime = round(time() - self.deltaTime)
		self.signedString = self.__sign(method='ActiveOrders', nonce=correctTime, pair=symbol)
		response = self.__query(req_method='post', url='https://api.tidex.com/tapi', method='ActiveOrders', nonce=correctTime, pair=symbol)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = []
				i = 0
				for item in response['return']:
					data.append({})
					data[i]['id'] = item
					data[i]['pair'] = req['pair']
					data[i]['side'] = response['return'][item]['type'].lower()
					data[i]['qty'] = response['return'][item]['amount']
					data[i]['fill'] = 0.0
					data[i]['price'] = response['return'][item]['rate']
					data[i]['time'] = response['return'][item]['timestamp_created'] + self.deltaTime
					i += 1
				return data if i > 0 else False
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
		order_id = int(req['id'])
		correctTime = round(time() - self.deltaTime)
		self.signedString = self.__sign(method='CancelOrder', nonce=correctTime, order_id=order_id)
		response = self.__query(req_method='post', url='https://api.tidex.com/tapi', method='CancelOrder', nonce=correctTime, order_id=order_id)
		if not isinstance(response, dict):
			return False
		try:
			if response['success'] == 1:
				return True
			else:
				return False
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
		correctTime = round(time() - self.deltaTime)
		self.signedString = self.__sign(nonce=correctTime, pair=symbol, type=side, amount=qty, rate=price, method='Trade')
		response = self.__query(req_method='post', url='https://api.tidex.com/tapi', nonce=correctTime, pair=symbol, type=side, amount=qty, rate=price, method='Trade')
		if not isinstance(response, dict):
			return False
		try:
			return str(response['return']['order_id']) if response['success'] == 1 else False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
				self.debug_log('code: 290. Send order false')
			return False


#~ https://tidex.com/services/api-specification
