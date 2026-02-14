import requests # Подключаем модуль для работы с HTTP запросами
import json # Подключаем модуль для работы с объектами json
import math # Подключаем модуль для математических операций
import hmac # Подключаем модуль шифрования HMAC
import hashlib # Подключаем библиотеки шифрования
from time import time # Подключаем модуль работы с временем
import urllib.parse #  Подключение модуля работы с http строкой

class apiBtcalpha():
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
	deltaTime = 0.0
	# В секундах
	key = ''
	secret = ''
	coins = set()
	pairs = set()
	rules = dict()
	
	debug = False
	error = False
	
	orders = dict()
	
	def __init__(self, key, secret, debug=False):
		self.key = key
		self.secret = secret
		response = self.__query(method='get',url='https://btc-alpha.com/api/v1/exchanges/', headers=False, limit=1)
		serverTime = response[0]['timestamp']
		self.deltaTime = time.time() - serverTime
		self.debug = debug
	
	def debug_log(self, s):
		self.error = s
	
	def __query(self, method, url, headers, **req):
		# Функция отправки запроса (вспомогательная функция)
		if method == 'get':
			try:
				if headers == False:
					response = requests.get(url, params=sorted(req.items()))
				else:
					response = requests.get(url, params=sorted(req.items()), headers=headers)
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + )
					self.debug_log('code: 201, url: '+url)
				return False
			if response.status_code == 200 or response.status_code == 400:
				return response.json() # Возвращаем JSON объект
			else:
				return False
		if method == 'post':
			try:
				response = requests.post(url, data=sorted(req.items()), headers=headers)
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202, url: '+url)
					self.debug_log('code: 202, url: '+url)
				return False
			if response.status_code == 200 or response.status_code == 201 or response.status_code == 400:
				return response.json() # Возвращаем JSON объект
			else:
				return False

	def __sign(self, **req):
		# Функция для шифрования подписи
		#~ path = urllib.parse.urlencode(sorted(req.items()))
		
		params = urllib.parse.urlencode(sorted(req.items(), key=lambda val: val[0]))
		
		if len(params) > 0:
			msg = self.key + params
		else:
			msg = self.key
		sign = hmac.new(self.secret.encode(), msg.encode(), digestmod='sha256').hexdigest()

		return {
			#~ 'Accept': 'application/json',
			#~ 'Content-Type': 'application/x-www-form-urlencoded',
			'X-KEY': self.key,
			'X-SIGN': sign,
			'X-NONCE': str(int(time.time() * 1000)),
		}

	def getRules(self):
		# Получение правил биржи, монет и символов
		# pairs - set()
		# coins - set()
		# rules - dict()
		response = self.__query(method='get',url='https://btc-alpha.com/api/v1/pairs/', headers=False)
		if type(response) != type(list()):
			return False
		if response != False:

			try:
				for i in range(len(response)):

					baseAsset = response[i]['currency1'].lower()
					quoteAsset = response[i]['currency2'].lower()
					pair = baseAsset + '_' + quoteAsset
					
					self.coins.add(baseAsset)
					self.coins.add(quoteAsset)
					self.pairs.add(pair)
					
					self.rules[pair] = {}
					self.rules[pair]['symbol'] = response[i]['name']
					self.rules[pair]['minPrice'] = 0
					self.rules[pair]['maxPrice'] = 0
					self.rules[pair]['minQty'] = response[i]['minimum_order_size']
					self.rules[pair]['maxQty'] = response[i]['maximum_order_size']
					self.rules[pair]['aroundPrice'] = response[i]['price_precision']
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
					self.debug_log('code: 210')
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
		response = self.__query(method='get',url='https://btc-alpha.com/api/v1/orderbook/'+symbol+'/', headers=False, limit_asks=req['depth'], limit_bids=req['depth'], group=1)
		if type(response) != type(dict()):
			return False
		if response != False:
			try:
				data = {}
				data['asks'] = []
				data['bids'] = []
				num_asks = req['depth'] if req['depth'] < len(response['sell']) else len(response['sell'])
				num_bids = req['depth'] if req['depth'] < len(response['buy']) else len(response['buy'])
				for i in range(num_asks):
					data['asks'].append([])
					data['asks'][i].append(float(response['sell'][i]['price']))
					data['asks'][i].append(float(response['sell'][i]['amount']))
				for i in range(num_bids):
					data['bids'].append([])
					data['bids'][i].append(float(response['buy'][i]['price']))
					data['bids'][i].append(float(response['buy'][i]['amount']))
				return data
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 220')
					self.debug_log('code: 220')
				return False
		else:
			return False
	
	def getPrice(self, **req):
		# Получение последней цены
		symbol = self.rules[req['pair']]['symbol']
		response = self.__query(method='get',url='https://btc-alpha.com/api/v1/exchanges/', headers=False, pair=symbol, limit=1)
		if type(response) != type(list()):
			return False
		if response != False:
			try:
				return response[0]['price']
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
					self.debug_log('code: 230')
				return False	
		return False

	# Авторизованные методы
	
	def getBalances(self):
		# Получение балансов
		headers=self.__sign()
		response = self.__query(method='get', url='https://btc-alpha.com/api/v1/wallets/', headers=headers)
		if type(response) != type(list()):
			return False
		if response != False:
			data = {}
			try:
				for coin in self.coins:
					data[coin] = 0
				count = len(response)
				for i in range(count):
					data[response[i]['currency'].lower()] = float(response[i]['balance'])
				return data
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 250')
					self.debug_log('code: 250')
				return False
		else:
			return False
		
	def getTrades(self, **req):
		# Получение истории ордеров
		# Сначала старые, в конце новые
		symbol = self.rules[req['pair']]['symbol']
		headers = self.__sign()
		response = self.__query(method='get', url='https://btc-alpha.com/api/v1/orders/own/', headers=headers, pair=symbol)
		if type(response) != type(list()):
			return False
		if response != False:
			try:
				count = len(response)
				data = []
				j = 0
				for i in range(count):
					if response[count-1-i]['status'] == 2 or response[count-1-i]['status'] == 3:
						if float(response[count-1-i]['amount']) != 0.0:
							data.append({})
							data[j]['pair'] = req['pair']
							data[j]['side'] = response[count-1-i]['type']
							data[j]['qty'] = float(response[count-1-i]['amount'])
							data[j]['price'] = float(response[count-1-i]['price'])
							orderId = str(response[count-1-i]['id'])
							if orderId in self.orders:
								data[j]['time'] = orders[orderId]
							else:
								data[j]['time'] = 0.0
							j += 1
				return data if j > 0 else False
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 260')
					self.debug_log('code: 260')
				return False
				
		else:
			return False
		return False
		
	def getOrders(self, **req):
		# Получение активных ордеров
		# Сначала старые, в конце новые
		symbol = self.rules[req['pair']]['symbol']
		headers = self.__sign()
		response = self.__query(method='get', url='https://btc-alpha.com/api/v1/orders/own/', headers=headers, pair=symbol, status=1)
		if type(response) != type(list()):
			return False
		if response != False:
			try:
				count = len(response)
				data = []
				for i in range(count):
					data.append({})
					orderId = str(response[count-1-i]['id'])
					data[i]['id'] = orderId
					data[i]['pair'] = req['pair']
					data[i]['side'] = response[count-1-i]['type']
					data[i]['qty'] = float(response[count-1-i]['amount'])
					data[i]['fill'] = 0.0
					data[i]['price'] = float(response[count-1-i]['price'])
					if orderId in self.orders:
						data[i]['time'] = self.orders[orderId]
					else:
						data[i]['time'] = 0.0
				return data if count > 0 else False
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 270')
					self.debug_log('code: 270')
				return False
		else:
			return False
		return False
		
	def cancelOrder(self, **req):
		# Отмена ордера
		# orderId
		
		headers = self.__sign(order=int(req['id']))
		response = self.__query(method='post', url='https://btc-alpha.com/api/v1/order-cancel/', headers=headers, order=int(req['id']))
		if type(response) != type(dict()):
			return False
		try:
			if response['order'] == int(req['id']):
				if response['order'] in self.orders:
					del self.orders[response['order']]
				return True
			else:
				return False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 280')
				self.debug_log('code: 280')
			return False
		return False

	def sendOrder(self, **req):
		# Отправка ордера
		# orderId
		headers = self.__sign(pair=self.rules[req['pair']]['symbol'], type=req['side'], amount=req['qty'], price=req['price'])
		response = self.__query(method='post', url='https://btc-alpha.com/api/v1/order/', headers=headers, pair=self.rules[req['pair']]['symbol'], type=req['side'], amount=req['qty'], price=req['price'])

		if type(response) != type(dict()):
			return False
		try:
			orderId = str(response['oid'])
			orders[orderId] = time.time()
			return orderId
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
				self.debug_log('code: 290')
			return False
		return False

#~ https://btc-alpha.github.io/api-docs/

api = apiBtcalpha(key='CWszaxqBuKe5RDo4ARuEctTQLU7DWKc3WF6PXwxRnTgAyQDGuXeAV4Ebs96kdsywDc9JgamqX', secret='4QMFAz9SHfwzPDAQaYvxBBggpABQVZd32LaFfYVU2ozSux2CwzDbSsmskHGp4Z6HGusgqZBMgZnrwexBsMwzHY3S')

req = api.getRules()
#~ req = api.getPairs()
#~ req = api.getDepth(pair='xrp_usd', depth=5)
#~ req = api.getPrice(pair='btc_usd')
#~ req = api.getBalances()
print('---------------------')
#~ req = api.getOrders(pair='doge_usdt')
req = api.getTrades(pair='doge_usdt')
#~ req = api.cancelOrder(pair='doge_usdt', id='247603520')
#~ req = api.sendOrder(pair='btc_usdt', side='sell', qty=1379.0, price=0.00362582)
#~ 
print('---------------------')
print(req)
#~ print(api.deltaTime)
#~ print(time.time())
