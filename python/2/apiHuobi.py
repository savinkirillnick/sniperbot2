import requests # Подключаем модуль для работы с HTTP запросами
import json # Подключаем модуль для работы с объектами json
import hmac # Подключаем модуль шифрования HMAC
import hashlib # Подключаем библиотеки шифрования
from time import time, timezone, localtime, strftime # Подключаем модуль работы с временем
import urllib.parse #  Подключение модуля работы с http строкой
from base64 import b64encode # Подключаем кодирование 64


class apiHuobi:
	# Класс для работы с api huobi
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
		self.error = False
		response = self.__query(req_method='get',url='http://api.huobi.pro/v1/common/timestamp')
		serverTime = response['data']
		self.deltaTime = time() - serverTime/1000
		self.account_id = self.__get_account()
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
				if data['status'] == 'error':
					self.debug_log('code ' + data['err-code'] + ': ' + data['err-msg'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False
		if req_method == 'post':
			try:
				response = requests.post(url, params=sorted(req.items()))
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202, url: '+url)
					self.debug_log('code: 202, url: '+url)
				return False
			if response.status_code in [200, 400]:
				data = response.json()
				if data['status'] == 'error':
					self.debug_log('code ' + data['err-code'] + ': ' + data['err-msg'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False
		if req_method == 'send':
			headers = {'Content-type': 'application/json'}
			try:
				data = dict()
				for key in req:
					if key == 'account_id':
						data['account-id'] = req[key]
					else:
						data[key] = req[key]
				response = requests.post(url, data=json.dumps(data), headers=headers)
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 204, url: '+url)
					self.debug_log('code: 204, url: '+url)
				return False
			if response.status_code in [200, 400]:
				data = response.json()
				if data['status'] == 'error':
					self.debug_log('code ' + data['err-code'] + ': ' + data['err-msg'])
					return False
				else:
					return data # Возвращаем JSON объект
			else:
				return False
				
	def __create_url(self, api_method, req_method, **req):
		correctTime = time() + timezone - self.deltaTime
		
		params = dict()
		params['AccessKeyId'] = self.key
		params['SignatureMethod'] = 'HmacSHA256'
		params['SignatureVersion'] = 2
		params['Timestamp'] = strftime('%Y-%m-%dT%H:%M:%S', localtime(correctTime))
		
		if req != {}:
			for key in req:
				params[key] = req[key]
		Signature = self.__sign(api_method, req_method, params)
		return 'https://api.huobi.pro' + api_method + '?'+ urllib.parse.urlencode(sorted(params.items())) + '&Signature=' + Signature
		
	def __sign(self, api_method, req_method, params):	
		# Функция для шифрования подписи
		secret = self.secret.encode()
		data = (req_method + '\napi.huobi.pro\n' + api_method + '\n' + str(urllib.parse.urlencode(sorted(params.items())))).encode()
		hash_data = hmac.new(secret, data, hashlib.sha256).digest()
		encodedBytes = urllib.parse.quote_plus(b64encode(hash_data))
		return encodedBytes
	
	def __get_account(self):
		url = self.__create_url(api_method='/v1/account/accounts', req_method='GET')
		response = self.__query(req_method = 'get', url=url)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				return response['data'][0]['id']
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 205')
					self.debug_log('code: 205')
				return False
		else:
			return False

	def getRules(self):
		# Получение правил биржи, монет и символов
		# pairs - set()
		# coins - set()
		# rules - dict()
		response = self.__query(req_method='get',url='http://api.huobi.pro/v1/common/symbols')
		if not isinstance(response, dict):
			return False
		if response:
			try:
				count = len(response['data'])
				for i in range(count):
					symbol = response['data'][i]
					if symbol['state'] == 'online':
						baseAsset = symbol['base-currency'].lower()
						quoteAsset = symbol['quote-currency'].lower()
						pair = baseAsset + '_' + quoteAsset
						
						self.coins.add(baseAsset)
						self.coins.add(quoteAsset)
						self.pairs.add(pair)
						
						self.rules[pair] = {}
						self.rules[pair]['symbol'] = symbol['symbol']
						self.rules[pair]['minPrice'] = 0
						self.rules[pair]['maxPrice'] = 0
						self.rules[pair]['minQty'] = float(symbol['min-order-amt'])
						self.rules[pair]['maxQty'] = float(symbol['max-order-amt'])
						self.rules[pair]['aroundPrice'] = int((symbol['price-precision']))
						self.rules[pair]['aroundQty'] = int((symbol['amount-precision']))
						self.rules[pair]['minSum'] = float(symbol['min-order-value'])
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
		response = self.__query(req_method='get',url='https://api.huobi.pro/market/trade?symbol='+symbol)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				return response['tick']['data'][0]['price']
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
		depth = req['depth']
		symbol = self.rules[req['pair']]['symbol']
		url = self.__create_url(api_method='/market/depth', req_method='GET', symbol=symbol, type='step0')
		response = self.__query(req_method='get', url=url)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = dict()
				data['asks'] = []
				data['bids'] = []
				num_asks = depth if depth < len(response['tick']['asks']) else len(response['tick']['asks'])
				num_bids = depth if depth < len(response['tick']['bids']) else len(response['tick']['bids'])
				for i in range(num_asks):
					data['asks'].append([])
					data['asks'][i].append(float(response['tick']['asks'][i][0]))
					data['asks'][i].append(float(response['tick']['asks'][i][1]))
				for i in range(num_bids):
					data['bids'].append([])
					data['bids'][i].append(float(response['tick']['bids'][i][0]))
					data['bids'][i].append(float(response['tick']['bids'][i][1]))
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
		url = self.__create_url(api_method='/v1/account/accounts/'+ str(self.account_id) +'/balance', req_method='GET')
		response = self.__query(req_method='get', url=url)
		if not isinstance(response, dict):
			return False
		if response:
			data = {}
			try:
				count = len(response['data']['list'])
				for i in range(count):
					if response['data']['list'][i]['type'] == 'trade':
						data[response['data']['list'][i]['currency'].lower()] = float(response['data']['list'][i]['balance'])
					if all:
						if response['data']['list'][i]['type'] == 'frozen':
							if response['data']['list'][i]['currency'].lower() in data:
								data[response['data']['list'][i]['currency'].lower()] += float(response['data']['list'][i]['balance'])
							else:
								data[response['data']['list'][i]['currency'].lower()] = float(response['data']['list'][i]['balance'])
				return data
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 250')
					self.debug_log('code: 250. Get balances false')
				return False
		else:
			return False

	def getOrders(self, **req):
		# Получение активных ордеров
		# Сначала старые, в конце новые
		symbol = self.rules[req['pair']]['symbol']
		url = self.__create_url(api_method='/v1/order/orders', req_method='GET', symbol=symbol, states='submitted')
		response = self.__query(req_method='get', url=url)
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
					if response['data'][i]['type'][:3] == 'buy':
						data[i]['side'] = 'buy'
					if response['data'][i]['type'][:4] == 'sell':
						data[i]['side'] = 'sell'
					data[i]['qty'] = float(response['data'][i]['amount'])
					data[i]['fill'] = float(response['data'][i]['field-amount'])
					data[i]['price'] = float(response['data'][i]['price'])
					data[i]['time'] = float(response['data'][i]['created-at'])/1000 + self.deltaTime
				return data if count > 0 else False
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 270')
					self.debug_log('code: 270. Get orders false')
				return False
		else:
			return False

	def getTrades(self, **req):
		# Получение истории ордеров
		# Сначала старые, в конце новые
		symbol = self.rules[req['pair']]['symbol']
		
		url = self.__create_url(api_method='/v1/order/matchresults', req_method='GET', symbol=symbol)
		response = self.__query(req_method='get', url=url)

		if not isinstance(response, dict):
			return False
		if response:
			try:
				count = len(response['data'])
				data = []
				for i in range(count):
					if response['data'][i]['type'] != 'submit-cancel':
						data.append({})
						data[i]['pair'] = req['pair']
						if response['data'][i]['type'][:3] == 'buy':
							data[i]['side'] = 'buy'
						if response['data'][i]['type'][:4] == 'sell':
							data[i]['side'] = 'sell'
						data[i]['qty'] = float(response['data'][i]['filled-amount'])
						data[i]['price'] = float(response['data'][i]['price'])
						data[i]['time'] = float(response['data'][i]['created-at'])/1000 + self.deltaTime
				return data if count > 0 else False
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 260')
					self.debug_log('code: 260. Get trades false')
				return False
		else:
			return False

	def cancelOrder(self, **req):
		# Отмена ордера
		# orderId
		orderId = str(req['id'])
		url = self.__create_url(api_method='/v1/order/orders/'+orderId+'/submitcancel', req_method='POST')
		response = self.__query(req_method='post', url=url)
		if not isinstance(response, dict):
			return False
		try:
			return True if response['status'] == 'ok' else False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 280')
				self.debug_log('code: 280. Cancel order false')
			return False

	def sendOrder(self, **req):
		# Отправка ордера
		# orderId
		symbol = self.rules[req['pair']]['symbol']
		side = req['side'].lower()+'-limit'

		aroundPrice = self.rules[req['pair']]['aroundPrice']
		aroundQty = self.rules[req['pair']]['aroundQty']
		formatPrice = '{:.'+str(aroundPrice)+'f}'
		formatQty = '{:.'+str(aroundQty)+'f}'

		amount = str(formatQty.format(req['qty']))
		price = str(formatPrice.format(req['price']))
		
		url = self.__create_url(api_method='/v1/order/orders/place', req_method='POST')
		response = self.__query(req_method='send', url=url, account_id=str(self.account_id), amount=amount, source='api', symbol=symbol, type=side, price=price)
		if not isinstance(response, dict):
			return False
		try:
			return response['data'] if response['data'] is not None else False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
				self.debug_log('code: 290. Send order false')
			return False

#~ https://huobiapi.github.io/docs/spot/v1/en/
