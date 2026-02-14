import requests # Подключаем модуль для работы с HTTP запросами
import hmac # Подключаем модуль шифрования HMAC
import hashlib # Подключаем библиотеки шифрования
from time import time # Подключаем модуль работы с временем
import urllib.parse #  Подключение модуля работы с http строкой
from base64 import b64encode # Подключаем кодирование 64

class apiBithumb:
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
		self.key = ''
		self.secret = ''
		self.coins = set()
		self.pairs = set()
		self.rules = dict()
		self.pair = ''
		self.debug = debug
		self.error = False
		response = self.__query(method='/public/btci')
		serverTime = int(response['data']['date'])
		self.deltaTime = time() - serverTime / 1000

	def debug_log(self, s):
		self.error = s

	def __query(self, method, **req):
		nonce = str(round(1000*(time() - self.deltaTime)))
		url = 'https://api.bithumb.com' + method
		req['endpoint'] = method
		str_data = urllib.parse.urlencode(req)
		data = method + chr(0) + str_data + chr(0) + nonce
		signature = self.__sign(data)
		try:
			response = requests.post(url, data=req, headers={'Api-Key': self.key, 'Api-Sign': signature, 'Api-Nonce': nonce})
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 202, url: '+url)
				self.debug_log('code: 202, url: '+url)
			return False
		if response.status_code in [200, 400]:
			data = response.json()
			if data['status'] != '0000':
				self.debug_log('code ' + data['status'] + ': ' + data['message'])
				return False
			else:
				return data # Возвращаем JSON объект
		else:
			return False

	def __sign(self, data):
		# Функция для шифрования подписи
		secret = self.secret.encode()
		data = data.encode()
		return b64encode(hmac.new(secret, data, hashlib.sha512).hexdigest().encode()).decode()

	def getRules(self):
		# Получение правил биржи, монет и символов
		# pairs - set()
		# coins - set()
		# rules - dict()
		pairs = ['zrx_krw', 'amo_krw', 'apix_krw', 'arpa_krw', 'ae_krw', 'aion_krw', 'ankr_krw', 'rep_krw', 'aoa_krw', 'basic_krw', 'bhp_krw', 'bsv_krw', 'boa_krw', 'bat_krw', 'bznt_krw', 'btt_krw', 'btc_krw', 'bch_krw', 'bcd_krw', 'btg_krw', 'con_krw', 'ada_krw', 'link_krw', 'chr_krw', 'cos_krw', 'ctxs_krw', 'cosm_krw', 'lba_krw', 'mco_krw', 'cro_krw', 'dad_krw', 'dvp_krw', 'dash_krw', 'dac_krw', 'el_krw', 'eos_krw', 'em_krw', 'enj_krw', 'eth_krw', 'etc_krw', 'fzz_krw', 'fab_krw', 'fleta_krw', 'fnb_krw', 'fct_krw', 'fx_krw', 'gxc_krw', 'gnt_krw', 'hyc_krw', 'hdac_krw', 'icx_krw', 'iost_krw', 'ipx_krw', 'ins_krw', 'itc_krw', 'knc_krw', 'luna_krw', 'lamb_krw', 'ltc_krw', 'loom_krw', 'lrc_krw', 'mxc_krw', 'meta_krw', 'mtl_krw', 'mix_krw', 'xmr_krw', 'mbl_krw', 'xem_krw', 'egg_krw', 'omg_krw', 'rnt_krw', 'orbs_krw', 'ogo_krw', 'pivx_krw', 'plx_krw', 'powr_krw', 'pcm_krw', 'xpr_krw', 'npxs_krw', 'qbz_krw', 'qtum_krw', 'qkc_krw', 'xrp_krw', 'soc_krw', 'snt_krw', 'steem_krw', 'xml_krw', 'strat_krw', 'sxp_krw', 'trx_krw', 'tmtg_krw', 'theta_krw', 'true_krw', 'trv_krw', 'valor_krw', 'vet_krw', 'xvg_krw', 'waxp_krw', 'wom_krw', 'wpx_krw', 'wtc_krw', 'waves_krw', 'wicc_krw', 'wet_krw', 'zec_krw', 'zil_krw', 'elf_krw', 'vsys_krw', 'xsr_krw' ]
		try:
			for pair in pairs:
				value = pair.split('_')
				baseAsset = value[0]
				quoteAsset = value[1]
				
				self.coins.add(baseAsset)
				self.coins.add(quoteAsset)
				
				self.rules[pair] = {}
				self.rules[pair]['symbol'] = pair.upper()
				self.rules[pair]['minPrice'] = 0
				self.rules[pair]['maxPrice'] = 0
				self.rules[pair]['minQty'] = 0
				self.rules[pair]['maxQty'] = 0
				self.rules[pair]['aroundPrice'] = 0
				self.rules[pair]['aroundQty'] = 0
				self.rules[pair]['minSum'] = 0
				self.rules[pair]['maxSum'] = 0
			self.coins = list(self.coins)
			self.coins.sort()
			self.pairs = pairs
			self.pairs.sort()
			return self.rules
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 210')
				self.debug_log('code: 210. Get rules false')
			return False
	
	def getCoins(self):
		return self.coins
	
	def getPairs(self):
		return self.pairs
	
	def __upd(self, **req):
		pair = req['pair']
		self.rules[pair] = {}
		
		if req['ask'] < 1:
			aroundPrice = 4
			aroundQty = -1
			minQty = 10
		elif req['ask'] >= 1 and req['ask'] < 10:
			aroundPrice = 3
			aroundQty = -1
			minQty = 10
		elif req['ask'] >= 10 and req['ask'] < 100:
			aroundPrice = 2
			aroundQty = -1
			minQty = 10
		elif req['ask'] >= 100 and req['ask'] < 1000:
			aroundPrice = 1
			aroundQty = 0
			minQty = 1
		elif req['ask'] >= 1000 and req['ask'] < 5000:
			aroundPrice = 0
			aroundQty = 1
			minQty = 0.1
		elif req['ask'] >= 5000 and req['ask'] < 10000:
			aroundPrice = -1
			aroundQty = 1
			minQty = 0.1
		elif req['ask'] >= 10000 and req['ask'] < 50000:
			aroundPrice = -1
			aroundQty = 2
			minQty = 0.01
		elif req['ask'] >= 50000 and req['ask'] < 100000:
			aroundPrice = -2
			aroundQty = 2
			minQty = 0.01
		elif req['ask'] >= 100000 and req['ask'] < 500000:
			aroundPrice = -2
			aroundQty = 3
			minQty = 0.001
		elif req['ask'] >= 500000 and req['ask'] < 1000000:
			aroundPrice = -3
			aroundQty = 3
			minQty = 0.001
		else:
			aroundPrice = -3
			aroundQty = 4
			minQty = 0.0001
		
		self.rules[pair]['symbol'] = pair.upper()
		self.rules[pair]['minPrice'] = req['bid'] * 0.1
		self.rules[pair]['maxPrice'] = req['ask'] * 2
		self.rules[pair]['minQty'] = minQty
		self.rules[pair]['maxQty'] = 0
		self.rules[pair]['aroundPrice'] = aroundPrice
		self.rules[pair]['aroundQty'] = aroundQty
		self.rules[pair]['minSum'] = 0
		self.rules[pair]['maxSum'] = 5000000000
	
	def getDepth(self, **req):
		# Получение стакана
		# Сначала спредовые
		# depth = dict()
		symbol = req['pair'].upper()
		response = self.__query(method='/public/orderbook/'+symbol)
		self.pair = req['pair']
		if not isinstance(response, dict):
			return False
		if response:
			try:
				if response['status'] == '0000':
					data = {}
					data['asks'] = []
					data['bids'] = []
					num_asks = req['depth'] if req['depth'] < len(response['data']['asks']) else len(response['data']['asks'])
					num_bids = req['depth'] if req['depth'] < len(response['data']['bids']) else len(response['data']['bids'])
					for i in range(num_asks):
						data['asks'].append([])
						data['asks'][i].append(float(response['data']['asks'][i]['price']))
						data['asks'][i].append(float(response['data']['asks'][i]['quantity']))
					for i in range(num_bids):
						data['bids'].append([])
						data['bids'][i].append(float(response['data']['bids'][i]['price']))
						data['bids'][i].append(float(response['data']['bids'][i]['quantity']))
					self.__upd(pair=req['pair'], ask=data['asks'][0][0], bid=data['bids'][0][0])
					return data
				else:
					return False
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 220')
					self.debug_log('code: 220. Get depth false')
				return False
		else:
			return False
	
	def getPrice(self, **req):
		# Получение последней цены
		symbol = req['pair'].upper()
		response = self.__query(method='/public/ticker/'+symbol)
		if not isinstance(response, dict):
			return False
		if response:
			try:
				if response['status'] == '0000':
					return float(response['data']['closing_price'])
				else:
					return False
			except:
				if self.debug:
					#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 230')
					self.debug_log('code: 230. Get price false')
				return False	
		return False

	# Авторизованные методы
	
	def getBalances(self, all=False):
		# Получение балансов
		value = self.pair.split('_')
		response = self.__query(method='/info/balance', currency=value[0].upper())
		
		if not isinstance(response, dict):
			return False
		if response:
			try:
				data = {}
				if response['status'] == '0000':
					if all:
						base_asset = value[0]
						quote_asset = value[1]
						base_avail = 'total_'+base_asset
						quote_avail = 'total_'+quote_asset
						data[base_asset] = float(response['data'][base_avail])
						data[quote_asset] = float(response['data'][quote_avail])
					else:
						base_asset = value[0]
						quote_asset = value[1]
						base_avail = 'available_'+base_asset
						quote_avail = 'available_'+quote_asset
						data[base_asset] = float(response['data'][base_avail])
						data[quote_asset] = float(response['data'][quote_avail])
					return data
				else:
					return False
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
		value = req['pair'].split('_')
		response = self.__query(method='/info/orders', order_currency=value[0].upper(), payment_currency=value[1].upper())
		if not isinstance(response, dict):
			return False
		if response:
			try:
				if response['status'] == '0000':
					data = []
					j = 0
					count = len(response['data'])
					for i in range(count):
						if float(response['data'][i]['units_remaining']) == 0:
							data.append({})
							data[j]['pair'] = req['pair']
							if response['data'][i]['type'] == 'bid':
								data[j]['side'] = 'buy'
							elif response['data'][i]['type'] == 'ask':
								data[j]['side'] = 'sell'
							data[j]['qty'] = float(response['data'][i]['units'])
							data[j]['price'] = float(response['data'][i]['price'])
							data[j]['time'] = float(response['data'][i]['order_date'])/1000000 + self.deltaTime
							j += 1
					return data if j > 0 else False
				else:
					return False
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
		value = req['pair'].split('_')
		response = self.__query(method='/info/orders', order_currency=value[0].upper(), payment_currency=value[1].upper())
		if not isinstance(response, dict):
			return False
		if response:
			try:
				if response['status'] == '0000':
					data = []
					j = 0
					count = len(response['data'])
					for i in range(count):
						if float(response['data'][i]['units_remaining'].replace(',','')) != 0:
							data.append({})
							data[j]['id'] = response['data'][i]['order_id']
							data[j]['pair'] = req['pair']
							if response['data'][i]['type'] == 'bid':
								data[j]['side'] = 'buy'
							elif response['data'][i]['type'] == 'ask':
								data[j]['side'] = 'sell'
							data[j]['qty'] = float(response['data'][i]['units'].replace(',',''))
							data[j]['fill'] = float(response['data'][i]['units'].replace(',','')) - float(response['data'][i]['units_remaining'].replace(',',''))
							data[j]['price'] = float(response['data'][i]['price'].replace(',',''))
							data[j]['time'] = float(response['data'][i]['order_date'])/1000000 + self.deltaTime 
							j += 1
					return data if j > 0 else False
				else:
					return False
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
		value = req['pair'].split('_')

		orderId = req['id']
		response_b = self.__query(method='/trade/cancel', order_id=orderId, order_currency=value[0].upper(), payment_currency=value[1].upper(), type='bid')
		response_s = self.__query(method='/trade/cancel', order_id=orderId, order_currency=value[0].upper(), payment_currency=value[1].upper(), type='ask')

		try:
			if response_b['status'] == '0000' or response_s['status'] == '0000':
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
		value = self.rules[req['pair']]['symbol'].split('_')
		if req['side'].lower() == 'buy':
			side = 'bid'
		elif req['side'].lower() == 'sell':
			side = 'ask'
		else:
			return False
		units = req['qty']
		price = req['price']
		response = self.__query(method='/trade/place', order_currency=value[0], payment_currency=value[1], type=side, units=units, price=price)
		if not isinstance(response, dict):
			return False
		try:
			return response['order_id'] if response['status'] == '0000' else False
		except:
			if self.debug:
				#~ print(time.strftime('%m/%d %H:%M ', time.localtime()) + 'code: 290')
				self.debug_log('code: 290. Send order false')
			return False
		
#~ https://apidocs.bithumb.com/

