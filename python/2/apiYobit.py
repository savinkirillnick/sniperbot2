import requests # Подключаем модуль для работы с HTTP запросами
import hmac # Подключаем модуль шифрования HMAC
import hashlib # Подключаем библиотеки шифрования
from time import time # Подключаем модуль работы с временем
import urllib.parse #  Подключение модуля работы с http строкой

class apiYobit:
	# Класс для работы с api yobit
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
		self.coins = set()
		self.pairs = set()
		self.rules = dict()
		self.error = False

	def debug_log(self, s):
		self.error = s
	
	# signature
	def __signature(self, req):
		secret = self.secret.encode()
		data = urllib.parse.urlencode(sorted(req.items())).encode()
		return hmac.new(secret, data, hashlib.sha512).hexdigest()

	def __get(self, url):
		try:
			response = requests.get(url)
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 201')
				self.debug_log('code: 201, url: '+url)
			return False
		if response.status_code in [200, 400]:
			data = response.json()
			if 'error' in data:
				self.debug_log('code: ' + data['error'])
				return False
			else:
				return data  # Возвращаем JSON объект
		else:
			return False

	def __post(self, **req):
		nonce = str(round(time()))
		req['nonce'] = nonce
		sign = self.__signature(req)
		try:
			response = requests.post('https://yobit.net/tapi', data=sorted(req.items()), headers={'Content-Type':'application/x-www-form-urlencoded','Key':self.key,'Sign':sign})
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202')
				self.debug_log('code: 202, url: https://yobit.net/tapi')
			return False
		if response.status_code in [200, 400]:
			data = response.json()
			if 'error' in data:
				self.debug_log('code: ' + data['error'])
				return False
			else:
				return data  # Возвращаем JSON объект
		else:
			return False

	def getRules(self):
		# Получение правил биржи, монет и символов
		# pairs - set()
		# coins - set()
		# rules - dict()
		response = self.__get('https://yobit.net/api/3/info')
		if not isinstance(response, dict):
			return False
		if response:
			serverTime = float(response['server_time'])
			machineTime = time()
			self.deltaTime = machineTime - serverTime
			try:
				for pair in response['pairs']:
					if response['pairs'][pair]['hidden'] == 0:
						values = pair.split('_')
						baseAsset = values[0]
						quoteAsset = values[1]
						self.coins.add(baseAsset)
						self.coins.add(quoteAsset)
						self.pairs.add(pair)
						
						self.rules[pair] = {}
						self.rules[pair]['symbol'] = pair
						self.rules[pair]['minPrice'] = float(response['pairs'][pair]['min_price'])
						self.rules[pair]['maxPrice'] = float(response['pairs'][pair]['max_price'])
						self.rules[pair]['minQty'] = float(response['pairs'][pair]['min_amount'])
						self.rules[pair]['maxQty'] = 0
						self.rules[pair]['aroundPrice'] = int(response['pairs'][pair]['decimal_places'])
						self.rules[pair]['aroundQty'] = int(response['pairs'][pair]['decimal_places'])
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

	def getPrice(self, **req):
		# Получение последней цены
		symbol = self.rules[req['pair']]['symbol']
		response = self.__get('https://yobit.net/api/3/ticker/' + symbol)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				return float(response[symbol]['last'])
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
					self.debug_log('code: 230. Get price false')
				return False	
		return False

	def getDepth(self, **req):
		# Получение стакана
		# Сначала спредовые
		# depth = dict()
		symbol = self.rules[req['pair']]['symbol']
		response = self.__get('https://yobit.net/api/3/depth/' + symbol)
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

	# Авторизованные методы
	
	def getBalances(self, all=False):
		# Получение балансов
		response = self.__post(method='getInfo')
		if not isinstance(response, dict):
			return False
		if response:
			data = {}
			try:
				for coin in self.coins:
					data[coin] = 0
				for coin in response['return']['funds']:
					data[coin] = float(response['return']['funds'][coin])
					if all:
						data[coin] += float(response['return']['funds_incl_orders'][coin])
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
		response = self.__post(method='TradeHistory', pair=symbol, count=10, order='ASC')
		
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = []
				j = 0
				for i in response['return']:
					data.append({})
					data[j]['pair'] = req['pair']
					data[j]['side'] = response['return'][i]['type'].lower()
					data[j]['qty'] = float(response['return'][i]['amount'])
					data[j]['price'] = float(response['return'][i]['rate'])
					data[j]['time'] = float(response['return'][i]['timestamp']) + self.deltaTime
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
		response = self.__post(method='ActiveOrders', pair=symbol)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = []
				j = 0
				for i in response['return']:
					data.append({})
					data[j]['id'] = i
					data[j]['pair'] = req['pair']
					data[j]['side'] = response['return'][i]['type'].lower()
					data[j]['qty'] = float(response['return'][i]['amount'])
					data[j]['fill'] = 0.0
					data[j]['price'] = float(response['return'][i]['rate'])
					data[j]['time'] = float(response['return'][i]['timestamp_created']) + self.deltaTime
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
		symbol = self.rules[req['pair']]['symbol']
		order_id = int(req['id'])
		response = self.__post(method='CancelOrder', order_id=order_id)
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
		response = self.__post(method='Trade', pair=symbol, type=req['side'], rate=req['price'], amount=req['qty'])
		
		if not isinstance(response, dict):
			return False
		try:
			return str(response['return']['order_id']) if response['success'] == 1 else False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
				self.debug_log('code: 290. Send order false')
			return False


#~ https://yobit.net/ru/api/
