import requests # Подключаем модуль для работы с HTTP запросами
import hmac # Подключаем модуль шифрования HMAC
import hashlib # Подключаем библиотеки шифрования
from time import time, localtime, strftime # Подключаем модуль работы с временем
import urllib.parse #  Подключение модуля работы с http строкой

class apiExmo:
	# Класс для работы с api exmo
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
		self.nonce = round(time())
		self.debug = debug
		self.deltaTime = 0.0
		self.signedString = ''
		self.coins = set()
		self.pairs = set()
		self.rules = dict()
		self.error = False

		response = self.__query(method='get', url='https://api.exmo.com/v1.1/ticker')
		if not isinstance(response, dict):
			return None
		if response:
			try:
				serverTime = response['BTC_USDT']['updated']
				self.deltaTime = time() - serverTime
			except:
				if self.debug:
					print(strftime('%m/%d %H:%M ', localtime()) + 'code: 200')
				return None
				
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
					self.debug_log('code' + data['error'][5:])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False
		if method == 'post':
			try:
				response = requests.post(url, data=sorted(req.items()), headers={'Content-Type': 'application/x-www-form-urlencoded', 'Key': self.key, 'Sign': self.signedString})
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202, url: '+url)
					self.debug_log('code: 202, url: '+url)
				return False
			if response.status_code in [200, 400]:
				data = response.json()
				if 'error' in data:
					self.debug_log('code' + data['error'][5:])
					return False
				else:
					return data # Возвращаем JSON объект
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
		response = self.__query(method='get',url='https://api.exmo.com/v1.1/pair_settings/')
		if not isinstance(response, dict):
			return False
		if response:
			try:
				for symbol in response:
					pair = symbol.lower()
					values = symbol.split('_')
					self.coins.add(values[0].lower())
					self.coins.add(values[1].lower())
					self.pairs.add(pair)
					
					self.rules[pair] = {}
					self.rules[pair]['symbol'] = symbol
					self.rules[pair]['minPrice'] = float(response[symbol]['min_price'])
					self.rules[pair]['maxPrice'] = float(response[symbol]['max_price'])
					self.rules[pair]['minQty'] = float(response[symbol]['min_quantity'])
					self.rules[pair]['maxQty'] = float(response[symbol]['max_quantity'])
					self.rules[pair]['aroundPrice'] = 8
					self.rules[pair]['aroundQty'] = 8
					self.rules[pair]['minSum'] = float(response[symbol]['min_amount'])
					self.rules[pair]['maxSum'] = float(response[symbol]['max_amount'])
					
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
		response = self.__query(method='get',url='https://api.exmo.com/v1.1/order_book/', pair=symbol, limit=depth)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = {}
				data['asks'] = []
				data['bids'] = []
				num_asks = req['depth'] if req['depth'] < len(response[symbol]['ask']) else len(response[symbol]['ask'])
				num_bids = req['depth'] if req['depth'] < len(response[symbol]['bid']) else len(response[symbol]['bid'])
				for i in range(num_asks):
					data['asks'].append([])
					data['asks'][i].append(float(response[symbol]['ask'][i][0]))
					data['asks'][i].append(float(response[symbol]['ask'][i][1]))
				for i in range(num_bids):
					data['bids'].append([])
					data['bids'][i].append(float(response[symbol]['bid'][i][0]))
					data['bids'][i].append(float(response[symbol]['bid'][i][1]))
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
		response = self.__query(method='get',url='https://api.exmo.com/v1.1/ticker')
		if not isinstance(response, dict):
			return False
		if response:
			try:
				return float(response[symbol]['last_trade'])
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
					self.debug_log('code: 230. Get price false')
				return False	
		return False

	# Авторизованные методы
	
	def getBalances(self, all=False):
		# Получение балансов
		correctTime = round((time() - self.deltaTime) * 1000)
		self.signedString = self.__sign(nonce=correctTime)
		response = self.__query(method='post', url='https://api.exmo.com/v1.1/user_info', nonce=correctTime)
		if not isinstance(response, dict):
			return False
		if response:
			data = {}
			try:
				for c in response['balances']:
					if all:
						data[c.lower()] = float(response['balances'][c]) + float(response['reserved'][c])
					else:
						data[c.lower()] = float(response['balances'][c])
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
		correctTime = round((time() - self.deltaTime) * 1000)
		self.signedString = self.__sign(nonce=correctTime, symbol=symbol, limit=10)
		response = self.__query(method='get', url='https://api.exmo.com/v1.1/user_trades', nonce=correctTime, symbol=symbol, limit=10)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				count = len(response[symbol])
				data = []
				for i in range(count):
					data.append({})
					data[i]['pair'] = req['pair']
					data[i]['side'] = response[symbol][i]['type']
					data[i]['qty'] = float(response[symbol][i]['quantity'])
					data[i]['price'] = float(response[symbol][i]['price'])
					data[i]['time'] = float(response[symbol][i]['date']) + self.deltaTime
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
		correctTime = round((time() - self.deltaTime) * 1000)
		self.signedString = self.__sign(nonce=correctTime)
		response = self.__query(method='post', url='https://api.exmo.com/v1.1/user_open_orders', nonce=correctTime)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				count = len(response[symbol])
				data = []
				for i in range(count):
					data.append({})
					data[i]['id'] = response[symbol][i]['order_id']
					data[i]['pair'] = req['pair']
					data[i]['side'] = response[symbol][i]['type'].lower()
					data[i]['qty'] = float(response[symbol][i]['quantity'])
					data[i]['fill'] = 0.0
					data[i]['price'] = float(response[symbol][i]['price'])
					data[i]['time'] = float(response[symbol][i]['created']) + self.deltaTime
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
		correctTime = round((time() - self.deltaTime) * 1000)
		self.signedString = self.__sign(nonce=correctTime, order_id=orderId)
		response = self.__query(method='post', url='https://api.exmo.com/v1.1/order_cancel', order_id=orderId, nonce=correctTime)
		if not isinstance(response, dict):
			return False
		try:
			return True if response['result'] is True else False
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
		correctTime = round((time() - self.deltaTime) * 1000)
		self.signedString = self.__sign(nonce=correctTime, pair=symbol, type=side, quantity=qty, price=price)
		response = self.__query(method='post', url='https://api.exmo.com/v1.1/order_create', pair=symbol, type=side, quantity=qty, price=price, nonce=correctTime)
		if not isinstance(response, dict):
			return False
		try:
			return str(response['order_id']) if response['result'] is True else False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
				self.debug_log('code: 290. Send order false')
			return False

#~ https://exmo.me/en/api
