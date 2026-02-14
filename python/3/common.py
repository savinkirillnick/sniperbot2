from math import log10
from os import remove
from os.path import isfile
from threading import Thread
from time import time, sleep, strftime, localtime

import ccxt
import requests


class Common:

    def __init__(self, app):
        self.app = app
        self.exchanges = ccxt.exchanges

    def launch(self):
        mode = ''
        if self.app.user.demo_mode:
            mode = 'in demo mode'
        self.app.gui.log(f'Welcome to {self.app.user.name} ver.{self.app.user.ver} {mode}')

        try:
            self.app.user.settings_list = self.app.db.get_settings_list()
        except Exception as e:
            self.app.errors.error(106, e)
            self.app.user.settings_list = list()

        if self.app.user.shared_key != 'demo':
            try:
                self.app.db.save_key(self.app.user.shared_key)
            except Exception as e:
                self.app.errors.error(101, e)

        Thread(target=self.update_depth, daemon=True).start()
        Thread(target=self.update_price, daemon=True).start()
        Thread(target=self.update_orders, daemon=True).start()
        Thread(target=self.update_trades, daemon=True).start()
        Thread(target=self.update_balances, daemon=True).start()
        Thread(target=self.update_main, daemon=True).start()

    def update_depth(self):

        def get_depth():
            try:
                depth = self.app.api.fetch_order_book(self.app.user.rules[self.app.bot.pair]['symbol'], None)
            except Exception as e:
                self.app.errors.error(128, e)
                depth = dict()
            if depth:
                self.app.user.depth = depth

        while True:
            try:
                if self.app.user.bot_is_init and self.app.user.api_is_init:
                    get_depth()
                    self.app.gui.win_main.progress(self.app.gui.win_main.progress_depth)
                    if self.app.gui.win_depth.winfo_exists():
                        self.app.gui.win_depth.view_depth()
                sleep(self.app.bot.upd_time)
            except Exception as e:
                self.app.errors.error(152, e)

    def update_price(self):

        def get_price():
            try:
                last_price = self.app.api.fetch_ticker(self.app.user.rules[self.app.bot.pair]['symbol'])
            except Exception as e:
                self.app.errors.error(127, e)
                last_price = dict()
            if last_price:
                self.app.user.last_price = last_price['last']
                if self.app.user.kl_is_init is not True:
                    self.app.user.kl_is_init = True
                self.app.kline.add(self.app.user.last_price)
                if self.app.strategy.sell_at.lower() == 'stop':
                    self.app.trailing.check()

        while True:
            try:
                if self.app.user.bot_is_init and self.app.user.api_is_init:
                    get_price()
                    if self.app.user.bot_is_run and self.app.user.last_price:
                        self.app.strategy.check(self.app.user.last_price, self.app.position.price)
                    self.app.gui.win_main.progress(self.app.gui.win_main.progress_price)
                    if self.app.gui.win_chart.winfo_exists():
                        self.app.gui.win_chart.canvas.forget()
                        self.app.gui.win_chart.draw()
                sleep(self.app.bot.upd_time)
            except Exception as e:
                self.app.errors.error(153, e)

    def update_orders(self):

        def get_orders():
            try:
                orders = self.app.api.fetch_open_orders(self.app.user.rules[self.app.bot.pair]['symbol'])
            except Exception as e:
                self.app.errors.error(130, e)
                orders = list()

            if orders:
                self.app.user.orders = orders
            else:
                self.app.user.orders = list()

        def check_orders():
            if len(self.app.user.orders) > 0:
                current_time = time()
                try:
                    for i in range(len(self.app.user.orders)):
                        if self.app.user.orders[i]['timestamp'] / 1000 + self.app.bot.order_life < current_time:
                            self.app.user.queue_id = self.app.user.orders[i]['id']
                            self.app.user.queue_side = self.app.user.orders[i]['side']
                except Exception as e:
                    self.app.errors.error(132, e)
            else:
                self.app.user.queue_id = ''
                self.app.user.queue_side = ''

        def cancel_order(order_id=''):
            id = order_id if order_id != '' else self.app.user.queue_id if self.app.user.queue_id != '' else ''
            if id != '':
                try:
                    cancel = self.app.api.cancel_order(id, self.app.user.rules[self.app.bot.pair]['symbol'])
                except Exception as e:
                    self.app.errors.error(131, e)
                    cancel = 0
                if cancel:
                    self.app.gui.log('Order canceled')
                    self.app.user.queue_id = ''

                    if self.app.user.queue_side.lower() == 'buy':
                        self.app.user.start_buy_trading = time()
                    elif self.app.user.queue_side.lower() == 'sell':
                        self.app.user.start_sell_trading = time()
                    self.app.user.queue_side = ''

                    for i in range(len(self.app.user.orders)):
                        if self.app.user.orders[i]['id'] == id:
                            del self.app.user.orders[i]
                            break
                    if self.app.gui.win_orders.winfo_exists():
                        self.app.gui.win_orders.view_orders()
                    return True
            return False

        while True:
            try:
                if self.app.ttimer.check(time()):
                    if self.app.user.bot_is_init and self.app.user.api_is_init:
                        get_orders()
                        check_orders()
                        if len(self.app.user.orders) > 0 and self.app.user.queue_id != '':
                            cancel_order(self.app.user.queue_id)
                        else:
                            self.app.user.queue_id = ''
                        self.app.gui.win_main.progress(self.app.gui.win_main.progress_orders)
                        if self.app.gui.win_orders.winfo_exists():
                            self.app.gui.win_orders.view_orders()
                    sleep(10)
                else:
                    sleep(1)
            except Exception as e:
                self.app.errors.error(154, e)

    def update_trades(self):

        def get_trades():
            try:
                trades = self.app.api.fetch_my_trades(self.app.user.rules[self.app.bot.pair]['symbol'], None)

            except Exception as e:
                self.app.errors.error(134, e)
                trades = list()

            if trades:
                self.app.user.trades = trades if len(trades) < 10 else trades[-10:]

        def check_trades():

            if len(self.app.user.trades) > 0:
                try:
                    tmp = list()
                    for i in range(len(self.app.user.trades)):
                        if self.app.user.trades[i]['timestamp'] / 1000 > self.app.user.last_trade_time:
                            tmp.append(self.app.user.trades[i])
                            if self.app.user.trades[i]['side'] == 'buy':
                                self.app.position.buy(price=self.app.user.trades[i]['price'], qty=self.app.user.trades[i]['amount'])
                                self.app.strategy.buy(price=self.app.user.trades[i]['price'], qty=self.app.user.trades[i]['amount'])

                                try:
                                    self.app.db.save_position(exchange=self.app.pos.exchange, pair=self.app.pos.pair, price=self.app.pos.price, qty=self.app.pos.qty)
                                except Exception as e:
                                    self.app.errors.error(110, e)

                                try:
                                    self.app.db.save_strategy(exchange=self.app.bot.exchange, pair=self.app.bot.pair,
                                                              data={'sell_price': self.app.bot.sell_price,
                                                                    'buy_price': self.app.bot.buy_price,
                                                                    'sell_qty': self.app.bot.sell_qty,
                                                                    'buy_qty': self.app.bot.buy_qty,
                                                                    'depo': self.app.bot.depo,
                                                                    'depo_ex': self.app.strategy.depo_ex,
                                                                    'exchange': self.app.bot.exchange,
                                                                    'pair': self.app.bot.pair,
                                                                    'buy_type': self.app.bot.buy_type,
                                                                    'sell_type': self.app.bot.sell_type})
                                except Exception as e:
                                    self.app.errors.error(112, e)
                                self.app.user.start_sell_trading = time()
                            elif self.app.user.trades[i]['side'] == 'sell':
                                self.app.position.sell(price=self.app.user.trades[i]['price'], qty=self.app.user.trades[i]['amount'])
                                self.app.strategy.sell(price=self.app.user.trades[i]['price'], qty=self.app.user.trades[i]['amount'])
                                try:
                                    self.app.db.save_position(exchange=self.app.position.exchange, pair=self.app.position.pair, price=self.app.position.price, qty=self.app.position.qty)
                                except Exception as e:
                                    self.app.errors.error(110, e)
                                try:
                                    self.app.db.save_strategy(exchange=self.app.bot.exchange, pair=self.app.bot.pair,
                                                              data={'sell_price': self.app.bot.sell_price,
                                                                    'buy_price': self.app.bot.buy_price,
                                                                    'sell_qty': self.app.bot.sell_qty,
                                                                    'buy_qty': self.app.bot.buy_qty,
                                                                    'depo': self.app.bot.depo,
                                                                    'depo_ex': self.app.strategy.depo_ex,
                                                                    'exchange': self.app.bot.exchange,
                                                                    'pair': self.app.bot.pair,
                                                                    'buy_type': self.app.bot.buy_type,
                                                                    'sell_type': self.app.bot.sell_type})
                                except Exception as e:
                                    self.app.errors.error(112, e)
                                self.app.user.start_buy_trading = time()
                                if self.app.strategy.last_buy_step == 0:
                                    self.app.user.start_sell_trading = time()
                                self.app.trailing.reset()
                                if self.app.user.balances[self.app.user.curr_base.upper()]['free'] < self.app.user.rules[self.app.bot.pair]['minQty'] and not len(self.app.user.orders):
                                    self.reset_position()

                            self.app.user.last_trade_time = self.app.user.trades[i]['timestamp'] / 1000
                    self.app.stat.use_trades(tmp)
                except Exception as e:
                    self.app.errors.error(135, e)

        def check_pos():
            if self.app.position.qty > 0:
                if self.app.user.rules[self.app.bot.pair]['minQty'] > 0:
                    if self.app.position.qty < self.app.user.rules[self.app.bot.pair]['minQty']:
                        self.reset_position()
                if self.app.user.rules[self.app.bot.pair]['minSum'] > 0:
                    if self.app.user.last_price * self.app.position.qty < self.app.user.rules[self.app.bot.pair]['minSum']:
                        self.reset_position()

        while True:
            try:
                if self.app.ttimer.check(time()):
                    if self.app.user.bot_is_init and self.app.user.api_is_init:
                        get_trades()
                        check_trades()
                        check_pos()
                        self.app.gui.win_main.progress(self.app.gui.win_main.progress_trades)
                        if self.app.gui.win_trades.winfo_exists():
                            self.app.gui.win_trades.view_trades()
                    sleep(10)
                else:
                    sleep(1)
            except Exception as e:
                self.app.errors.error(155, e)

    def update_balances(self):
        def get_balances():
            try:
                balances = self.app.api.fetch_balance()
            except Exception as e:
                self.app.errors.error(137, e)
                balances = dict()

            if balances is not dict():
                self.app.user.balances = balances
                if self.app.user.curr_quote.upper() not in balances.keys():
                    self.app.user.balances[self.app.user.curr_quote.upper()] = dict()
                    self.app.user.balances[self.app.user.curr_quote.upper()]['free'] = 0.0
                    self.app.user.balances[self.app.user.curr_quote.upper()]['used'] = 0.0
                    self.app.user.balances[self.app.user.curr_quote.upper()]['total'] = 0.0
                if self.app.user.curr_base.upper() not in balances.keys():
                    self.app.user.balances[self.app.user.curr_base.upper()] = dict()
                    self.app.user.balances[self.app.user.curr_base.upper()]['free'] = 0.0
                    self.app.user.balances[self.app.user.curr_base.upper()]['used'] = 0.0
                    self.app.user.balances[self.app.user.curr_base.upper()]['total'] = 0.0

        while True:
            try:
                if self.app.ttimer.check(time()):
                    if self.app.user.bot_is_init and self.app.user.api_is_init:
                        get_balances()
                        self.app.gui.win_main.progress(self.app.gui.win_main.progress_balances)
                    sleep(10)
                else:
                    sleep(1)
            except Exception as e:
                self.app.errors.error(156, e)

    def update_main(self):

        def check_new_strategy():
            if self.app.user.activation.check():
                if time() > self.app.user.next_time_settings:
                    try:
                        if isfile('upd.txt'):
                            f = open('upd.txt', 'r')
                            new_set = f.read()
                            f.close()
                            remove('upd.txt')
                            self.load_set(new_set)
                            if self.app.user.bot_is_run is True:
                                self.start_bot()
                    except Exception as e:
                        self.app.errors.error(119, e)
                    self.app.user.next_time_settings = time() + 60.0

        while True:
            try:
                if self.app.user.bot_is_init and self.app.user.api_is_init:
                    self.prepare_prices()

                    if self.app.gui.win_terminal.winfo_exists():
                        self.app.gui.win_terminal.view_terminal()

                    if self.app.user.bot_is_run and self.app.user.last_price:
                        if self.app.ttimer.check(time()):
                            self.prepare_trade()

                    if self.app.user.stat_is_init is False:
                        self.init_stat_data()

                    check_new_strategy()
                    self.check_alarm()

                    self.app.gui.win_main.progress(self.app.gui.win_main.progress_main)
                sleep(1.0)

            except Exception as e:
                self.app.errors.error(157, e)

    def cancel_order(self, order_id=''):
        id = order_id if order_id != '' else self.app.user.queue_id if self.app.user.queue_id != '' else ''
        if id != '':
            try:
                cancel = self.app.api.cancel_order(id, self.app.user.rules[self.app.bot.pair]['symbol'])
            except Exception as e:
                self.app.errors.error(131, e)
                cancel = 0
            if cancel:
                self.app.gui.log('Order canceled')
                self.app.user.queue_id = ''

                if self.app.user.queue_side.lower() == 'buy':
                    self.app.user.start_buy_trading = time()
                elif self.app.user.queue_side.lower() == 'sell':
                    self.app.user.start_sell_trading = time()
                self.app.user.queue_side = ''

                for i in range(len(self.app.user.orders)):
                    if self.app.user.orders[i]['id'] == id:
                        del self.app.user.orders[i]
                        break
                if self.app.gui.win_orders.winfo_exists():
                    self.app.gui.win_orders.view_orders()
                return True
        return False

    def reset_position(self):
        self.app.position.reset()
        self.app.strategy.reset()
        self.app.trailing.reset()
        self.app.user.buy_access = False
        self.app.user.sell_access = False

        try:
            self.app.db.save_position(exchange=self.app.bot.exchange, pair=self.app.bot.pair, price=0.0, qty=0.0)
        except Exception as e:
            self.app.errors.error(110, e)
        try:
            self.app.db.save_strategy(exchange=self.app.bot.exchange, pair=self.app.bot.pair,
                                      data={'sell_price': self.app.bot.sell_price,
                                            'buy_price': self.app.bot.buy_price,
                                            'sell_qty': self.app.bot.sell_qty,
                                            'buy_qty': self.app.bot.buy_qty,
                                            'depo': self.app.bot.depo,
                                            'depo_ex': self.app.strategy.depo_ex,
                                            'exchange': self.app.bot.exchange,
                                            'pair': self.app.bot.pair,
                                            'buy_type': self.app.bot.buy_type,
                                            'sell_type': self.app.bot.sell_type})
        except Exception as e:
            self.app.errors.error(112, e)
        self.app.gui.log('Position cleared')
        return 0

    def start_bot(self):
        self.app.user.bot_is_run = True
        self.app.user.buy_access = False
        self.app.user.sell_access = False
        self.app.gui.log('Bot started')
        self.app.gui.win_main.indicator_run.config(image=self.app.gui.win_main.icon_play)

    def stop_bot(self):
        self.app.user.bot_is_run = False
        self.app.user.buy_qty = 0.0
        self.app.user.buy_price = 0.0
        self.app.user.buy_access = False
        self.app.user.sell_qty = 0.0
        self.app.user.sell_price = 0.0
        self.app.user.sell_access = False
        self.app.strategy.next_buy_price = 0.0
        self.app.strategy.next_sell_price = 0.0
        self.app.strategy.next_buy_lot = 0.0
        self.app.strategy.next_sell_lot = 0.0

        if self.app.gui.win_terminal.winfo_exists():
            self.app.gui.win_terminal.entry_buy_price.delete(0, self.app.gui.tk.END)
            self.app.gui.win_terminal.entry_buy_qty.delete(0, self.app.gui.tk.END)
            self.app.gui.win_terminal.entry_sell_price.delete(0, self.app.gui.tk.END)
            self.app.gui.win_terminal.entry_sell_qty.delete(0, self.app.gui.tk.END)
            self.app.gui.win_terminal.label_buy_price.configure(fg='#000000')
            self.app.gui.win_terminal.label_buy_qty.configure(fg='#000000')
            self.app.gui.win_terminal.label_sell_price.configure(fg='#000000')
            self.app.gui.win_terminal.label_sell_qty.configure(fg='#000000')

        self.app.gui.log('Bot stoped')
        self.app.gui.win_main.indicator_run.config(image=self.app.gui.win_main.icon_stop)

    def update_settings(self, data={}):
        if not data:
            data = self.app.gui.win_settings.get_set_data()

        if self.app.user.bot_is_run:
            self.stop_bot()
        if self.app.bot.exchange != data['exchange'].lower() or self.app.bot.pair != data['pair'].lower():
            self.app.user.depth['bids'] = list()
            self.app.user.depth['asks'] = list()
            self.app.user.trades = list()
            self.app.user.orders = list()
            self.app.user.kl_is_init = False
            self.app.kline.reset()
            self.app.user.stat_is_init = False

        self.app.gui.root.title(self.app.user.name + ' ' + self.app.user.ver + ' > ' + data['exchange'].capitalize() + ' > ' + data['pair'].upper())

        if self.app.bot.exchange != data['exchange'].lower():
            self.app.user.api_is_init = False

        self.app.bot.upd(data)
        self.app.position.upd()
        self.app.strategy.upd(data)
        self.app.stat.set_depo(self.app.bot.depo)
        self.app.user.curr_base = data['pair'].split('_')[0]
        self.app.user.curr_quote = data['pair'].split('_')[1]

        self.app.user.bot_is_init = True
        self.app.user.pos_is_init = True
        self.app.user.st_is_init = True

        self.app.gui.log(self.app.user.name + ' settings updated')

        while not self.app.user.api_is_init:
            try:
                self.api_init()
            except Exception as e:
                self.app.errors.error(125, e)
                self.app.gui.log(str(e))
                self.app.bot.clear()
                self.app.position.clear()
                break

    def delete_set(self):
        try:
            self.app.db.del_bot_settings(self.app.gui.win_settings.entry_set.get())
        except Exception as e:
            self.app.errors.error(103, e)
        self.app.user.settings_list = self.app.db.get_settings_list()
        self.app.gui.win_settings.entry_set.configure(values=self.app.user.settings_list)
        self.app.gui.log('Set #' + self.app.gui.win_settings.entry_set.get() + ' deleted')

    def save_set(self):
        self.update_settings()
        data = self.app.gui.win_settings.get_set_data()
        try:
            self.app.db.save_bot_settings(self.app.gui.win_settings.entry_set.get(), data)
        except Exception as e:
            self.app.errors.error(104, e)
        self.app.user.settings_list = self.app.db.get_settings_list()
        self.app.gui.win_settings.entry_set.configure(values=self.app.user.settings_list)
        self.app.gui.log('Set #' + self.app.gui.win_settings.entry_set.get() + ' saved')

    def load_set(self, set_num=''):
        if not set_num:
            set_num = self.app.gui.win_settings.entry_set.get()
        try:
            if set_num:
                data = self.app.db.load_bot_settings(set_num)
            else:
                data = self.app.db.load_bot_settings(self.app.gui.win_settings.entry_set.get())

            self.update_settings(data)

            if self.app.gui.win_settings.winfo_exists():
                self.app.gui.win_settings.view_settings()

            self.app.gui.log('Set #' + self.app.gui.win_settings.entry_set.get() + ' loaded')
        except Exception as e:
            self.app.errors.error(105, e)
            self.app.gui.log('Set #' + self.app.gui.win_settings.entry_set.get() + ' is not loaded')

        try:
            self.app.alarm.upd(self.app.db.load_alarm(self.app.bot.exchange, self.app.bot.pair))
        except Exception as e:
            self.app.errors.error(115, e)
        self.app.bot.num_set = self.app.gui.win_settings.entry_set.get()
        price, qty = 0.0, 0.0
        try:
            price, qty = self.app.db.load_position(self.app.bot.exchange, self.app.bot.pair)
        except Exception as e:
            self.app.errors.error(111, e)
        self.app.position.set_data({'exchange': self.app.bot.exchange, 'pair': self.app.bot.pair, 'price': price, 'qty': qty})
        try:
            self.app.strategy.upd(self.app.db.load_strategy(exchange=self.app.bot.exchange, pair=self.app.bot.pair))
        except Exception as e:
            self.app.errors.error(113, e)
        self.app.trailing.upd()
        self.app.trailing.reset()

    def api_init(self):

        x = self.app.bot.exchange.lower()

        ccxt_api = {
            'ace': ccxt.ace,
            'alpaca': ccxt.alpaca,
            'ascendex': ccxt.ascendex,
            'bequant': ccxt.bequant,
            'bigone': ccxt.bigone,
            'binance': ccxt.binance,
            'binancecoinm': ccxt.binancecoinm,
            'binanceus': ccxt.binanceus,
            'binanceusdm': ccxt.binanceusdm,
            'bingx': ccxt.bingx,
            'bit2c': ccxt.bit2c,
            'bitbank': ccxt.bitbank,
            'bitbay': ccxt.bitbay,
            'bitbns': ccxt.bitbns,
            'bitcoincom': ccxt.bitcoincom,
            'bitfinex': ccxt.bitfinex,
            'bitfinex2': ccxt.bitfinex2,
            'bitflyer': ccxt.bitflyer,
            'bitget': ccxt.bitget,
            'bithumb': ccxt.bithumb,
            'bitmart': ccxt.bitmart,
            'bitmex': ccxt.bitmex,
            'bitopro': ccxt.bitopro,
            'bitpanda': ccxt.bitpanda,
            'bitrue': ccxt.bitrue,
            'bitso': ccxt.bitso,
            'bitstamp': ccxt.bitstamp,
            'bitteam': ccxt.bitteam,
            'bitvavo': ccxt.bitvavo,
            'bl3p': ccxt.bl3p,
            'blockchaincom': ccxt.blockchaincom,
            'blofin': ccxt.blofin,
            'btcalpha': ccxt.btcalpha,
            'btcbox': ccxt.btcbox,
            'btcmarkets': ccxt.btcmarkets,
            'btcturk': ccxt.btcturk,
            'bybit': ccxt.bybit,
            'cex': ccxt.cex,
            'coinbase': ccxt.coinbase,
            'coinbaseadvanced': ccxt.coinbaseadvanced,
            'coinbaseexchange': ccxt.coinbaseexchange,
            'coinbaseinternational': ccxt.coinbaseinternational,
            'coincheck': ccxt.coincheck,
            'coinex': ccxt.coinex,
            'coinlist': ccxt.coinlist,
            'coinmate': ccxt.coinmate,
            'coinmetro': ccxt.coinmetro,
            'coinone': ccxt.coinone,
            'coinsph': ccxt.coinsph,
            'coinspot': ccxt.coinspot,
            'cryptocom': ccxt.cryptocom,
            'currencycom': ccxt.currencycom,
            'delta': ccxt.delta,
            'deribit': ccxt.deribit,
            'digifinex': ccxt.digifinex,
            'exmo': ccxt.exmo,
            'fmfwio': ccxt.fmfwio,
            'gate': ccxt.gate,
            'gateio': ccxt.gateio,
            'gemini': ccxt.gemini,
            'hashkey': ccxt.hashkey,
            'hitbtc': ccxt.hitbtc,
            'hitbtc3': ccxt.hitbtc3,
            'hollaex': ccxt.hollaex,
            'htx': ccxt.htx,
            'huobi': ccxt.huobi,
            'huobijp': ccxt.huobijp,
            'hyperliquid': ccxt.hyperliquid,
            'idex': ccxt.idex,
            'independentreserve': ccxt.independentreserve,
            'indodax': ccxt.indodax,
            'kraken': ccxt.kraken,
            'krakenfutures': ccxt.krakenfutures,
            'kucoin': ccxt.kucoin,
            'kucoinfutures': ccxt.kucoinfutures,
            'kuna': ccxt.kuna,
            'latoken': ccxt.latoken,
            'lbank': ccxt.lbank,
            'luno': ccxt.luno,
            'lykke': ccxt.lykke,
            'mercado': ccxt.mercado,
            'mexc': ccxt.mexc,
            'ndax': ccxt.ndax,
            'novadax': ccxt.novadax,
            'oceanex': ccxt.oceanex,
            'okcoin': ccxt.okcoin,
            'okx': ccxt.okx,
            'onetrading': ccxt.onetrading,
            'oxfun': ccxt.oxfun,
            'p2b': ccxt.p2b,
            'paradex': ccxt.paradex,
            'paymium': ccxt.paymium,
            'phemex': ccxt.phemex,
            'poloniex': ccxt.poloniex,
            'poloniexfutures': ccxt.poloniexfutures,
            'probit': ccxt.probit,
            'timex': ccxt.timex,
            'tokocrypto': ccxt.tokocrypto,
            'tradeogre': ccxt.tradeogre,
            'upbit': ccxt.upbit,
            'vertex': ccxt.vertex,
            'wavesexchange': ccxt.wavesexchange,
            'wazirx': ccxt.wazirx,
            'whitebit': ccxt.whitebit,
            'woo': ccxt.woo,
            'woofipro': ccxt.woofipro,
            'xt': ccxt.xt,
            'yobit': ccxt.yobit,
            'zaif': ccxt.zaif,
            'zonda': ccxt.zonda
        }

        try:
            if x in ccxt.exchanges:

                # Получаем список наобходимых данных
                required = ccxt_api[x].requiredCredentials

                # Формируем словарь аргументов
                args = dict()
                args.update({key: self.app.bot.opt_key for key in required})
                args.update({'apiKey': self.app.bot.api_key, 'secret': self.app.bot.api_secret})

                # запускаем инициализацию api
                self.app.api = ccxt_api[x](args)

        except Exception as e:

            self.app.gui.log('Initialization API error. Change exchange to another and try again.')
            self.app.api = None

        if self.app.api:
            server_time = 0.0

            if not server_time:
                try:
                    server_time = self.app.api.fetch_time()
                except:
                    pass

            if not server_time:
                try:
                    server_time = self.app.api.fetch_ticker(self.app.api.fetch_markets()[0]['symbol'])['timestamp']
                except:
                    pass

            if not server_time:
                server_time = time() * 1000

            self.app.user.delta_time = time() - server_time / 1000

            rules = self.app.api.load_markets()

            self.app.user.rules = {}
            self.app.user.coins = set()
            self.app.user.pairs = set()

            for symbol in rules:
                if 'type' in rules[symbol]:
                    if rules[symbol]['type'] != 'spot':
                        break
                base_asset = rules[symbol]['base'].lower()
                quote_asset = rules[symbol]['quote'].lower()
                pair = base_asset + '_' + quote_asset
                self.app.user.coins.add(base_asset)
                self.app.user.coins.add(quote_asset)
                self.app.user.pairs.add(pair)

                self.app.user.rules[pair] = {}
                self.app.user.rules[pair]['symbol'] = symbol
                if 'limits' in rules[symbol]:
                    if 'price' in rules[symbol]['limits']:
                        if 'min' in rules[symbol]['limits']['price']:
                            self.app.user.rules[pair]['minPrice'] = float(
                                rules[symbol]['limits']['price']['min']) if isinstance(
                                rules[symbol]['limits']['price']['min'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['minPrice'] = 0.0
                        if 'max' in rules[symbol]['limits']['price']:
                            self.app.user.rules[pair]['maxPrice'] = float(
                                rules[symbol]['limits']['price']['max']) if isinstance(
                                rules[symbol]['limits']['price']['max'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['maxPrice'] = 0.0
                    else:
                        self.app.user.rules[pair]['minPrice'] = 0.0
                        self.app.user.rules[pair]['maxPrice'] = 0.0
                    if 'amount' in rules[symbol]['limits']:
                        if 'min' in rules[symbol]['limits']['amount']:
                            self.app.user.rules[pair]['minQty'] = float(rules[symbol]['limits']['amount']['min']) if isinstance(
                                rules[symbol]['limits']['amount']['min'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['minQty'] = 0.0
                        if 'max' in rules[symbol]['limits']['amount']:
                            self.app.user.rules[pair]['maxQty'] = float(rules[symbol]['limits']['amount']['max']) if isinstance(
                                rules[symbol]['limits']['amount']['max'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['maxQty'] = 0.0
                    else:
                        self.app.user.rules[pair]['minQty'] = 0.0
                        self.app.user.rules[pair]['maxQty'] = 0.0
                    if 'cost' in rules[symbol]['limits']:
                        if 'min' in rules[symbol]['limits']['cost']:
                            self.app.user.rules[pair]['minSum'] = float(rules[symbol]['limits']['cost']['min']) if isinstance(
                                rules[symbol]['limits']['cost']['min'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['minSum'] = 0.0
                        if 'max' in rules[symbol]['limits']['cost']:
                            self.app.user.rules[pair]['maxSum'] = float(rules[symbol]['limits']['cost']['max']) if isinstance(
                                rules[symbol]['limits']['cost']['max'], (int, float)) else 0.0
                        else:
                            self.app.user.rules[pair]['maxSum'] = 0.0
                    else:
                        self.app.user.rules[pair]['minSum'] = 0.0
                        self.app.user.rules[pair]['maxSum'] = 0.0
                else:
                    self.app.user.rules[pair]['minPrice'] = 0.0
                    self.app.user.rules[pair]['maxPrice'] = 0.0
                    self.app.user.rules[pair]['minQty'] = 0.0
                    self.app.user.rules[pair]['maxQty'] = 0.0
                    self.app.user.rules[pair]['minSum'] = 0.0
                    self.app.user.rules[pair]['maxSum'] = 0.0

                if 'precision' in rules[symbol]:
                    if 'price' in rules[symbol]['precision']:
                        self.app.user.rules[pair]['aroundPrice'] = int(rules[symbol]['precision']['price']) if isinstance(
                            rules[symbol]['precision']['price'], int) else int(
                            abs(log10(float(rules[symbol]['precision']['price']))))
                    else:
                        self.app.user.rules[pair]['aroundPrice'] = 8
                    if 'amount' in rules[symbol]['precision']:
                        self.app.user.rules[pair]['aroundQty'] = int(rules[symbol]['precision']['amount']) if isinstance(
                            rules[symbol]['precision']['amount'], int) else int(
                            abs(log10(float(rules[symbol]['precision']['amount']))))
                    else:
                        self.app.user.rules[pair]['aroundQty'] = 8
                else:
                    self.app.user.rules[pair]['aroundPrice'] = 8
                    self.app.user.rules[pair]['aroundQty'] = 8

            self.app.user.api_is_init = True
            self.app.kline.upd(delta=self.app.user.delta_time)
            self.app.gui.log('Bot ready for trading on ' + self.app.bot.exchange.capitalize())

    def control_trade(self, order_price, order_qty):
        counter = 0
        try:
            if self.app.user.rules[self.app.bot.pair]['minPrice'] > 0:
                if order_price >= self.app.user.rules[self.app.bot.pair]['minPrice']:
                    counter += 1
                else:
                    self.app.gui.log('Price less than min price: ' + str(
                        self.app.user.rules[self.app.bot.pair]['minPrice']) + ' ' + self.app.user.curr_quote.upper())
                    raise Exception('My price: ' + self.app.gui.fp(order_price) + ' < Minimal price: ' + self.app.gui.fp(self.app.user.botst.rules[self.app.bot.pair]['minPrice']))
            else:
                counter += 1

            if self.app.user.rules[self.app.bot.pair]['minQty'] > 0:
                if order_qty >= self.app.user.rules[self.app.bot.pair]['minQty']:
                    counter += 1
                else:
                    self.app.gui.log('Qty less than min qty: ' + str(
                        self.app.user.rules[self.app.bot.pair]['minQty']) + ' ' + self.app.user.curr_base.upper())
                    raise Exception('My amount: ' + self.app.gui.fq(order_qty) + ' < Minimal amount: ' + self.app.gui.fq(self.app.user.rules[self.app.bot.pair]['minQty']))
            else:
                counter += 1

            if self.app.user.rules[self.app.bot.pair]['minSum'] > 0:
                if order_qty * order_price >= self.app.user.rules[self.app.bot.pair]['minSum']:
                    counter += 1
                else:
                    self.app.gui.log('Sum less than min sum: ' + str(
                        self.app.user.rules[self.app.bot.pair]['minSum']) + ' ' + self.app.user.curr_quote.upper())
                    raise Exception('My sum: ' + self.app.gui.fp(order_qty * order_price) + ' < Minimal sum: ' + self.app.gui.fp(self.app.user.rules[self.app.bot.pair]['minSum']))
            else:
                counter += 1

            if self.app.user.rules[self.app.bot.pair]['maxPrice'] > 0:
                if order_price < self.app.user.rules[self.app.bot.pair]['maxPrice']:
                    counter += 1
                else:
                    self.app.gui.log('Price more than max price: ' + str(
                        self.app.user.rules[self.app.bot.pair]['maxPrice']) + ' ' + self.app.user.curr_quote.upper())
                    raise Exception('My price: ' + self.app.gui.fp(order_price) + ' > Maximal price: ' + self.app.gui.fp(self.app.user.rules[self.app.bot.pair]['maxPrice']))
            else:
                counter += 1

            if self.app.user.rules[self.app.bot.pair]['maxQty'] > 0:
                if order_qty < self.app.user.rules[self.app.bot.pair]['maxQty']:
                    counter += 1
                else:
                    self.app.gui.log('Qty more than max qty: ' + str(
                        self.app.user.rules[self.app.bot.pair]['maxQty']) + ' ' + self.app.user.curr_base.upper())
                    raise Exception('My amount: ' + self.app.gui.fq(order_qty) + ' > Maximal amount: ' + self.app.gui.fq(self.app.user.rules[self.app.bot.pair]['maxQty']))
            else:
                counter += 1

            if self.app.user.rules[self.app.bot.pair]['maxSum'] > 0:
                if order_qty * order_price < self.app.user.rules[self.app.bot.pair]['maxSum']:
                    counter += 1
                else:
                    self.app.gui.log('Sum more than max sum: ' + str(
                        self.app.user.rules[self.app.bot.pair]['maxSum']) + ' ' + self.app.user.curr_quote.upper())
                    raise Exception('My sum: ' + self.app.gui.fp(order_qty * order_price) + ' > Maximal sum: ' + self.app.gui.fp(self.app.user.rules[self.app.bot.pair]['maxSum']))
            else:
                counter += 1
        except Exception as e:
            self.app.errors.error(141, e)
            counter = 0
        if counter == 6:
            return True
        else:
            return False

    def send_order(self, side, order_price, order_qty):
        if self.app.user.bot_is_init and self.app.user.api_is_init and self.app.bot.api_key != '' and self.app.bot.api_secret != '':
            order = dict()
            try:

                if side.lower() == 'buy':
                    order = self.app.api.create_limit_buy_order(self.app.user.rules[self.app.bot.pair]['symbol'], order_qty, order_price)
                elif side.lower() == 'sell':
                    order = self.app.api.create_limit_sell_order(self.app.user.rules[self.app.bot.pair]['symbol'], order_qty, order_price)

            except Exception as e:
                self.app.errors.error(140, e)
                order = dict()
            if order:

                self.app.user.last_time = time() - 1.0
                data = dict()

                data['pair'] = self.app.bot.pair
                data['price'] = order_price
                data['qty'] = order_qty
                data['side'] = side
                data['desc'] = side.upper() + ' ' + str(
                    self.app.gui.fq(order_qty)) + ' ' + self.app.user.curr_base.upper() + ' × ' + str(
                    self.app.gui.fp(order_price)) + ' ' + self.app.user.curr_quote.upper()

                self.app.gui.log(data['desc'])

                self.app.user.orders.append(
                    {'id': order['id'], 'pair': self.app.bot.pair, 'side': side, 'qty': order_qty, 'fill': 0.0,
                     'price': order_price,
                     'time': time()})

                if side == 'buy':
                    self.app.user.start_buy_trading = time() + self.app.bot.pause
                    self.app.user.buy_access = False
                elif side == 'sell':
                    self.app.user.start_sell_trading = time() + self.app.bot.pause
                    self.app.user.sell_access = False

                if self.app.gui.win_orders.winfo_exists():
                    self.app.gui.win_orders.view_orders()

                self.check_alarm(event=side, data=data['desc'])

            else:
                if side == 'buy':
                    self.app.user.start_buy_trading = time() + 10
                    self.app.user.buy_access = False
                elif side == 'sell':
                    self.app.user.start_sell_trading = time() + 10
                    self.app.user.sell_access = False

    def prepare_prices(self):

        self.app.user.buy_access = False
        self.app.user.sell_access = False
        try:
            if len(self.app.user.depth['bids']) > 0 and len(self.app.user.depth['asks']) > 0 and self.app.user.last_price != 0.0 and self.app.strategy.next_buy_price > 0 and self.app.strategy.next_sell_price > 0:

                base_qty = self.app.user.balances[self.app.user.curr_base.upper()]['free']
                quote_qty = self.app.user.balances[self.app.user.curr_quote.upper()]['free']

                actual_buy_price = self.app.strategy.buy_price
                actual_sell_price = self.app.strategy.sell_price
                bid_price = self.app.user.depth['bids'][0][0]
                ask_price = self.app.user.depth['asks'][0][0]
                last_price = self.app.user.last_price
                now = time()

                
                actual_buy_qty = actual_sell_qty = base_qty

                if self.app.strategy.buy_type.lower() == 'quote':
                    actual_buy_qty = self.app.strategy.buy_qty / actual_buy_price if actual_buy_price > 0.0 else 0.0

                if self.app.strategy.sell_type.lower() == 'quote':
                    actual_sell_qty = self.app.strategy.sell_qty / actual_sell_price if actual_sell_price > 0.0 else 0.0

                # BUY ORDER

                p_access = False
                q_access = False

                if bid_price > actual_buy_price:
                    buy_price_fg = '#eb4d5c'  # High Price
                else:
                    if now < self.app.user.start_buy_trading:
                        buy_price_fg = '#2dab3c'  # Pause
                    else:
                        buy_price_fg = '#000000'  # Ready
                        p_access = True

                if actual_buy_qty * actual_buy_price > quote_qty:
                    buy_qty_fg = '#eb4d5c'  # Low balance
                else:
                    if now < self.app.user.start_buy_trading:
                        buy_qty_fg = '#2dab3c'  # Pause
                    else:
                        buy_qty_fg = '#000000'  # Ready
                        q_access = True

                if p_access is True and q_access is True:
                    self.app.user.buy_access = True  # BUY ACCESS

                p_access = False
                q_access = False

                # SELL ORDER

                if ask_price < actual_sell_price:
                    sell_price_fg = '#eb4d5c'  # Low Price
                else:

                    if now < self.app.user.start_sell_trading:  # Проверка паузы
                        sell_price_fg = '#2dab3c'  # Pause
                    else:
                        sell_price_fg = '#000000'  # Ready
                        p_access = True

                if round(actual_sell_qty, self.app.user.rules[self.app.bot.pair]['aroundQty']) > base_qty:
                    while round(actual_sell_qty, self.app.user.rules[self.app.bot.pair]['aroundQty']) > base_qty:
                        actual_sell_qty -= 0.1 ** self.app.user.rules[self.app.bot.pair]['aroundQty']

                if actual_sell_qty > base_qty:
                    sell_qty_fg = '#eb4d5c'  # Low Balance
                else:
                    if now < self.app.user.start_sell_trading:
                        sell_qty_fg = '#2dab3c'  # Pause
                    else:
                        sell_qty_fg = '#000000'  # Ready
                        q_access = True

                if p_access is True and q_access is True:
                    self.app.userself.app.user.sell_access = True  # SELL ACCESS

                self.app.user.buy_price = actual_buy_price if actual_buy_price > 0 else 0
                self.app.user.buy_qty = actual_buy_qty if actual_buy_qty > 0 else 0
                self.app.user.sell_price = actual_sell_price if actual_sell_price > 0 else 0
                self.app.user.sell_qty = actual_sell_qty if actual_sell_qty > 0 else 0

                if self.app.gui.win_terminal.winfo_exists():
                    self.app.gui.win_terminal.label_buy_price.configure(fg=buy_price_fg)
                    self.app.gui.win_terminal.label_sell_price.configure(fg=sell_price_fg)
                    self.app.gui.win_terminal.label_buy_qty.configure(fg=buy_qty_fg)
                    self.app.gui.win_terminal.label_sell_qty.configure(fg=sell_qty_fg)
        except Exception as e:
            self.app.errors.error(142, e)

    def prepare_trade(self):
        now = time()
        if self.app.user.buy_price > 0.0 and self.app.user.buy_qty > 0.0:
            if self.app.user.buy_access is True and now > self.app.user.start_buy_trading:
                if self.control_trade(self.app.user.buy_price, self.app.user.buy_qty):
                    self.send_order('buy', self.app.user.buy_price, self.app.user.buy_qty)  # BUY

        if self.app.user.sell_price > 0.0 and self.app.user.sell_qty > 0.0:
            if self.app.user.sell_access is True and now > self.app.user.start_sell_trading:
                if self.control_trade(self.app.user.sell_price, self.app.user.sell_qty):
                    self.send_order('sell', self.app.user.sell_price, self.app.user.sell_qty)  # SELL

    def check_alarm(self, event='', data=''):
        signal = False
        if not event:
            if not self.app.user.last_alarm_time:
                self.app.user.last_alarm_time = time()

        if self.app.alarm.every == 'Event':
            if event == 'buy' and self.app.alarm.buy is True:
                signal = True
            elif event == 'sell' and self.app.alarm.sell is True:
                signal = True
        elif self.app.alarm.every == 'Period':
            period = int(self.app.alarm.h) * 3600 + int(self.app.alarm.m) * 60
            if not period:
                period = 86400
            if time() > self.app.user.last_alarm_time + period:
                signal = True
        elif self.app.alarm.every == 'Day':
            t1 = strftime("%H:%M", localtime(time()))
            t2 = self.app.alarm.h + ':' + self.app.alarm.m
            if t1 == t2 and time() > self.app.user.last_alarm_time + 86280:
                signal = True

        if signal and self.app.alarm.on.lower() == 'on':
            self.app.user.last_alarm_time = time()
            msg = 'Stepbot report\n' + self.app.bot.exchange + ' > ' + (self.app.bot.pair.replace('_', '/')).upper() + '\n'
            if self.app.alarm.stat:
                coin = self.app.bot.pair.split('_')
                msg += coin[0].upper() + ': ' + str('{:.8f}'.format(self.app.user.balances[coin[0].upper()]['total'])) + '\n'
                msg += coin[1].upper() + ': ' + str('{:.8f}'.format(self.app.user.balances[coin[1].upper()]['total'])) + '\n'
                msg += 'Sum: ' + str(self.app.gui.fp(self.app.user.balances[coin[1].upper()]['total'] + self.app.user.balances[coin[0].upper()][
                    'total'] * self.app.user.last_price)) + ' ' + coin[1].upper() + '\n'
            if event == 'buy' and self.app.alarm.buy is True:
                msg += 'Send ' + data + '\n'
            if event == 'sell' and self.app.alarm.buy is True:
                msg += 'Send ' + data + '\n'
            self.send_telegram(self.app.alarm.token, self.app.alarm.chat_id, msg)

    def send_telegram(self, token, chat_id, text):
        url = 'https://api.telegram.org/bot'
        url += token
        method = url + '/sendMessage'

        try:
            r = requests.post(method, data={
                'chat_id': chat_id,
                'text': text
            })

            if r.status_code != 200:
                raise Exception('post_text error')
        except Exception as e:
            self.app.errors.error(107, e)

    def init_stat_data(self):
        try:
            trades = self.app.api.fetch_my_trades(self.app.user.rules[self.app.bot.pair]['symbol'], None)
        except Exception as e:
            self.app.errors.error(116, e)
            trades = dict()
        if trades:
            self.app.stat.start_time = trades[0]['timestamp'] // 1000
            self.app.stat.use_trades(trades)
            self.app.user.stat_is_init = True

    def hand_buy(self):
        order_price = float(self.app.gui.win_terminal.entry_buy_price.get())
        order_qty = float(self.app.gui.win_terminal.entry_buy_qty.get())
        if self.control_trade(order_price, order_qty):
            self.send_order('buy', order_price, order_qty)  ######### BUY

    def hand_sell(self):
        order_price = float(self.app.gui.win_terminal.entry_sell_price.get())
        order_qty = float(self.app.gui.win_terminal.entry_sell_qty.get())
        if self.control_trade(order_price, order_qty):
            self.send_order('sell', order_price, order_qty)  ######## SELL