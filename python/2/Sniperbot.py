from apiBinance import *
from apiBithumb import *
from apiDovewallet import *
from apiCex import *
from apiHuobi import *
from apiKucoin import *
from apiLivecoin import *
from apiExmo import *
from apiOkex import *
from apiTidex import *
from apiYobit import *

import sys
import requests
import time
import sqlite3
import random
import os

import tkinter as tk
from tkinter import ttk
import json

from classDB import *
from classPosition import *

#~ 1.2.1
#~ Исправлены мелкие ошибки скриптов работы с API Bithumb, Dovewallet, Okex

#~ 1.2
#~ Обновление кода
#~ Добавлена возможность смены стратегии из вне
#~ Переделаны функции хранения и вывода логов
#~ Исправлен параметр паузы покупки после продажи

#~ 1.1 build 4
#~ Исправлен метод округления цен биржи Tidex
#~ Подключена биржа Kucoin
#~ Исправлена функции расчета цен продаж

#~ 1.1 build 3
#~ Испавлено построение времени ожидания отправки ордера

#~ 1.1 build 2
#~ Переписана функция основного цикла
#~ Исправлены тайминги для бирж
#~ Добавлены биржи Yobit, Livecoin

#~ 1.1 build 1
#~ Мелкие исправления работы с биржевыми API

#~ 1.1
#~ Введена система кодов ошибок
#~ Добавлен модуль подсчета позиции
#~ Добавлена биржа Cex
#~ Мелкие изменения по работе с биржами Binance, Bithumb, Okex, Dovewallet

#~ 1.0 build 5
#~ Добавлен режим выявления ошибок. Вызывается флагами -d или --debug
#~ Изменена работа таймингов при отмене ордера
#~ Добавлена биржа Bithumb

#~ 1.0 build 4
#~ Добавлено отображение времени в логах
#~ Исправлен метод отмены ордеров для Binance
#~ Небольшая оптимизация кода
#~ Добавлены биржи Tidex, Dovewallet

#~ 1.0 build 3
#~ Добавлена биржа Okex
#~ Переписан скрипт отображения истории ордеров Huobi
#~ 
#~ 1.0 build 2
#~ Добавлена биржа Exmo
#~ Переписан скрипт отмены ордеров
#~ 
#~ 1.0 build 1
#~ Рабочая версия программы Sniperbot

class Bot():

	error = ''
	access_time = 0.0
	
	api_key = ''
	api_secret = ''
	exchange = ''
	pair = ''
	order_life = 0.0
	pause = 0.0
	upd_time = 0.0

	max_buy = 0.0
	min_sell = 0.0
	step_size = 0.0
	lot_size = 0.0
	fee = 0.0
	
	db = None
	
	def __init__(self, db):
		
		self.db = db
	
	def access(self, access_time):
		self.access_time = access_time
	
	def load(self, set_num):
		if time.time() < self.access_time:
			try:
				self.db.c.execute('SELECT * FROM bot_settings WHERE set_num=?', (set_num,))
				row = self.db.c.fetchall()
				self.db.conn.commit()
				if row != []:
					data = json.loads(row[0][2])
					self.api_key = data['api_key'] if 'api_key' in data else ''
					self.api_secret = data['api_secret'] if 'api_secret' in data else ''
					self.exchange = data['exchange'] if 'exchange' in data else ''
					self.pair = data['pair'] if 'pair' in data else ''
					self.order_life = data['order_life'] if 'order_life' in data else 0.0
					self.pause = data['pause'] if 'pause' in data else 0.0
					self.upd_time = data['upd_time'] if 'upd_time' in data else 0.0
					
					self.max_buy = data['max_buy'] if 'max_buy' in data else 0.0
					self.min_sell = data['min_sell'] if 'min_sell' in data else 0.0
					self.step_size = data['step_size'] if 'step_size' in data else 0.0
					self.lot_size = data['lot_size'] if 'lot_size' in data else 0.0
					self.fee = data['fee'] if 'fee' in data else 0.0
					
			except:
				self.error = 'code: 106. Bot settings not loaded'
	
	def save(self, set_num):
		if time.time() < self.access_time:
			try:
				data = dict()
				data['api_key'] = self.api_key
				data['api_secret'] = self.api_secret
				data['exchange'] = self.exchange
				data['pair'] = self.pair
				data['order_life'] = self.order_life
				data['pause'] = self.pause
				data['upd_time'] = self.upd_time
				
				data['max_buy'] = self.max_buy
				data['min_sell'] = self.min_sell
				data['step_size'] = self.step_size
				data['lot_size'] = self.lot_size
				data['fee'] = self.fee
				
				data_json = json.dumps(data)
				
				self.db.c.execute('SELECT * FROM bot_settings WHERE set_num=?', (set_num,))
				row = self.db.c.fetchall()
				self.db.conn.commit()
				if row != []:
					self.db.c.execute('UPDATE bot_settings SET set_desc=? WHERE set_num=?', (data_json, set_num))
				else:
					self.db.c.execute('INSERT INTO bot_settings (id, set_num, set_desc) VALUES (null, ?, ?)', (set_num, data_json))
				self.db.conn.commit()
				
			except:
				self.error = 'code: 105. Bot settings not saved'

	def upd(self, data):
		self.api_key = data['api_key'] if 'api_key' in data else self.api_key 
		self.api_secret = data['api_secret'] if 'api_secret' in data else self.api_secret
		self.exchange = data['exchange'] if 'exchange' in data else self.exchange
		self.pair = data['pair'] if 'pair' in data else self.pair
		self.order_life = data['order_life'] if 'order_life' in data else self.order_life
		self.pause = data['pause'] if 'pause' in data else self.pause
		self.upd_time = data['upd_time'] if 'upd_time' in data else self.upd_time
		
		self.max_buy = data['max_buy'] if 'max_buy' in data else self.max_buy
		self.min_sell = data['min_sell'] if 'min_sell' in data else self.min_sell
		self.step_size = data['step_size'] if 'step_size' in data else self.step_size
		self.lot_size = data['lot_size'] if 'lot_size' in data else self.lot_size
		self.fee = data['fee'] if 'fee' in data else self.fee

class ChildDebugWindow(tk.Toplevel):
	
	def __init__(self, **req):
		super().__init__(root)
		self.init_window(req)
	
	def init_window(self, req):
		self.title('Debug window')
		self.geometry("260x400+400+300")
		self.resizable(False, False)
		
		label_params = tk.Label(self, text='PARAMS:', font='Arial 10 bold')
		label_params.place(x=10, y=10)
		
		self.params_box = tk.Text(self, font='Arial 10', wrap=tk.WORD)
		params_scrollbar = tk.Scrollbar(self.params_box)
		
		params_scrollbar['command'] = self.params_box.yview
		self.params_box['yscrollcommand'] = params_scrollbar.set
		
		self.params_box.place(x=10, y=35, width=240, height=360)
		params_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		list_keys = list(req.keys())
		list_keys.sort()
		
		param_string = ''
		for item in list_keys:
			param_string += item + ': ' + str(req[item]) + '\n'
		
		self.params_box.insert(tk.END, param_string)
		self.params_box.configure(state='disable')
		self.params_box.yview_moveto(1)

class ChildPositionWindow(tk.Toplevel):
	
	def __init__(self, price, qty, buy_num_step, sell_num_step, start_price):
		super().__init__(root)
		self.init_window(price, qty, buy_num_step, sell_num_step, start_price)
		self.view = app
	
	def init_window(self, price, qty):
		self.title('Edit position')
		self.geometry("280x200+320+240")
		root.resizable(False, False)

		label_desc = tk.Label(self, text='EDIT POSITION', font='Arial 10 bold')
		label_desc.place(x=10, y=10)
		
		label_price = tk.Label(self, text='Average price')
		label_price.place(x=10, y=35)
		self.entry_price = ttk.Entry(self)
		self.entry_price.place(x=150, y=35, width = 120)
		self.entry_price.delete(0, tk.END)
		self.entry_price.insert(0, price)
		
		label_qty = tk.Label(self, text='Position amount')
		label_qty.place(x=10, y=60)
		self.entry_qty = ttk.Entry(self)
		self.entry_qty.place(x=150, y=60, width = 120)
		self.entry_qty.delete(0, tk.END)
		self.entry_qty.insert(0, qty)

		btn_apply = ttk.Button(self, text='Apply', command=self.edit_position)
		btn_apply.place(x=10, y=170, width=120, height=20)
		
		btn_cancel = ttk.Button(self, text='Cancel', command=self.destroy)
		btn_cancel.place(x=150, y=170, width=120, height=20)
		
		self.grab_set()
		self.focus_set()
		
	def edit_position(self):
		self.view.edit_position(price=float(self.entry_price.get()), qty=float(self.entry_qty.get()))
		self.destroy()

class Main(tk.Frame):
	
	ver = '1.2'
	
	debug = False
	test = True
	#~ test = False

	error = ''
	error_time = 0.0
	
	api_is_init = False
	bot_access = False
	bot_is_init = False
	bot_is_run = False
	pos_is_init = False
	
	db = None
	api = None
	rules = None
	bot = None
	pos = None
	
	shared_key = ''
	access_time = 0.0
	set_num = ''
	
	queue_id = ''
	
	pos_time = 0.0
	last_price = 0.0
	
	start_buy_trading = time.time()
	start_sell_trading = time.time()
	
	next_time_depth = 0.0
	next_time_price = 0.0
	next_time_balance = 0.0
	next_time_orders = 0.0
	next_time_trades = 0.0
	next_time_settings = 0.0
	
	last_time = 0.0
	last_side = ''
	last_id = ''
	
	buy_access = False
	sell_access = False
	
	logs_system = ''
	logs_trade = ''
	
	logs_time = 0.0
	
	balances = dict()
	trades = list()
	orders = list()
	depth = dict()
	
	def __init__(self, root):
		super().__init__(root)
		for param in sys.argv:
			if param == '--debug' or param == '-d':
				print('Debug mode is ON')
				self.debug = True

		if self.test:
			self.debug = True

		self.db = DB()
		self.bot = Bot(db=self.db)
		self.pos = Position(db=self.db)

		self.depth = {'bids':[[0.0,0.0],],'asks':[[0.0,0.0],]}
		
		self.init_window()

		self.db.c.execute('SELECT * FROM init_settings')
		row = self.db.c.fetchall()
		if row != []:
			self.entry_share.insert(0, row[0][1])
		else:
			self.entry_share.insert(0, 'demo')
		self.db.conn.commit()
		self.log('Welcome to Sniper Bot')
		self.update_main()

	def init_window(self):
		
		#menu
		toolbar = tk.Frame(bg='#ffffff', bd=0, width=800, height=470)
		toolbar.pack(side=tk.TOP, fill=tk.BOTH)

		label_share = tk.Label(toolbar, bg='#ffffff', text='Share')
		label_share.place(x=10, y=10)
		self.entry_share = ttk.Entry(toolbar)
		self.entry_share.place(x=80, y=10, width = 120)
		btn_init = ttk.Button(toolbar, text='Init', command=self.get_access)
		btn_init.place(x=275, y=10, width=120, height=20)
		self.btn_save = ttk.Button(toolbar, text='Save', command=self.save_settings, state='disabled')
		self.btn_save.place(x=470, y=10, width=120, height=20)
		self.btn_load = ttk.Button(toolbar, text='Load', command=self.load_settings, state='disabled')
		self.btn_load.place(x=665, y=10, width=120, height=20)

		label_key = tk.Label(toolbar, bg='#ffffff', text='Key')
		label_key.place(x=10, y=35)
		label_secret = tk.Label(toolbar, bg='#ffffff', text='Secret')
		label_secret.place(x=205, y=35)
		label_exchange = tk.Label(toolbar, bg='#ffffff', text='Exchange')
		label_exchange.place(x=400, y=35)
		label_set = tk.Label(toolbar, bg='#ffffff', text='Set')
		label_set.place(x=595, y=35)
		self.entry_key = ttk.Entry(toolbar, state='disabled')
		self.entry_key.place(x=80, y=35, width = 120)
		self.entry_secret = ttk.Entry(toolbar, state='disabled')
		self.entry_secret.place(x=275, y=35, width = 120)
		self.entry_exchange = ttk.Combobox(toolbar, values=[u'Binance', u'Bithumb', u'Cex', u'Dovewallet', u'Exmo', u'Huobi', u'Kucoin', u'Livecoin', u'Okex', u'Tidex', u'Yobit'], state='disabled')
		self.entry_exchange.current(0)
		self.entry_exchange.place(x=470, y=35, width = 120)
		self.entry_set = ttk.Combobox(toolbar, values=[u'',], state='disabled')
		self.entry_set.place(x=665, y=35, width = 120)

		label_max_buy = tk.Label(toolbar, bg='#ffffff', text='Max Buy')
		label_max_buy.place(x=10, y=60)
		label_min_sell = tk.Label(toolbar, bg='#ffffff', text='Min Sell')
		label_min_sell.place(x=205, y=60)
		label_step_size = tk.Label(toolbar, bg='#ffffff', text='Step Size')
		label_step_size.place(x=400, y=60)
		label_lot_size = tk.Label(toolbar, bg='#ffffff', text='Lot Size')
		label_lot_size.place(x=595, y=60)
		self.entry_max_buy = ttk.Entry(toolbar, state='disabled')
		self.entry_max_buy.place(x=80, y=60, width = 120)
		self.entry_min_sell = ttk.Entry(toolbar, state='disabled')
		self.entry_min_sell.place(x=275, y=60, width = 120)
		self.entry_step_size = ttk.Entry(toolbar, state='disabled')
		self.entry_step_size.place(x=470, y=60, width = 120)
		self.entry_lot_size = ttk.Entry(toolbar, state='disabled')
		self.entry_lot_size.place(x=665, y=60, width = 120)

		label_pair = tk.Label(toolbar, bg='#ffffff', text='Pair')
		label_pair.place(x=10, y=85)
		label_order_life = tk.Label(toolbar, bg='#ffffff', text='Order Life')
		label_order_life.place(x=205, y=85)
		label_pause = tk.Label(toolbar, bg='#ffffff', text='Pause')
		label_pause.place(x=400, y=85)
		label_upd_time = tk.Label(toolbar, bg='#ffffff', text='Upd Time')
		label_upd_time.place(x=595, y=85)
		self.entry_pair = ttk.Entry(toolbar, state='disabled')
		self.entry_pair.place(x=80, y=85, width = 120)
		self.entry_order_life = ttk.Entry(toolbar, state='disabled')
		self.entry_order_life.place(x=275, y=85, width = 120)
		self.entry_pause = ttk.Entry(toolbar, state='disabled')
		self.entry_pause.place(x=470, y=85, width = 120)
		self.entry_update_time = ttk.Entry(toolbar, state='disabled')
		self.entry_update_time.place(x=665, y=85, width = 120)

		label_fee = tk.Label(toolbar, bg='#ffffff', text='Fee')
		label_fee.place(x=10, y=110)
		self.entry_fee = ttk.Entry(toolbar, state='disabled')
		self.entry_fee.place(x=80, y=110, width = 120)

		self.btn_use = ttk.Button(toolbar, text='Apply', command=self.use_settings, state='disabled')
		self.btn_use.place(x=275, y=110, width=120, height=20)
		self.btn_start = ttk.Button(toolbar, text='Start', command=self.start_bot, state='disabled')
		self.btn_start.place(x=470, y=110, width=120, height=20)
		self.btn_stop = ttk.Button(toolbar, text='Stop', command=self.stop_bot, state='disabled')
		self.btn_stop.place(x=665, y=110, width=120, height=20)
		
		self.label_error = tk.Label(toolbar, bg='#ffffff', text='Errors log')
		self.label_error.place(x=10, y=135)
		
		if self.debug == True:
			self.btn_params = ttk.Button(toolbar, text='View Params', command=self.open_debug_dialog)
			self.btn_params.place(x=665, y=135, width=120, height=20)
		
		label_ask_title = tk.Label(toolbar, bg='#ffffff', text='ASK:', font='Arial 10 bold')
		label_ask_title.place(x=10, y=160)
		label_bid_title = tk.Label(toolbar, bg='#ffffff', text='BID:', font='Arial 10 bold')
		label_bid_title.place(x=205, y=160)

		label_ask_price_title = tk.Label(toolbar, bg='#ffffff', text='Price')
		label_ask_price_title.place(x=10, y=185)
		label_ask_qty_title = tk.Label(toolbar, bg='#ffffff', text='Amount')
		label_ask_qty_title.place(x=75, y=185)
		label_ask_sum_title = tk.Label(toolbar, bg='#ffffff', text='Summ')
		label_ask_sum_title.place(x=140, y=185)
		
		label_bid_price_title = tk.Label(toolbar, bg='#ffffff', text='Price')
		label_bid_price_title.place(x=205, y=185)
		label_bid_qty_title = tk.Label(toolbar, bg='#ffffff', text='Amount')
		label_bid_qty_title.place(x=270, y=185)
		label_bid_sum_title = tk.Label(toolbar, bg='#ffffff', text='Summ')
		label_bid_sum_title.place(x=335, y=185)	
		
		self.value_ask_price = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.0000')
		self.value_ask_price.place(x=10, y=205)
		self.value_ask_qty = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.0000')
		self.value_ask_qty.place(x=75, y=205)
		self.value_ask_sum = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.0000')
		self.value_ask_sum.place(x=140, y=205)
		self.value_bid_price = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.0000')
		self.value_bid_price.place(x=205, y=205)
		self.value_bid_qty = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.0000')
		self.value_bid_qty.place(x=270, y=205)
		self.value_bid_sum = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.0000')
		self.value_bid_sum.place(x=335, y=205)	

		label_funds = tk.Label(toolbar, bg='#ffffff', text='FUNDS:', font='Arial 10 bold')
		label_funds.place(x=10, y=235)

		self.quote_asset = tk.Label(toolbar, bg='#ffffff', text='Quote')
		self.quote_asset.place(x=10, y=260)
		
		self.base_asset = tk.Label(toolbar, bg='#ffffff', text='Base')
		self.base_asset.place(x=205, y=260)

		self.entry_quote = ttk.Entry(toolbar, state='disabled')
		self.entry_quote.place(x=80, y=260, width = 120)

		self.entry_base = ttk.Entry(toolbar, state='disabled')
		self.entry_base.place(x=275, y=260, width = 120)
		
		label_buy = tk.Label(toolbar, bg='#ffffff', text='BUY')
		label_buy.place(x=10, y=285)
		
		label_sell = tk.Label(toolbar, bg='#ffffff', text='SELL')
		label_sell.place(x=205, y=285)
		
		self.label_buy_qty = tk.Label(toolbar, bg='#ffffff', text='Qty')
		self.label_buy_qty.place(x=10, y=310)

		self.label_sell_qty = tk.Label(toolbar, bg='#ffffff', text='Qty')
		self.label_sell_qty.place(x=205, y=310)
		
		self.entry_buy_qty = ttk.Entry(toolbar, state='disabled')
		self.entry_buy_qty.place(x=80, y=310, width = 120)

		self.entry_sell_qty = ttk.Entry(toolbar, state='disabled')
		self.entry_sell_qty.place(x=275, y=310, width = 120)
		
		self.label_buy_price = tk.Label(toolbar, bg='#ffffff', text='Price')
		self.label_buy_price.place(x=10, y=335)

		self.label_sell_price = tk.Label(toolbar, bg='#ffffff', text='Price')
		self.label_sell_price.place(x=205, y=335)
		
		self.entry_buy_price = ttk.Entry(toolbar, state='disabled')
		self.entry_buy_price.place(x=80, y=335, width = 120)

		self.entry_sell_price = ttk.Entry(toolbar, state='disabled')
		self.entry_sell_price.place(x=275, y=335, width = 120)
		
		self.label_position = tk.Label(toolbar, bg='#ffffff', text='POSITION:', font='Arial 10 bold')
		self.label_position.place(x=10, y=360)
		label_position_last_title = tk.Label(toolbar, bg='#ffffff', text='Last')
		label_position_last_title.place(x=10, y=385)
		label_position_price_title = tk.Label(toolbar, bg='#ffffff', text='Price')
		label_position_price_title.place(x=90, y=385)
		label_position_qty_title = tk.Label(toolbar, bg='#ffffff', text='Amount')
		label_position_qty_title.place(x=170, y=385)
		label_position_sum_title = tk.Label(toolbar, bg='#ffffff', text='Sum')
		label_position_sum_title.place(x=250, y=385)
		label_position_profit_title = tk.Label(toolbar, bg='#ffffff', text='Profit, %')
		label_position_profit_title.place(x=330, y=385)
		
		self.value_position_last = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.000')
		self.value_position_last.place(x=10, y=405)		
		self.value_position_price = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.000')
		self.value_position_price.place(x=90, y=405)
		self.value_position_qty = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.000')
		self.value_position_qty.place(x=170, y=405)
		self.value_position_sum = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.000')
		self.value_position_sum.place(x=250, y=405)
		self.value_position_profit = tk.Label(toolbar, bg='#ffffff', font='Arial 8', text='0.000')
		self.value_position_profit.place(x=330, y=405)
		
		self.btn_reset_position = ttk.Button(toolbar, text='Reset', command=self.reset_position, state='disabled')
		self.btn_reset_position.place(x=275, y=360, width=60, height=20)
		
		self.btn_edit_position = ttk.Button(toolbar, text='Edit', command=self.open_dialog, state='disabled')
		self.btn_edit_position.place(x=345, y=360, width=50, height=20)

		btn_reset_log = ttk.Button(toolbar, text='Clear Logs', command=self.reset_log)
		btn_reset_log.place(x=665, y=160, width=120, height=20)

		label_logs = tk.Label(toolbar, bg='#ffffff', text='LOGS:', font='Arial 10 bold')
		label_logs.place(x=400, y=160)
		
		self.logs_box = tk.Text(toolbar, font='Arial 10', wrap=tk.WORD, state='disabled')
		logs_scrollbar = tk.Scrollbar(self.logs_box)
		
		logs_scrollbar['command'] = self.logs_box.yview
		self.logs_box['yscrollcommand'] = logs_scrollbar.set
		
		self.logs_box.place(x=400, y=185, width=380, height=115)
		logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		label_trades = tk.Label(toolbar, bg='#ffffff', text='TRADES:', font='Arial 10 bold')
		label_trades.place(x=400, y=305)
		
		self.trades_box = tk.Text(toolbar, font='Arial 10', wrap=tk.WORD, state='disabled')
		trades_scrollbar = tk.Scrollbar(self.trades_box)
		
		trades_scrollbar['command'] = self.trades_box.yview
		self.trades_box['yscrollcommand'] = trades_scrollbar.set
		
		self.trades_box.place(x=400, y=330, width=380, height=115)
		trades_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		label_progress = tk.Label(toolbar, bg='#ffffff', text='Progress')
		label_progress.place(x=10, y=430)

		self.progress = ttk.Progressbar(toolbar, orient='horizontal', length=315, mode='determinate')
		self.progress.place(x=80, y=430)

		self.progress['value'] = 0
		self.progress['maximum'] = 100


		### Version ###
		label_version = tk.Label(toolbar, bg='#ffffff', text=self.ver, font='Arial 8')
		label_version.place(x=10, y=453)

	def get_access(self):
		
		self.api_is_init = False
		
		url = 'http://funnymay.com/auth/get_access.php?share='+ self.entry_share.get()
		response = requests.get(url)
		
		if response.status_code == 200 or response.status_code == 400:
			self.access_time = time.time() + float(response.text)
			
			if self.access_time > time.time():
				self.entry_key.configure(state='normal')
				self.entry_secret.configure(state='normal')
				self.entry_exchange.configure(state='normal')
				self.entry_max_buy.configure(state='normal')
				self.entry_min_sell.configure(state='normal')
				self.entry_step_size.configure(state='normal')
				self.entry_lot_size.configure(state='normal')
				self.entry_pair.configure(state='normal')
				self.entry_order_life.configure(state='normal')
				self.entry_pause.configure(state='normal')
				self.entry_update_time.configure(state='normal')
				self.btn_use.configure(state='normal')
				self.btn_start.configure(state='normal')
				self.btn_stop.configure(state='normal')
				self.entry_fee.configure(state='normal')
				self.entry_base.configure(state='normal')
				self.entry_quote.configure(state='normal')
				self.entry_buy_qty.configure(state='normal')
				self.entry_sell_qty.configure(state='normal')
				self.entry_buy_price.configure(state='normal')
				self.entry_sell_price.configure(state='normal')
				self.btn_edit_position.configure(state='normal')
				self.btn_reset_position.configure(state='normal')
				
				if int(response.text) > 1:
					self.entry_set.configure(state='normal')
					self.btn_save.configure(state='normal')
					self.btn_load.configure(state='normal')	
				
				self.db.c.execute('UPDATE init_settings SET shared_key=?, time=? WHERE id=1', (self.entry_share.get(), self.access_time))
				self.db.conn.commit()
				
				self.db.save(shared_key=self.entry_share.get(), access_time=int(self.access_time))
				self.bot.access(self.access_time)
				self.pos.access(self.access_time)
				
				if self.bot_access != True:
					self.bot_access = True
					self.log('Access granted')
			else:
				self.log('Access denied')
				self.access_time = 0
		self.get_settings()

	def trades_log(self, s): #OK
		self.trades_box.configure(state='normal')
		t = time.strftime("%m/%d %H:%M", time.localtime(time.time()))
		self.trades_box.insert(tk.END, t+' '+s+'\n')
		self.trades_box.configure(state='disable')
		self.trades_box.yview_moveto(1)

	def log(self, s): #OK
		self.logs_box.configure(state='normal')
		t = time.strftime("%m/%d %H:%M", time.localtime(time.time()))
		self.logs_box.insert(tk.END, t+' '+s+'\n')
		self.logs_box.configure(state='disable')
		self.logs_box.yview_moveto(1)

	def upd_log(self, from_s, to_s): #OK
		s = self.logs_box.get(1.0, tk.END)
		s = s.replace(from_s, to_s)
		self.logs_box.configure(state='normal')
		self.logs_box.delete(1.0, tk.END)
		self.logs_box.insert(tk.END, s[:-1])
		self.logs_box.configure(state='disable')
		self.logs_box.yview_moveto(1)

	def reset_log(self): #OK
		self.logs_box.configure(state='normal')
		self.logs_box.delete(1.0, tk.END)
		self.logs_box.configure(state='disable')
	
	def debug_log(self, s): #OK
		t = time.strftime('%m/%d %H:%M ', time.localtime())
		print(t+' '+s)
		self.error_time = time.time() + 5.0
		self.label_error.configure(text=t+' '+s)

	def start_bot(self):
		self.use_settings()
		self.bot_is_run = True
		self.log('Bot runned')
		self.buy_access = False
		self.sell_access = False
		
	def stop_bot(self):
		self.bot_is_run = False
		self.log('Bot stopped')
		self.entry_buy_qty.delete(0, tk.END)
		self.entry_buy_price.delete(0, tk.END)
		self.entry_sell_qty.delete(0, tk.END)
		self.entry_sell_price.delete(0, tk.END)
		self.label_buy_price.configure(fg='#000000')
		self.label_buy_qty.configure(fg='#000000')
		self.label_sell_price.configure(fg='#000000')
		self.label_sell_qty.configure(fg='#000000')

	def prog(self): #OK
		if self.progress['value'] < self.progress['maximum']:
			self.progress['value'] += 1
		else:
			self.progress['value'] = 0

		if time.time() > self.error_time:
			self.label_error.configure(text='')

	def load_settings(self):
		
		if time.time() < self.access_time:

			self.bot.load(set_num=self.entry_set.get())
			self.pos.load(bot=self.bot)

			self.log('Set #'+self.entry_set.get()+' loaded')
			self.bot_is_init = True
			self.view_settings()
		else:
			self.log('Access expired')
		self.get_settings()
	
	def save_settings(self):
		self.use_settings()
		if time.time() < self.access_time:
			
			self.bot.save(set_num=self.entry_set.get())
			
			self.log('Set #'+self.entry_set.get()+' saved')
		else:
			self.log('Access expired')
		self.get_settings()

	def use_settings(self):

		if self.bot_is_run == True:
			self.stop_bot()
		
		if self.bot.exchange != self.entry_exchange.get().lower() or self.bot.pair != self.entry_pair.get().lower():
			self.depth = dict()
			self.last_price = 0.0
		
		if self.bot.exchange != self.entry_exchange.get().lower():
			self.api_is_init = False

		api_key = self.entry_key.get()
		api_secret = self.entry_secret.get()
		exchange = self.entry_exchange.get().lower()
		pair = self.entry_pair.get().lower()
		order_life = float(self.entry_order_life.get())
		pause = float(self.entry_pause.get())
		upd_time = float(self.entry_update_time.get())

		max_buy = float(self.entry_max_buy.get())
		min_sell = float(self.entry_min_sell.get())
		step_size = float(self.entry_step_size.get())
		lot_size = float(self.entry_lot_size.get())
		fee = float(self.entry_fee.get())

		self.bot.upd(data={'api_key':api_key, 'api_secret':api_secret, 'exchange':exchange, 'pair':pair, 'order_life':order_life, 'pause':pause, 'upd_time':upd_time, 'max_buy':max_buy, 'min_sell':min_sell, 'step_size':step_size, 'lot_size':lot_size, 'fee':fee,})
		self.pos.upd(bot=self.bot, price=self.pos.price, qty=self.pos.qty)

		self.last_price = 0.0
		
		if self.bot_is_init == False:
			self.log('Initialization complete')
			self.bot_is_init = True
		self.view_settings()

	def view_settings(self): #OK
	
		self.entry_key.delete(0, tk.END)
		self.entry_secret.delete(0, tk.END)
		self.entry_exchange.delete(0, tk.END)
		self.entry_pair.delete(0, tk.END)
		self.entry_order_life.delete(0, tk.END)
		self.entry_pause.delete(0, tk.END)
		self.entry_update_time.delete(0, tk.END)
		self.entry_max_buy.delete(0, tk.END)
		self.entry_min_sell.delete(0, tk.END)
		self.entry_step_size.delete(0, tk.END)
		self.entry_lot_size.delete(0, tk.END)
		self.entry_fee.delete(0, tk.END)
		
		self.entry_key.insert(0, self.bot.api_key)
		self.entry_secret.insert(0, self.bot.api_secret)
		self.entry_exchange.insert(0, self.bot.exchange.capitalize())
		self.entry_pair.insert(0, self.bot.pair)
		self.entry_order_life.insert(0, self.bot.order_life)
		self.entry_pause.insert(0, self.bot.pause)
		self.entry_update_time.insert(0,self.bot.upd_time)
		self.entry_max_buy.insert(0, self.bot.max_buy)
		self.entry_min_sell.insert(0, self.bot.min_sell)
		self.entry_step_size.insert(0, self.bot.step_size)
		self.entry_lot_size.insert(0, self.bot.lot_size)
		self.entry_fee.insert(0, self.bot.fee)

	def get_settings(self): #OK
		data = self.db.get_settings_list()
		self.entry_set.configure(values=sorted(data))

	def check_new_strategy(self): #OK
		t = time.time()
		if t < self.access_time:
			if t > self.next_time_settings:
				try:
					f = open('upd.txt', 'r')
					new_set = f.read()
					f.close()
					os.remove('upd.txt')
					self.entry_set.delete(0, tk.END)
					self.entry_set.insert(0, new_set)
					if self.bot_is_run == True:
						self.load_settings()
						self.start_bot()
					else:
						self.load_settings()
				except:
					return False
				self.next_time_settings = t + 60.0

	def init_api(self): #OK
		
		if self.bot.exchange.lower() == 'binance':
			self.api = apiBinance(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		elif self.bot.exchange.lower() == 'bithumb':
			self.api = apiBithumb(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		elif self.bot.exchange.lower() == 'cex':
			self.api = apiCex(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		elif self.bot.exchange.lower() == 'dovewallet':
			self.api = apiDovewallet(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		elif self.bot.exchange.lower() == 'exmo':
			self.api = apiExmo(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		elif self.bot.exchange.lower() == 'huobi':
			self.api = apiHuobi(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		elif self.bot.exchange.lower() == 'kucoin':
			self.api = apiKucoin(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		elif self.bot.exchange.lower() == 'livecoin':
			self.api = apiLivecoin(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		elif self.bot.exchange.lower() == 'okex':
			self.api = apiOkex(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		elif self.bot.exchange.lower() == 'tidex':
			self.api = apiTidex(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		elif self.bot.exchange.lower() == 'yobit':
			self.api = apiYobit(key=self.bot.api_key, secret=self.bot.api_secret, debug=self.debug)
		
		self.rules = self.api.getRules()
		self.api_is_init = True

	def reset_position(self): #OK
		self.pos.reset()
		self.buy_access = False
		self.sell_access = False
		self.view_position(self.last_price)
		self.log('Position cleared')
	
	def view_position(self, price): #OK
		
		if self.pos.qty != 0.0 and self.pos.price != 0.0:

			aroundPrice = self.rules[self.pos.pair]['aroundPrice']
			aroundQty = self.rules[self.pos.pair]['aroundQty']
			
			formatPrice = '{:.'+str(aroundPrice)+'f}'
			formatQty = '{:.'+str(aroundQty)+'f}'
			
			last_price = str(formatPrice.format(self.last_price))
			pos_qty = str(formatQty.format(self.pos.qty))
			pos_price = str(formatPrice.format(self.pos.price))
			pos_sum = str(formatPrice.format(self.pos.price * self.pos.qty))
			pos_profit = round(100.0 * (price / self.pos.price - 1.0), 2)
			
			self.value_position_last.configure(text=last_price)
			self.value_position_price.configure(text=pos_price)
			self.value_position_qty.configure(text=pos_qty)
			self.value_position_sum.configure(text=pos_sum)
			
			if (pos_profit > 0.0):
				self.value_position_profit.configure(text='+'+str(pos_profit))
			else:
				self.value_position_profit.configure(text=str(pos_profit))
		else:
			aroundPrice = self.rules[self.bot.pair]['aroundPrice']
			aroundQty = self.rules[self.bot.pair]['aroundQty']
			
			formatPrice = '{:.'+str(aroundPrice)+'f}'
			formatQty = '{:.'+str(aroundQty)+'f}'
			
			last_price = str(formatPrice.format(self.last_price))
			self.value_position_last.configure(text=last_price)
			self.value_position_price.configure(text='0.000')
			self.value_position_qty.configure(text='0.000')
			self.value_position_sum.configure(text='0.000')
			self.value_position_profit.configure(text='0.000')

	def edit_position(self, price, qty): #OK
		
		self.pos.edit(price=price, qty=qty)
		self.view_position(self.last_price)

	def open_dialog(self):
		ChildPosition(price=self.pos.price, qty=self.pos.qty)

	def open_debug_dialog(self): #OK
		ChildDebugWindow(
		pos_price=round(self.pos.price,8),
		pos_qty=self.pos.qty,
		pos_pair=self.pos.pair,
		pos_exchange=self.pos.exchange,
		m_api_is_init=self.api_is_init,
		m_bot_is_init=self.bot_is_init,
		m_pos_is_init=self.pos_is_init,
		m_bot_is_run=self.bot_is_run,
		m_access_time=round(self.access_time),
		m_buy_access=self.buy_access,
		m_sell_access=self.sell_access,
		bot_exchange=self.bot.exchange,
		bot_pair=self.bot.pair,
		bot_pause=self.bot.pause,
		bot_order_life=self.bot.order_life,
		bot_update_time=self.bot.upd_time,
		bot_max_buy=self.bot.max_buy,
		bot_min_sell=self.bot.min_sell,
		bot_step_size=self.bot.step_size,
		bot_lot_size=self.bot.lot_size,
		bot_fee=self.fee,
		m_queue_id=self.queue_id,
		m_pos_time=round(self.pos_time),
		m_start_buy_trading=self.start_buy_trading,
		m_start_sell_trading=self.start_sell_trading,
		depth_bid_price=self.depth['bids'][0][0],
		depth_bid_qty=self.depth['bids'][0][1],
		depth_ask_price=self.depth['asks'][0][0],
		depth_ask_qty=self.depth['asks'][0][1],
		m_time=round(time.time()),
		)
	
	def get_balances(self): #OK
		balances = self.api.getBalances()
		if balances != False:
			self.balances = balances
		else:
			self.next_time_balance = time.time()
	
	def view_balances(self):
		if self.balances != dict():
			values = self.bot.pair.split('_')
			
			currency_base = values[0]
			currency_quote = values[1]
			
			self.quote_asset.configure(text=currency_quote.upper())
			self.base_asset.configure(text=currency_base.upper())
			
			self.entry_quote.delete(0, tk.END)
			self.entry_base.delete(0, tk.END)
			
			formatQty = '{:.8f}'
			
			if currency_quote in self.balances:
				quote_qty = str(formatQty.format(self.balances[currency_quote]))
			else:
				quote_qty = '0.0'
				
			if currency_base in self.balances:
				base_qty = str(formatQty.format(self.balances[currency_base]))
			else:
				base_qty = '0.0'
			
			self.entry_quote.insert(0, quote_qty)
			self.entry_base.insert(0, base_qty)

	def get_price(self): #OK
		last_price =  self.api.getPrice(pair=self.bot.pair)
		if last_price != False:
			self.last_price = last_price
		else:
			self.next_time_price = time.time()
	
	def get_depth(self):
		depth = self.api.getDepth(pair=self.bot.pair, depth=5)
		if depth != False:
			self.depth = depth
		else:
			self.next_time_depth = time.time()
	
	def view_depth(self):

		if self.depth != dict():
			
			aroundPrice = self.rules[self.bot.pair]['aroundPrice']
			aroundQty = self.rules[self.bot.pair]['aroundQty']
			
			formatPrice = '{:.'+str(aroundPrice)+'f}'
			formatQty = '{:.'+str(aroundQty)+'f}'
			
			pos_qty = str(formatQty.format(self.pos.qty))
			pos_price = str(formatPrice.format(self.pos.price))
			
			self.value_ask_price.configure(text=str(formatPrice.format(self.depth['asks'][0][0])))
			self.value_ask_qty.configure(text=str(formatQty.format(self.depth['asks'][0][1])))
			self.value_ask_sum.configure(text=str(formatPrice.format(self.depth['asks'][0][0]*self.depth['asks'][0][1])))
			self.value_bid_price.configure(text=str(formatPrice.format(self.depth['bids'][0][0])))
			self.value_bid_qty.configure(text=str(formatQty.format(self.depth['bids'][0][1])))
			self.value_bid_sum.configure(text=str(formatPrice.format(self.depth['bids'][0][0]*self.depth['bids'][0][1])))

	def get_orders(self):
		orders = self.api.getOrders(pair=self.bot.pair)
		if orders != False:
			self.orders = orders
		else:
			self.orders = list()
	
	def check_orders(self):
		if len(self.orders) > 0:
			current_time = time.time()
			for i in range(len(self.orders)):
				if self.orders[i]['time'] + self.bot.order_life < current_time:
					self.queue_id = self.orders[i]['id']
		else:
			self.queue_id = ''

	def get_trades(self):
		trades = self.api.getTrades(pair=self.bot.pair)
		if trades != False:
			self.trades = trades
	
	def check_trades(self):
		values = self.bot.pair.split('_')
		
		currency_base = values[0]
		currency_quote = values[1]
		
		aroundPrice = self.rules[self.bot.pair]['aroundPrice']
		aroundQty = self.rules[self.bot.pair]['aroundQty']
		
		formatPrice = '{:.'+str(aroundPrice)+'f}'
		formatQty = '{:.'+str(aroundQty)+'f}'
		
		if len(self.trades) > 0:
			for i in range(len(self.trades)):
				if self.trades[i]['time'] > self.pos_time:
					if self.trades[i]['side'] == 'buy':
						self.pos.buy(price=self.trades[i]['price'], qty=self.trades[i]['qty'])
						desc = 'BUY ' + str(formatQty.format(self.trades[i]['qty'])) + ' ' + currency_base.upper() + ' @ ' + str(formatPrice.format(self.trades[i]['price'])) + ' ' + currency_quote.upper()
						self.trades_log(s=desc)
						self.start_sell_trading = time.time()
					elif self.trades[i]['side'] == 'sell':
						self.pos.sell(price=self.trades[i]['price'], qty=self.trades[i]['qty'])
						desc = 'SELL ' + str(formatQty.format(self.trades[i]['qty'])) + ' ' + currency_base.upper() + ' @ ' + str(formatPrice.format(self.trades[i]['price'])) + ' ' + currency_quote.upper()
						self.trades_log(s=desc)
						self.start_buy_trading = time.time()
					self.pos_time = self.trades[i]['time']
		
	def cancel_order(self):
		if self.queue_id != '':
			if self.api.cancelOrder(pair=self.bot.pair, id=self.queue_id):
				j = 0
				count = len(self.orders)
				for i in range(count):
					if self.orders[j]['id'] == self.queue_id:
						del self.orders[j]
						j -= 1
					j += 1
				self.log('Order canceled')
				self.queue_id = ''
		else:
			self.queue_id = ''
			self.ops.clear()

	def prepair_prices(self):
		
		self.buy_access = False
		self.sell_access = False
		
		if self.depth != False and self.balances != False:
			
			sell_count = 0
			buy_count = 0
			
			values = self.bot.pair.split('_')
			currency_base = values[0]
			currency_quote = values[1]
			
			buy_price = self.depth['bids'][0][0] + self.bot.step_size
			sell_price = self.depth['asks'][0][0] - self.bot.step_size
			buy_qty = self.bot.lot_size / buy_price
			sell_qty = self.bot.lot_size*(1.0 - self.bot.fee/100) / sell_price
			
			if sell_price > self.bot.min_sell:
				self.label_sell_price.configure(fg='#000000')
				sell_count += 1
			else:
				self.label_sell_price.configure(fg='#eb4d5c')
				
			if sell_qty <= self.balances[currency_base]:
				self.label_sell_qty.configure(fg='#000000')
				sell_count += 1
			else:
				self.label_sell_qty.configure(fg='#eb4d5c')

			if buy_price < self.bot.max_buy:
				self.label_buy_price.configure(fg='#000000')
				buy_count += 1
			else:
				self.label_buy_price.configure(fg='#eb4d5c')
				
			if buy_qty*buy_price <= self.balances[currency_quote]:
				self.label_buy_qty.configure(fg='#000000')
				buy_count += 1
			else:
				self.label_buy_qty.configure(fg='#eb4d5c')
			
			if buy_count == 2:
				self.buy_access = True
			if sell_count == 2:
				self.sell_access = True
			
			aroundPrice = self.rules[self.bot.pair]['aroundPrice']
			aroundQty = self.rules[self.bot.pair]['aroundQty']
			
			formatPrice = '{:.'+str(aroundPrice)+'f}'
			formatQty = '{:.'+str(aroundQty)+'f}'
			
			if round(sell_qty,self.rules[self.bot.pair]['aroundQty']) > self.balances[currency_base]:
				while round(sell_qty,self.rules[self.bot.pair]['aroundQty']) > self.balances[currency_base]:
					sell_qty -= math.pow(0.1, self.rules[self.bot.pair]['aroundQty'])
			
			self.entry_buy_price.delete(0, tk.END)
			self.entry_buy_qty.delete(0, tk.END)
			self.entry_sell_price.delete(0, tk.END)
			self.entry_sell_qty.delete(0, tk.END)

			self.entry_buy_price.insert(0, str(formatPrice.format(buy_price)))
			self.entry_buy_qty.insert(0, str(formatQty.format(buy_qty)))
			
			self.entry_sell_price.insert(0, str(formatPrice.format(sell_price)))
			self.entry_sell_qty.insert(0, str(formatQty.format(sell_qty)))

	def prepair_trade(self):
		
		if self.entry_buy_price.get() != '' and self.entry_buy_qty.get() != '' and self.entry_sell_price.get() != '' and self.entry_sell_qty.get() != '':
		
			if self.buy_access == True and time.time() > self.start_buy_trading:
				order_price = float(self.entry_buy_price.get())
				order_qty = float(self.entry_buy_qty.get())
				if self.control_trade(order_price, order_qty) == True:
					self.send_order('buy', order_price, order_qty) ######### BUY
			
			if self.sell_access == True and time.time() > self.start_sell_trading:
				order_price = float(self.entry_sell_price.get())
				order_qty = float(self.entry_sell_qty.get())
				if self.control_trade(order_price, order_qty) == True:
					self.send_order('sell', order_price, order_qty) ######## SELL
					self.sell_trend_time = 0.0
			
	def control_trade(self, order_price, order_qty):
		counter = 0
		if self.rules[self.bot.pair]['minPrice'] > 0:
			if order_price >= self.rules[self.bot.pair]['minPrice']:
				counter += 1
			else:
				self.debug_log('code: 110. Price to low')
		else:
			counter += 1
		
		if self.rules[self.bot.pair]['minQty'] > 0:
			if order_qty >= self.rules[self.bot.pair]['minQty']:
				counter += 1
			else:
				self.debug_log('code: 111. Quantity to low')
		else:
			counter += 1
		
		if self.rules[self.bot.pair]['minSum'] > 0:
			if order_qty * order_price >= self.rules[self.bot.pair]['minSum']:
				counter += 1
			else:
				self.debug_log('code: 112. Sum to low')
		else:
			counter += 1
			
		if self.rules[self.bot.pair]['maxPrice'] > 0:
			if order_price < self.rules[self.bot.pair]['maxPrice']:
				counter += 1
			else:
				self.debug_log('code: 120. Price to high')
		else:
			counter += 1
		
		if self.rules[self.bot.pair]['maxQty'] > 0:
			if order_qty < self.rules[self.bot.pair]['maxQty']:
				counter += 1
			else:
				self.debug_log('code: 121. Quantity to high')
		else:
			counter += 1	
		
		if self.rules[self.bot.pair]['maxSum'] > 0:
			if order_qty * order_price < self.rules[self.bot.pair]['maxSum']:
				counter += 1
			else:
				self.debug_log('code: 122. Sum to high')
		else:
			counter += 1
		
		if counter == 6:
			return True
		else:
			return False
	
	def send_order(self, side, order_price, order_qty):

		if self.bot.api_key != '' and self.bot.api_secret != '':
			order = self.api.sendOrder(pair=self.bot.pair, side=side, qty=order_qty, price=order_price)
			if order != False:
				values = self.bot.pair.split('_')
				
				currency_base = values[0]
				currency_quote = values[1]
				
				aroundPrice = self.rules[self.bot.pair]['aroundPrice']
				aroundQty = self.rules[self.bot.pair]['aroundQty']
				
				formatPrice = '{:.'+str(aroundPrice)+'f}'
				formatQty = '{:.'+str(aroundQty)+'f}'

				self.last_side = side
				self.last_time = time.time() - 1.0
				self.last_id = order
				
				data = dict()
				
				data['pair'] = self.bot.pair
				data['price'] = order_price
				data['qty'] = order_qty
				data['side'] = side
				data['status'] = 'new'
				data['desc'] = side.upper() + ' ' + str(formatQty.format(order_qty)) + ' ' + currency_base.upper() + ' @ ' + str(formatPrice.format(order_price)) + ' ' + currency_quote.upper()
				
				self.log(data['desc'])
				
				self.orders.append({'id': order, 'pair': self.bot.pair, 'side': side, 'qty': order_qty, 'fill': 0.0, 'price': order_price, 'time': time.time() })
				
				if side == 'buy':
					self.start_buy_trading = time.time() + self.bot.pause
					self.buy_access = False
				elif side == 'sell':
					self.start_sell_trading = time.time() + self.bot.pause
					self.sell_access = False

	def update_main(self):
		if self.bot_access == True:
			
			if self.bot_is_init == True:
				if self.api_is_init == False:
					
					if self.test:
						self.init_api()
						self.pos_time = time.time()
					else:
						try:
							self.init_api()
							self.pos_time = time.time()
						
						except:
							if self.debug:
								self.debug_log('code: 02')
				else:
					
					if self.test:
					
						auth = False
						current_time = time.time()

						if current_time > self.next_time_depth:
							self.next_time_depth = current_time + self.bot.upd_time
							self.get_depth()
						
						if current_time > self.next_time_price:
							self.next_time_price = current_time + self.bot.upd_time
							self.get_price()
						
						if auth == False and current_time > self.next_time_balance:
							self.next_time_balance = current_time + self.bot.upd_time * 10
							auth = True
							self.get_balances()
						
						if auth == False and current_time > self.next_time_orders:
							self.next_time_orders = current_time + self.bot.upd_time * 10
							auth = True
							self.get_orders()
						
						if auth == False and current_time > self.next_time_trades:
							self.next_time_trades = current_time + self.bot.upd_time * 10
							auth = True
							self.get_trades()
						
						self.view_depth()
						
						self.view_balances()
						
						self.check_trades()
						
						self.view_position(self.last_price)

						self.check_orders()
						
						if self.bot_is_run == True:
							self.prepair_prices()
								
						if auth == False:
							auth = True

							if self.queue_id != '':
								self.cancel_order()

							if self.bot_is_run == True:
								self.prepair_trade()
					
					else:
									
						auth = False
						current_time = time.time()

						if current_time > self.next_time_depth:
							self.next_time_depth = current_time + self.bot.upd_time

							try:
								self.get_depth()
							except:
								if self.debug:
									self.debug_log('code: 10')
						
						if current_time > self.next_time_price:
							self.next_time_price = current_time + self.bot.upd_time

							try:
								self.get_price()
							except:
								if self.debug:
									self.debug_log('code: 40')
						
						if auth == False and current_time > self.next_time_balance:
							self.next_time_balance = current_time + self.bot.upd_time * 10
							auth = True

							try:
								self.get_balances()
							except:
								if self.debug:
									self.debug_log('code: 20')
						
						if auth == False and current_time > self.next_time_orders:
							self.next_time_orders = current_time + self.bot.upd_time * 10
							auth = True

							try:
								self.get_orders()
							except:
								if self.debug:
									self.debug_log('code: 50')
						
						if auth == False and current_time > self.next_time_trades:
							self.next_time_trades = current_time + self.bot.upd_time * 10
							auth = True
							
							try:
								self.get_trades()
							except:
								if self.debug:
									self.debug_log('code: 30')
						

						try:
							self.view_depth()
						except:
							if self.debug:
								self.debug_log('code: 11')
						

						try:
							self.view_balances()
						except:
							if self.debug:
								self.debug_log('code: 21')
						

						try:
							self.check_trades()
						except:
							if self.debug:
								self.debug_log('code: 31')
						
		
						try:
							self.view_position(self.last_price)
						except:
							if self.debug:
								self.debug_log('code: 41')
						
						try:
							self.check_orders()
						except:
							if self.debug:
								self.debug_log('code: 51')

						try:
							if self.bot_is_run == True:
								self.prepair_prices()
						except:
							if self.debug:
								self.debug_log('code: 60')	
								
						if auth == False:
							auth = True

							try:
								if self.queue_id != '':
									self.cancel_order()
							except:
								if self.debug:
									self.debug_log('code: 52')
							

							try:
								if self.bot_is_run == True:
									self.prepair_trade()
							except:
								if self.debug:
									self.debug_log('code: 70')	
							
			if self.api_is_init and self.debug:
				if self.api.error != False:
					self.debug_log(self.api.error)
					self.api.error = False
			if self.debug:
				if self.bot.error != '':
					self.debug_log(self.bot.error)
					self.bot.error = ''
				if self.pos.error != '':
					self.debug_log(self.pos.error)
					self.pos.error = ''
			self.prog()
			self.check_new_strategy()
		self.after(200, self.update_main)

icon = "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"

root = tk.Tk()
app = Main(root)
app.pack()
root.title("Sniperbot")
root.tk.call('wm', 'iconphoto', root._w, "-default", tk.PhotoImage(data=icon))
root.geometry("800x470+300+200")
root.resizable(False, False)
root.mainloop()


