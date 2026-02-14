import json
import tkinter as tk
import webbrowser
from base64 import b64encode, b64decode
from math import log10
from threading import Thread
from time import strftime, localtime, time, sleep
from tkinter import ttk
from random import randrange


class Gui:

    def __init__(self, app):
        self.app = app
        self.tk = tk
        self.root = tk.Tk()
        self.win_main = MainWindow(False, self.root, self.app)
        self.win_depth = DepthWindow(False, self.root, self.app)
        self.win_orders = OrdersWindow(False, self.root, self.app)
        self.win_trades = TradesWindow(False, self.root, self.app)
        self.win_clocks = ClocksWindow(False, self.root, self.app)
        self.win_terminal = TerminalWindow(False, self.root, self.app)
        self.win_settings = SettingsWindow(False, self.root, self.app)
        self.win_chart = ChartWindow(False, self.root, self.app)
        self.win_alarm = AlarmWindow(False, self.root, self.app)
        self.win_position = PositionWindow(False, self.root, self.app)
        self.win_edit_position = EditPositionWindow(False, self.root, self.app)
        self.win_statistic = StatisticWindow(False, self.root, self.app)
        self.win_info = InfoWindow(False, self.root, self.app)
        self.win_debug = DebugWindow(False, self.root, self.app)

    @staticmethod
    def rand_xy():
        return '+' + str(randrange(10, 320)) + '+' + str(randrange(10, 200))

    def fp(self, price):
        around_price = self.app.user.rules[self.app.bot.pair]['aroundPrice']
        format_price = '{:.' + str(around_price) + 'f}'
        return str(format_price.format(price))

    def fq(self, qty):
        around_qty = self.app.user.rules[self.app.bot.pair]['aroundQty']
        format_qty = '{:.' + str(around_qty) + 'f}'
        return str(format_qty.format(qty))

    @staticmethod
    def _on_key_release(event):
        ctrl = (event.state & 0x4) != 0
        if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
            event.widget.event_generate("<<Cut>>")

        if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
            event.widget.event_generate("<<Paste>>")

        if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

        if event.keycode == 65 and ctrl and event.keysym.lower() != "a":
            event.widget.event_generate("<<SelectAll>>")

    def run(self):
        main_icon = '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'
        self.root.title(self.app.user.name + ' ' + self.app.user.ver)
        self.root.tk.call('wm', 'iconphoto', self.root._w, "-default", tk.PhotoImage(data=main_icon))
        self.root.bind_all("<Key>", self._on_key_release, "+")
        self.root.geometry('400x160' + self.rand_xy())
        self.root.resizable(False, False)

        self.win_main = MainWindow(True, self.root, self.app)

        self.root.mainloop()

    def log(self, s):
        self.win_main.log(s)


class MainWindow(tk.Frame):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.root = root
        self.app = app

        self.icon_alarm = tk.PhotoImage(data='R0lGODlhGQAeALMAAPP1901qf/P5/eHn6zKa2U+p4C6a2W255nO853S856HS72qGlpyut8PO0//9+v///ywAAAAAGQAeAAAEmfDJSau9OOvNu//g0zROSDXLwnhA5TBLsHiDlRQFYdXV0Dw8RWKIIygktQZvohxJEkIiQSdqVlaMmjB6IxiOA2yl+Ttwh1ND1df71aDD+FSXXE6W8fy8BNwc8lJUHGdxOUaDCQiKCHpTRxkKOJJFcwaOGZOGc5tTmJScnAkZAqClBAIeMAGrASYOKKwzrigqJhOotrm6u7wXEQA7')
        self.icon_book = tk.PhotoImage(data='R0lGODlhGwAeALMAAAF1yzyZ2U1qf3eOnhyN1FOn3oacqpCksaCxvCiX2E+q31+x4na85mF+j2qGlv///ywAAAAAGwAeAAAEbvDJSau9OOvNu/9g6CVkWUpOqqoX4L6vJMw0fTF4nktI7/uioJBiKqJWqwthyWRKGtBo9KbT8X6/oVak6Hq9EoN4PL4Ezmi0ZMBut6lV3BXb29o9i7xeLzn4/38XBYOEhGFkZHBxc3R3jo+QkZERADs=')
        self.icon_case = tk.PhotoImage(data='R0lGODlhGQAeAKIAAE1qf6CxvNnh5iiX2Ha85mqGlv///wAAACwAAAAAGQAeAAADcmi63P4wykmrdSGH20IBQLFxhgco4XgF5wKokFfMdG3PsFEQfO//vUJjByz6hAyi0YhcKJfApuIZpBWluoF2OwAIBADuFvsBmUGZ85l8+6Tb7DYIHqfDh3Y6Pt/e820NIX81LQssaoiIOSSMjY6PkJEPCQA7')
        self.icon_chart = tk.PhotoImage(data='R0lGODlhGQAeALMAAAV3zE1qf73J0Ueh26CxvGy45GqGlrDZ8dng5P///wAAAAAAAAAAAAAAAAAAAAAAACwAAAAAGQAeAAAEZDDJSau9OOvNu/9giCRjSZ6mGa7c0U7C5W5zElcFMNASERg4ncWU2/mARGGmmDgGd0uh08m0zJjTn6RWuSpvzgR3wqyCtdEd0+RUUarjJhoDv9zSW/uLRYmLUIApgHyEhYaHIREAOw==')
        self.icon_clock = tk.PhotoImage(data='R0lGODlhGQAeALMAAAB7zpeptMnR1jSc2nS856fV8Imcp7bCyeHn6qKzu////wAAAAAAAAAAAAAAAAAAACwAAAAAGQAeAAAEk1DJSau9OOvNu/+ecIyk8AlBqq7mhhqBgBQF8sbaKyMIAPA2WMuiA/Z+QIHwcogZj0/UgRgwPKHPJSXhfPquqESFe8U+A2JKquwjXFMVWJngG9SA1XigPBsABkZ5FAYGO1cFBHdBBhUHcnxnBlN6hpAvTEKQNlWTFo5dYJwan6CbohuOhKqrnRwjKyMgsrO0tba3EQA7')
        self.icon_code = tk.PhotoImage(data='R0lGODlhFgAeAKIAAE1qf+Dm6qCxvCiX2Ha85mqGlrLX7f///ywAAAAAFgAeAAADfHi63P4wykmrvVeUzbsXTUGMZGkWIWGY7Igy4tqe4WDfeP4uReD/wOBO0Qsaf8NDMVAA/AQBwDJZFDiRPgCUGfJZn0Wtj+q9MrdiLoyZjj6lal7Zu0yTA9/zz97FX5dRW3dseHtTfUdGSWaJQAANVgCSk5SUIBiYmZqbnAkAOw==')
        self.icon_orders = tk.PhotoImage(data='R0lGODlhGQAeAKIAAAF1y01qf6CxvCiX2Ha85mqGlv///wAAACwAAAAAGQAeAAADUGi63P4wykmrvTgXUdT4YCg2QiAoQKqurNMpRCzPdGbfymuIfEiaKJZQ1di8aMgZbnnR9Z6/k2FILXJgySRzKzF6nrxokNoqLrJarnrNbi8TADs=')
        self.icon_settings = tk.PhotoImage(data='R0lGODlhGQAeALMAAPX2+PL09vj5+unt8FJxh8rT2dfe4+7x83W65GaXtmqGlqGyvLvIz+Dm6fv8/P///ywAAAAAGQAeAAAEqfDJSau9OOvNu6/CoiiL81HiSJ5TOi6spKrN5iz4UihE7yuMQe5QcfF6CQQi8VPBKDNeUkllRiszwpRaJcwqjFFPyfRNey/LTqv0Fh48sjezIFAJgIm9/bzU7wMSAHsIBH0UDgFSbQQHa3JAAhUGYntlSIxpUCpsXF1fm5xbn6AtWZhLTZoTDgkjAAU+skBhCgkBGwdRCg+SJ0aHH8AxEikLgcTJysvMExEAOw==')
        self.icon_statistic = tk.PhotoImage(data='R0lGODlhGQAeALMAADxdc1VxhZSms1yv4aCxvNzk6SiX2HW85nSNnPX6/eLn6v///wAAAAAAAAAAAAAAACwAAAAAGQAeAAAEg3DJSau9OOvNu/9gmAmCNxxoqq6pUQ1wLM+ySw1Gru/8XhGKoHBIFBJ+xSTxSAEKEQHEECFYIoUBRTaIAEiHzImTG+V6i2HJmNj9WpvFQluZXqzNX6hbUb+3C0FZW0F9RAJ7emBXSnSLjGg/BJKTlJWUGVQYhxgJFAganyKio6SlphcRADs=')
        self.icon_terminal = tk.PhotoImage(data='R0lGODlhGQAeALMAAAF1y+Hm6k1qf3S75p+wu9vt+CiX2HzA55zQ7WqGlsXQ1ur1+/T6/fH09fz9/f///ywAAAAAGQAeAAAEefDJSau9OOvNu/9gKG7OSDlDeRFJsiEGgrFuxhg4s7YajMsTWmtIsCxwyMUkMGwGLAck7kARtoqVghRZmDSaiYZlsMUNKIqhQkM2XBxDFaaNSa/ZuMzdxAeVkRJgTRUAhYaGEgKKi4sVA4+QkBIElJWVfZiZmpucFREAOw==')
        self.icon_trades = tk.PhotoImage(data='R0lGODlhGQAeAKIAAAF1y01qf6CxvCiX2Ha85mqGlv///wAAACwAAAAAGQAeAAADUGi63P4wykmrvTiDrYr/YNgQAKEEaKquzrAIcCzPWW0bG9CF/DeWp5Uw1XrNjrGb0pLb9Xg/k2FILSqQ2KVW0jQ8e9EgldVwXbHHrXrNbi8TADs=')
        self.icon_info = tk.PhotoImage(data='R0lGODlhGwAeAKIAAAB7zlOn3oacqqCxvGqGluHn6v///////yH/C05FVFNDQVBFMi4wAwEAAAAh+QQFAAAHACwAAAAAGwAeAAADeWi63P4wykmrvVgOwvvIXShanDAUaDoIHFWmcMoS0gsHQTxHhBAXuB8LsjnFAIBf8cH5OVMtR/PpjDamseDPysDeclualODUxrgLb8oMQyuKPzZqyfRlwbAhxJZC6txdPVQFOxMlRjArgEwijRkbIh8Zk5SVlpeYCgkAOw==')
        self.icon_play = tk.PhotoImage(data='R0lGODlhCwALAJEAACiX2Ha85v///wAAACH/C05FVFNDQVBFMi4wAwEAAAAh+QQEAAAAACwAAAAACwALAAACE5SPqQh7AIKDUCZKL7UsTgeGRgEAOw==')
        self.icon_stop = tk.PhotoImage(data='R0lGODlhCwALAIAAAKCxvP///yH/C05FVFNDQVBFMi4wAwEAAAAh+QQEAAAAACwAAAAACwALAAACEYyPqQftgJ6LErJKZX57rv8VADs=')

        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.tool_bar = tk.Frame(bg='#ffffff', bd=0, width=400, height=160)
        self.tool_bar.pack(side=tk.TOP, fill=tk.BOTH)
        y = 10
        tk.Label(self.tool_bar, bg='#ffffff', text='Share').place(x=10, y=y)
        self.entry_share = ttk.Entry(self.tool_bar)
        self.entry_share.place(x=80, y=y, width=120, height=25)

        ttk.Button(self.tool_bar, text='Init', command=self.access).place(x=220, y=y, width=120, height=25)
        y = 30
        tk.Label(self.tool_bar, bg='#ffffff', text='').place(x=10, y=y)

        y = 40
        self.failed_activation = tk.Label(self.tool_bar, bg='#ffffff', text='', fg='#dd3333', font='Arial 10')
        self.failed_activation.place(x=80, y=y)

        try:
            self.entry_share.insert(0, self.app.db.load_key())
        except:
            pass

    def access(self):
        self.app.user.shared_key = self.entry_share.get()
        if self.app.user.shared_key != 'demo':
            self.app.user.activation.get_file_data(self.app.user.shared_key)
        if self.app.user.activation.check():
            self.init_main_window()
            self.app.common.launch()
            self.app.db.save_key(self.app.user.shared_key)
        else:
            self.failed_activation.config(text='Activation failed')

    def log(self, s):
        # OK
        t = strftime("%m/%d %H:%M", localtime(time()))
        self.logs_box.configure(state='normal')
        self.logs_box.insert(tk.END, t + ' ' + s + '\n')
        self.logs_box.configure(state='disabled')

        self.logs_box.yview_moveto(1)

    def reset_log(self):
        # OK
        self.logs_box.configure(state='normal')
        self.logs_box.delete(1.0, tk.END)
        self.logs_box.configure(state='disabled')
        return 0

    @staticmethod
    def progress(progress_bar):
        if progress_bar.cget('fg') == '#3399dd':
            progress_bar.configure(fg='#dddddd')
        else:
            progress_bar.configure(fg='#3399dd')

    def init_main_window(self):
        self.tool_bar.forget()

        menu_bar = tk.Frame(bg='#ffffff', bd=0, width=400, height=30)
        menu_bar.pack(side=tk.TOP, fill=tk.BOTH)

        tool_bar = tk.Frame(bg='#ffffff', bd=0, width=400, height=20)
        tool_bar.pack(side=tk.TOP, fill=tk.BOTH)

        log_bar = tk.Frame(bg='#ffffff', bd=0, width=400, height=70)
        log_bar.pack(side=tk.TOP, fill=tk.BOTH)

        button_bar = tk.Frame(bg='#ffffff', bd=0, width=400, height=60)
        button_bar.pack(side=tk.TOP, fill=tk.BOTH)

        # menu bar
        tk.Button(menu_bar, command=self.__check_for_depth_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_book).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_orders_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_orders).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_trades_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_trades).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_terminal_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_terminal).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_chart_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_chart).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_position_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_case).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_clocks_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_clock).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_statistic_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_statistic).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_alarm_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_alarm).pack(side=tk.LEFT)

        tk.Button(menu_bar, command=self.__check_for_settings_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_settings).pack(side=tk.LEFT)
        if self.app.debug:
            tk.Button(menu_bar, command=self.__check_for_debug_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_code).pack(side=tk.LEFT)
        tk.Button(menu_bar, command=self.__check_for_info_window, bg='#ffffff', bd=0, compound=tk.TOP, image=self.icon_info).pack(side=tk.LEFT)

        # toolbar
        self.progress_depth = tk.Label(tool_bar, bg='#ffffff', text='D', fg='#3399dd', font='Arial 6')  # □■
        self.progress_depth.place(x=370, y=0)

        self.progress_price = tk.Label(tool_bar, bg='#ffffff', text='P', fg='#3399dd', font='Arial 6')  # □■
        self.progress_price.place(x=360, y=0)

        self.progress_orders = tk.Label(tool_bar, bg='#ffffff', text='O', fg='#3399dd', font='Arial 6')  # □■
        self.progress_orders.place(x=350, y=0)

        self.progress_trades = tk.Label(tool_bar, bg='#ffffff', text='T', fg='#3399dd', font='Arial 6')  # □■
        self.progress_trades.place(x=340, y=0)

        self.progress_balances = tk.Label(tool_bar, bg='#ffffff', text='B', fg='#3399dd', font='Arial 6')  # □■
        self.progress_balances.place(x=330, y=0)

        self.progress_main = tk.Label(tool_bar, bg='#ffffff', text='M', fg='#dddddd', font='Arial 6')  # □■
        self.progress_main.place(x=320, y=0)

        self.indicator_run = tk.Label(tool_bar, image=self.icon_stop, bd=0)
        self.indicator_run.place(x=308, y=2)

        tk.Label(tool_bar, bg='#ffffff', text='LOGS:', font='Arial 10 bold').place(x=10, y=0)

        # log bar
        self.logs_box = tk.Text(log_bar, font='Arial 10', wrap=tk.WORD, state='disabled')
        logs_scrollbar = ttk.Scrollbar(log_bar, orient='vertical', command=self.logs_box.yview, )

        self.logs_box.config(yscrollcommand=logs_scrollbar.set)

        logs_scrollbar.place(x=380, y=0, width=15, height=70)
        self.logs_box.place(x=5, y=0, width=375, height=70)

        # button bar
        ttk.Button(button_bar, text='Clear Logs', command=self.reset_log).place(x=10, y=5, width=120, height=23)
        ttk.Button(button_bar, text='Start', command=self.app.common.start_bot).place(x=140, y=5, width=120, height=23)
        ttk.Button(button_bar, text='Stop', command=self.app.common.stop_bot).place(x=270, y=5, width=120, height=23)

        self.progress(self.progress_main)

    def __check_for_depth_window(self):
        try:
            self.app.gui.win_depth.focus()
        except:
            self.app.gui.win_depth = DepthWindow(True, self.root, self.app)

    def __check_for_orders_window(self):
        try:
            self.app.gui.win_orders.focus()
        except:
            self.app.gui.win_orders = OrdersWindow(True, self.root, self.app)

    def __check_for_trades_window(self):
        try:
            self.app.gui.win_trades.focus()
        except:
            self.app.gui.win_trades = TradesWindow(True, self.root, self.app)

    def __check_for_clocks_window(self):
        try:
            self.app.gui.win_clocks.focus()
        except:
            self.app.gui.win_clocks = ClocksWindow(True, self.root, self.app)

    def __check_for_terminal_window(self):
        try:
            self.app.gui.win_terminal.focus()
        except:
            self.app.gui.win_terminal = TerminalWindow(True, self.root, self.app)

    def __check_for_settings_window(self):
        try:
            self.app.gui.win_settings.focus()
        except:
            self.app.gui.win_settings = SettingsWindow(True, self.root, self.app)
        if self.app.user.bot_is_init:
            self.app.gui.win_settings.view_settings()

    def __check_for_chart_window(self):
        try:
            self.app.gui.win_chart.focus()
        except:
            self.app.gui.win_chart = ChartWindow(True, self.root, self.app)

    def __check_for_alarm_window(self):
        try:
            self.app.gui.win_alarm.focus()
        except:
            self.app.gui.win_alarm = AlarmWindow(True, self.root, self.app)
        if self.app.user.bot_is_init:
            self.app.gui.win_alarm.view_alarm()

    def __check_for_position_window(self):
        try:
            self.app.gui.win_position.focus()
        except:
            self.app.gui.win_position = PositionWindow(True, self.root, self.app)

    def __check_for_statistic_window(self):
        try:
            self.app.gui.win_statistic.focus()
        except:
            self.app.gui.win_statistic = StatisticWindow(True, self.root, self.app)

    def __check_for_info_window(self):
        try:
            self.app.gui.win_info.focus()
        except:
            self.app.gui.win_info = InfoWindow(True, self.root, self.app)

    def __check_for_debug_window(self):
        try:
            self.app.gui.win_debug.focus()
        except:
            self.app.gui.win_debug = DebugWindow(True, self.root, self.app)


class DepthWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.title('Openbook window')
        self.geometry('300x165'+self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=35)
        tool_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(tool_bar, text='Bid', bg='#ffffff', font='Arial 10 bold').place(x=10, y=10)
        tk.Label(tool_bar, text='Ask', bg='#ffffff', font='Arial 10 bold').place(x=160, y=10)

        self.tree = ttk.Treeview(self)
        self.tree['columns'] = ('bid_price', 'bid_qty', 'bid_sum', 'ask_price', 'ask_qty', 'ask_sum',)
        self.tree.column('#0', width=0, minwidth=0, stretch=tk.NO)
        self.tree.column('bid_price', width=50, minwidth=50, stretch=tk.NO)
        self.tree.column('bid_qty', width=50, minwidth=50, stretch=tk.NO)
        self.tree.column('bid_sum', width=50, minwidth=50, stretch=tk.NO)
        self.tree.column('ask_price', width=50, minwidth=50, stretch=tk.NO)
        self.tree.column('ask_qty', width=50, minwidth=50, stretch=tk.NO)
        self.tree.column('ask_sum', width=50, minwidth=50, stretch=tk.NO)

        self.tree.heading('bid_price', text='Price', anchor=tk.W)
        self.tree.heading('bid_qty', text='Qty', anchor=tk.W)
        self.tree.heading('bid_sum', text='Sum', anchor=tk.W)
        self.tree.heading('ask_price', text='Price', anchor=tk.W)
        self.tree.heading('ask_qty', text='Qty', anchor=tk.W)
        self.tree.heading('ask_sum', text='Sum', anchor=tk.W)

        for i in range(5):
            if len(self.app.user.depth['bids']) > i and len(self.app.user.depth['asks']) > i:
                self.tree.insert('', 'end', 'depth_'+str(i), values=(
                    0.0 if not self.app.user.depth['bids'][i][0] else self.app.gui.fp(self.app.user.depth['bids'][i][0]),
                    0.0 if not self.app.user.depth['bids'][i][1] else self.app.gui.fq(self.app.user.depth['bids'][i][1]),
                    0.0 if not self.app.user.depth['bids'][i][0] else self.app.gui.fp(self.app.user.depth['bids'][i][0] * self.app.user.depth['bids'][i][1]),
                    0.0 if not self.app.user.depth['asks'][i][0] else self.app.gui.fp(self.app.user.depth['asks'][i][0]),
                    0.0 if not self.app.user.depth['asks'][i][1] else self.app.gui.fq(self.app.user.depth['asks'][i][1]),
                    0.0 if not self.app.user.depth['asks'][i][0] else self.app.gui.fp(self.app.user.depth['asks'][i][0] * self.app.user.depth['asks'][i][1]),
                ))
            else:
                self.tree.insert('', 'end', 'depth_' + str(i), values=(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))

        self.tree.pack(fill=tk.X)

    def view_depth(self):

        if self.app.user.depth != dict():
            bids_num = len(self.app.user.depth['bids'])
            asks_num = len(self.app.user.depth['asks'])

            if bids_num > 5:
                bids_num = 5
            if asks_num > 5:
                asks_num = 5
            try:
                for i in range(asks_num):
                    self.tree.set(item='depth_' + str(i), column='ask_price', value=self.app.gui.fp(self.app.user.depth['asks'][i][0]))
                    self.tree.set(item='depth_' + str(i), column='ask_qty', value=self.app.gui.fq(self.app.user.depth['asks'][i][1]))
                    self.tree.set(item='depth_' + str(i), column='ask_sum', value=self.app.gui.fp(self.app.user.depth['asks'][i][0] * self.app.user.depth['asks'][i][1]))

                for i in range(bids_num):
                    self.tree.set(item='depth_' + str(i), column='bid_price', value=self.app.gui.fp(self.app.user.depth['bids'][i][0]))
                    self.tree.set(item='depth_' + str(i), column='bid_qty', value=self.app.gui.fq(self.app.user.depth['bids'][i][1]))
                    self.tree.set(item='depth_' + str(i), column='bid_sum', value=self.app.gui.fp(self.app.user.depth['bids'][i][0] * self.app.user.depth['bids'][i][1]))
            except Exception as e:
                self.app.errors.error(129, e)


class OrdersWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        self.tree = None
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.title('Orders window')
        self.geometry('300x260' + self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=33)
        tool_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(tool_bar, text='Orders', bg='#ffffff', font='Arial 10 bold').place(x=10, y=10)

        treebar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=260)
        treebar.pack(side=tk.LEFT, fill=tk.BOTH)

        self.tree = ttk.Treeview(treebar)

        ttk.Button(tool_bar, text='Cancel', command=self.init_cancel).place(x=220, y=10, width=70, height=23)

        self.tree['columns'] = ('side', 'price', 'filled', 'amount', 'sum')
        self.tree.column('#0', width=0, minwidth=0, stretch=tk.NO)
        self.tree.column('side', width=60, minwidth=50)
        self.tree.column('price', width=60, minwidth=50, stretch=tk.NO)
        self.tree.column('filled', width=60, minwidth=50, stretch=tk.NO)
        self.tree.column('amount', width=60, minwidth=50, stretch=tk.NO)
        self.tree.column('sum', width=60, minwidth=50, stretch=tk.NO)

        self.tree.heading('side', text='Side', anchor=tk.W)
        self.tree.heading('price', text='Price', anchor=tk.W)
        self.tree.heading('filled', text='Filled', anchor=tk.W)
        self.tree.heading('amount', text='Amount', anchor=tk.W)
        self.tree.heading('sum', text='Sum', anchor=tk.W)

        for i in range(len(self.app.user.orders)):
            self.tree.insert('', 'end', self.app.user.orders[i]['id'], text=self.app.user.orders[i]['id'],
                             values=(self.app.user.orders[i]['side'],
                                     self.app.gui.fp(self.app.user.orders[i]['price']),
                                     self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['filled'])),
                                     self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['filled']) + (
                                         lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['remaining'])),
                                     round(self.app.user.orders[i]['price'] * (lambda x: 0.0 if x is None else x)(
                                         self.app.user.orders[i]['amount']), 8)))
        self.tree.pack(fill=tk.BOTH)

    def init_cancel(self):
        res = self.app.common.cancel_order(order_id=self.tree.item(self.tree.focus())['text'])

    def view_orders(self):
        self.tree.delete(*self.tree.get_children())

        # for i in app_o.tree.get_children():
        #     app_o.tree.delete(i)
        try:
            for i in range(len(self.app.user.orders)):
                self.tree.insert('', 'end', self.app.user.orders[i]['id'], text=self.app.user.orders[i]['id'],
                              values=(self.app.user.orders[i]['side'],
                                      self.app.gui.fp(self.app.user.orders[i]['price']),
                                      self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['filled'])),
                                      self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['filled']) + (lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['remaining'])),
                                      self.app.gui.fp(self.app.user.orders[i]['price'] * (lambda x: 0.0 if x is None else x)(self.app.user.orders[i]['amount']))))
        except Exception as e:
            self.app.errors.error(133, e)


class TradesWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        self.tree = None
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.title('Trades window')
        self.geometry('300x260'+self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=33)
        tool_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(tool_bar, text='Trades', bg='#ffffff', font='Arial 10 bold').place(x=10, y=10)

        treebar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=260)
        treebar.pack(side=tk.LEFT, fill=tk.BOTH)

        self.tree = ttk.Treeview(treebar)

        self.tree['columns'] = ('time', 'side', 'price', 'amount', 'sum')
        self.tree.column('#0', width=0, minwidth=0, stretch=tk.NO)
        self.tree.column('time', width=68, minwidth=50, stretch=tk.NO)
        self.tree.column('side', width=40, minwidth=40, stretch=tk.NO)
        self.tree.column('price', width=64, minwidth=50, stretch=tk.NO)
        self.tree.column('amount', width=64, minwidth=50, stretch=tk.NO)
        self.tree.column('sum', width=64, minwidth=50, stretch=tk.NO)

        self.tree.heading('time', text='Time', anchor=tk.W)
        self.tree.heading('side', text='Side', anchor=tk.W)
        self.tree.heading('price', text='Price', anchor=tk.W)
        self.tree.heading('amount', text='Amount', anchor=tk.W)
        self.tree.heading('sum', text='Sum', anchor=tk.W)

        for i in range(len(self.app.user.trades)):
            self.tree.insert('', 'end', 'trades_' + str(i),
                             values=(strftime('%m/%d %H:%M', localtime(self.app.user.trades[i]['timestamp']/1000)),
                                     self.app.user.trades[i]['side'],
                                     self.app.gui.fp(self.app.user.trades[i]['price']),
                                     self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.trades[i]['amount'])),
                                     self.app.gui.fp((lambda x: 0.0 if x is None else x)(self.app.user.trades[i]['cost']))))
        self.tree.pack(fill=tk.BOTH)

    def view_trades(self):
        self.tree.delete(*self.tree.get_children())

        # for i in app_t.tree.get_children():
        #     app_t.tree.delete(i)

        try:
            for i in range(len(self.app.user.trades)):
                self.tree.insert('', 'end', 'trades_' + str(i),
                                  values=(strftime('%m/%d %H:%M', localtime(self.app.user.trades[i]['timestamp'] / 1000)),
                                          self.app.user.trades[i]['side'],
                                          self.app.gui.fp(self.app.user.trades[i]['price']),
                                          self.app.gui.fq((lambda x: 0.0 if x is None else x)(self.app.user.trades[i]['amount'])),
                                          self.app.gui.fp((lambda x: 0.0 if x is None else x)(self.app.user.trades[i]['cost'])))
                                  )
        except Exception as e:
            self.app.errors.error(136, e)


class ClocksWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        self.day = self.hms = None
        if apply:
            self.init_window()
        else:
            self.destroy()

        Thread(target=self.update_time, daemon=True).start()

    def init_window(self):
        self.title('Clock')
        self.geometry('192x108'+self.app.gui.rand_xy())
        self.resizable(False, False)

        outer_frame = tk.Frame(self, bd=0, bg='#ffffff', width=192, height=108)
        outer_frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        bar = outer_frame

        self.day = tk.Label(bar, bg='#ffffff', text='01/01/01', font='Arial 24 bold')
        self.day.place(x=12, y=16)
        self.hms = tk.Label(bar, bg='#ffffff', text='00:00:00', font='Arial 24 bold')
        self.hms.place(x=12, y=52)

    def update_time(self):
        while True:
            try:
                if self.winfo_exists():
                    self.day.configure(text=strftime("%Y/%m/%d"))
                    self.hms.configure(text=strftime("%H:%M:%S.") + str(time()).split('.')[1][0:2])
                sleep(0.05)
            except Exception as e:
                self.app.errors.error(151, e)


class TerminalWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.title('Terminal')
        self.geometry('300x200'+self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bd=0, bg='#ffffff', width=300, height=200)
        tool_bar.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        y = 10
        tk.Label(tool_bar, bg='#ffffff', text='FUNDS:', font='Arial 10 bold').place(x=10, y=y)

        y += 25
        self.quote_asset = tk.Label(tool_bar, bg='#ffffff', text='Quote')
        self.quote_asset.place(x=10, y=y)
        self.base_asset = tk.Label(tool_bar, bg='#ffffff', text='Base')
        self.base_asset.place(x=150, y=y)
        self.entry_quote = ttk.Entry(tool_bar)
        self.entry_quote.place(x=60, y=y, width=80)
        self.entry_base = ttk.Entry(tool_bar)
        self.entry_base.place(x=200, y=y, width=80)

        y += 25
        tk.Label(tool_bar, bg='#ffffff', text='BUY').place(x=10, y=y)
        self.label_buy_num_step = tk.Label(tool_bar, bg='#ffffff', text='Step')
        self.label_buy_num_step.place(x=60, y=y)
        tk.Label(tool_bar, bg='#ffffff', text='SELL').place(x=150, y=y)
        self.label_sell_num_step = tk.Label(tool_bar, bg='#ffffff', text='Step')
        self.label_sell_num_step.place(x=200, y=y)

        y += 25
        self.label_buy_price = tk.Label(tool_bar, bg='#ffffff', text='Price')
        self.label_buy_price.place(x=10, y=y)
        self.label_sell_price = tk.Label(tool_bar, bg='#ffffff', text='Price')
        self.label_sell_price.place(x=150, y=y)
        self.entry_buy_price = ttk.Entry(tool_bar)
        self.entry_buy_price.insert(0, '0')
        self.entry_buy_price.place(x=60, y=y, width=80)
        self.entry_sell_price = ttk.Entry(tool_bar)
        self.entry_sell_price.insert(0, '0')
        self.entry_sell_price.place(x=200, y=y, width=80)

        y += 25
        self.label_buy_qty = tk.Label(tool_bar, bg='#ffffff', text='Qty')
        self.label_buy_qty.place(x=10, y=y)
        self.label_sell_qty = tk.Label(tool_bar, bg='#ffffff', text='Qty')
        self.label_sell_qty.place(x=150, y=y)
        self.entry_buy_qty = ttk.Entry(tool_bar)
        self.entry_buy_qty.insert(0, '0')
        self.entry_buy_qty.place(x=60, y=y, width=80)
        self.entry_sell_qty = ttk.Entry(tool_bar)
        self.entry_sell_qty.insert(0, '0')
        self.entry_sell_qty.place(x=200, y=y, width=80)

        y += 25
        s = ttk.Style()
        s.configure('Horizontal.TScale', background='#ffffff')
        self.buy_scale_qty = tk.IntVar()
        self.sell_scale_qty = tk.IntVar()
        self.label_scale_buy = tk.Label(tool_bar, bg='#ffffff', text=0, textvariable=self.buy_scale_qty)
        self.label_scale_buy.place(x=10, y=y)
        self.label_scale_sell = tk.Label(tool_bar, bg='#ffffff', text=0, textvariable=self.sell_scale_qty)
        self.label_scale_sell.place(x=150, y=y)
        scale_buy = ttk.Scale(tool_bar, style='Horizontal.TScale', from_=0, to=100, command=self.on_buy_scale)
        scale_buy.place(x=60, y=y, width=80)
        scale_sell = ttk.Scale(tool_bar, style='Horizontal.TScale', from_=0, to=100, command=self.on_sell_scale)
        scale_sell.place(x=200, y=y, width=80)

        y += 30
        btn_buy = ttk.Button(tool_bar, text='BUY', command=self.app.common.hand_buy)
        btn_buy.place(x=10, y=y, width=130, height=25)
        btn_sell = ttk.Button(tool_bar, text='SELL', command=self.app.common.hand_sell)
        btn_sell.place(x=150, y=y, width=130, height=25)

    def on_buy_scale(self, val):
        v = int(float(val))
        self.buy_scale_qty.set(str(v) + '%')
        try:
            price = float(self.entry_buy_price.get())
            if price != '':
                qty = (float(self.entry_quote.get()) / price) * (v/100)

                around_qty = self.app.user.rules[self.app.bot.pair]['aroundQty']

                if round(qty, around_qty) * price > self.app.user.balances[self.app.user.curr_quote.upper()]['free']:
                    while round(qty, around_qty) * price > self.app.user.balances[self.app.user.curr_quote.upper()]['free']:
                        qty -= 0.1 ** around_qty

                self.entry_buy_qty.delete(0, tk.END)
                self.entry_buy_qty.insert(0, self.app.gui.fq(qty))
        except Exception as e:
            self.app.errors.error(121, e)
        return 0

    def on_sell_scale(self, val):
        v = int(float(val))
        self.sell_scale_qty.set(str(v) + '%')
        try:
            qty = float(self.entry_base.get()) * (v/100)

            around_qty = self.app.user.rules[self.app.bot.pair]['aroundQty']

            if round(qty, around_qty) > self.app.user.balances[self.app.user.curr_base.upper()]['free']:
                while round(qty, around_qty) > self.app.user.balances[self.app.user.curr_base.upper()]['free']:
                    qty -= 0.1 ** around_qty

            self.entry_sell_qty.delete(0, tk.END)
            self.entry_sell_qty.insert(0, self.app.gui.fq(qty))
        except Exception as e:
            self.app.errors.error(122, e)
        return 0

    def view_terminal(self):  # OK
        if self.app.user.balances:
            try:
                self.quote_asset.configure(text=self.app.user.curr_quote.upper())
                self.base_asset.configure(text=self.app.user.curr_base.upper())

                format_qty = '{:.8f}'

                quote_qty = str(format_qty.format(self.app.user.balances[self.app.user.curr_quote.upper()]['free']))
                base_qty = str(format_qty.format(self.app.user.balances[self.app.user.curr_base.upper()]['free']))

                self.entry_quote.delete(0, tk.END)
                self.entry_base.delete(0, tk.END)
                self.entry_quote.insert(0, quote_qty)
                self.entry_base.insert(0, base_qty)

                self.label_buy_num_step.configure(text=str(self.app.strategy.last_buy_step))
                self.label_sell_num_step.configure(text=str(self.app.strategy.last_sell_step))
            except Exception as e:
                self.app.errors.error(138, e)

        if self.app.user.bot_is_run:
            try:
                self.entry_buy_price.delete(0, tk.END)
                self.entry_buy_qty.delete(0, tk.END)
                self.entry_sell_price.delete(0, tk.END)
                self.entry_sell_qty.delete(0, tk.END)
                self.entry_buy_price.insert(0, self.app.gui.fp(self.app.user.buy_price))
                self.entry_buy_qty.insert(0, self.app.gui.fq(self.app.user.buy_qty))
                self.entry_sell_price.insert(0, self.app.gui.fp(self.app.user.sell_price))
                self.entry_sell_qty.insert(0, self.app.gui.fq(self.app.user.sell_qty))
                self.label_buy_num_step.configure(text=self.app.strategy.last_buy_step)
                self.label_sell_num_step.configure(text=self.app.strategy.last_sell_step)
            except Exception as e:
                self.app.errors.error(139, e)

    def hand_buy(self):
        order_price = float(self.entry_buy_price.get())
        order_qty = float(self.entry_buy_qty.get())
        if self.app.common.control_trade(order_price, order_qty):
            self.app.common.send_order('buy', order_price, order_qty)  ######### BUY

    def hand_sell(self):
        order_price = float(self.entry_sell_price.get())
        order_qty = float(self.entry_sell_qty.get())
        if self.app.common.control_trade(order_price, order_qty):
            self.app.common.send_order('sell', order_price, order_qty)  ######## SELL


class SettingsWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):

        self.title('Settings window')
        self.geometry('300x400'+self.app.gui.rand_xy())
        self.resizable(False, False)

        full_height = 685 if (self.app.user.activation.check() and not self.app.user.demo_mode) else (685 - 120)

        # Создаю внешний фрейм
        outer_frame = tk.Frame(self, bd=0, width=300, height=400)
        outer_frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        # Создаю холст во внешнем фрейме
        self.canv = tk.Canvas(outer_frame, bd=0)
        self.canv.config(width=300, height=400)
        self.canv.config(scrollregion=(0, 2, 300, full_height))

        # Создаю скроллбар
        sbar = ttk.Scrollbar(outer_frame, orient='vertical', command=self.canv.yview, )
        self.canv.config(yscrollcommand=sbar.set)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canv.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        # Создаю внутренний фрейм
        inner_frame = tk.Frame(self.canv, bd=0, bg='#ffffff', width=300, height=full_height + 5)
        self.canv.create_window((0, 0), window=inner_frame, anchor=tk.NW)

        bar = inner_frame

        y = 10
        tk.Label(bar, bg='#ffffff', text='API Keys Settings', font='Arial 10 bold').place(x=10, y=y)

        y += 25
        tk.Label(bar, bg='#ffffff', text='API Key').place(x=10, y=y)
        self.entry_key = ttk.Entry(bar)
        self.entry_key.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='API Secret').place(x=10, y=y)
        self.entry_secret = ttk.Entry(bar)
        self.entry_secret.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Opt key').place(x=10, y=y)
        self.entry_optkey = ttk.Entry(bar)
        self.entry_optkey.place(x=100, y=y, width=170)

        if self.app.user.activation.check() and not self.app.user.demo_mode:
            y += 35
            tk.Label(bar, bg='#ffffff', text='Set number').place(x=10, y=y)
            self.entry_set = ttk.Combobox(bar, values=self.app.user.settings_list)
            self.entry_set.place(x=100, y=y, width=170)

            y += 25
            ttk.Button(bar, text='Save', command=self.app.common.save_set).place(x=10, y=y, width=80, height=23)
            ttk.Button(bar, text='Load', command=self.app.common.load_set).place(x=100, y=y, width=80, height=23)
            ttk.Button(bar, text='Delete', command=self.app.common.delete_set).place(x=190, y=y, width=80, height=23)

            y += 35
            tk.Label(bar, bg='#ffffff', text='Set 64string').place(x=10, y=y)
            self.entry_64string = ttk.Entry(bar)
            self.entry_64string.place(x=100, y=y, width=170)

            y += 25
            ttk.Button(bar, text='Encode', command=self.encode_settings).place(x=10, y=y, width=125, height=23)
            ttk.Button(bar, text='Decode', command=self.decode_settings).place(x=145, y=y, width=125, height=23)

        y += 35
        tk.Label(bar, bg='#ffffff', text='General Settings', font='Arial 10 bold').place(x=10, y=y)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Exchange').place(x=10, y=y)
        self.entry_exchange = ttk.Combobox(bar, values=self.app.common.exchanges)
        self.entry_exchange.set(u'binance')
        self.entry_exchange.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Pair').place(x=10, y=y)
        self.entry_pair = ttk.Entry(bar)
        self.entry_pair.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Deposit').place(x=10, y=y)
        self.entry_depo = ttk.Entry(bar)
        self.entry_depo.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Order Life').place(x=10, y=y)
        self.entry_order_life = ttk.Entry(bar)
        self.entry_order_life.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Pause').place(x=10, y=y)
        self.entry_pause = ttk.Entry(bar)
        self.entry_pause.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Upd.time').place(x=10, y=y)
        self.entry_update_time = ttk.Entry(bar)
        self.entry_update_time.place(x=100, y=y, width=170)

        y += 35
        tk.Label(bar, bg='#ffffff', text='Buy Settings', font='Arial 10 bold').place(x=10, y=y)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Buy price').place(x=10, y=y)
        self.entry_buy_price = ttk.Entry(bar)
        self.entry_buy_price.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Buy qty').place(x=10, y=y)
        self.entry_buy_qty = ttk.Entry(bar)
        self.entry_buy_qty.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Buy type').place(x=10, y=y)
        self.entry_buy_type = ttk.Combobox(bar, values=[u'Base', u'Quote'])
        self.entry_buy_type.current(0)
        self.entry_buy_type.place(x=100, y=y, width=170)

        y += 35
        tk.Label(bar, bg='#ffffff', text='Sell Settings', font='Arial 10 bold').place(x=10, y=y)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Sell price').place(x=10, y=y)
        self.entry_sell_price = ttk.Entry(bar)
        self.entry_sell_price.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Sell qty').place(x=10, y=y)
        self.entry_sell_qty = ttk.Entry(bar)
        self.entry_sell_qty.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Sell type').place(x=10, y=y)
        self.entry_sell_type = ttk.Combobox(bar, values=[u'Base', u'Quote'])
        self.entry_sell_type.current(0)
        self.entry_sell_type.place(x=100, y=y, width=170)

        y += 35
        ttk.Button(bar, text='Apply', command=self.app.common.update_settings).place(x=10, y=y, width=125, height=23)
        ttk.Button(bar, text='Close', command=self.destroy).place(x=145, y=y, width=125, height=23)

        # Контроль колесика мыши
        # для Windows
        self.bind("<MouseWheel>", self.mouse_wheel)
        # для Linux
        self.bind("<Button-4>", self.mouse_wheel)
        self.bind("<Button-5>", self.mouse_wheel)

    def mouse_wheel(self, event):
        # воспроизведение события колесика мыши Linux or Windows
        if event.num == 5 or event.delta == -120:
            self.canv.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self.canv.yview_scroll(-1, "units")

    def get_set_data(self):
        data = dict()

        data['api_key'] = self.entry_key.get()
        data['api_secret'] = self.entry_secret.get()
        data['opt_key'] = self.entry_optkey.get()
        data['exchange'] = self.entry_exchange.get().lower()
        data['depo'] = float(self.entry_depo.get())
        data['pair'] = self.entry_pair.get().lower()
        data['order_life'] = float(self.entry_order_life.get())
        data['pause'] = float(self.entry_pause.get())
        data['upd_time'] = float(self.entry_update_time.get())
        data['buy_price'] = float(self.entry_buy_price.get())
        data['buy_qty'] = float(self.entry_buy_qty.get())
        data['buy_type'] = self.entry_buy_type.get().lower()
        data['sell_price'] = float(self.entry_sell_price.get())
        data['sell_qty'] = float(self.entry_sell_qty.get())
        data['sell_type'] = self.entry_sell_type.get().lower()
        if self.app.user.activation.check() and not self.app.user.demo_mode:
            data['num_set'] = self.entry_set.get()
        return data

    def encode_settings(self):
        data = self.get_set_data()
        json_string = json.dumps(data)

        data_string = b64encode(json_string.encode())

        self.entry_64string.delete(0, tk.END)
        self.entry_64string.insert(0, data_string.decode('utf-8'))

    def decode_settings(self):

        data_string = self.entry_64string.get()
        json_string = b64decode(data_string)

        data = json.loads(json_string)

        self.app.bot.upd(data)
        self.app.common.update_settings()
        self.view_settings()

    def view_settings(self):

        data = self.app.bot.get_set_data()

        self.entry_key.delete(0, tk.END)
        self.entry_secret.delete(0, tk.END)
        self.entry_optkey.delete(0, tk.END)
        self.entry_exchange.delete(0, tk.END)
        self.entry_pair.delete(0, tk.END)
        self.entry_order_life.delete(0, tk.END)
        self.entry_pause.delete(0, tk.END)
        self.entry_update_time.delete(0, tk.END)
        self.entry_buy_price.delete(0, tk.END)
        self.entry_sell_price.delete(0, tk.END)
        self.entry_buy_qty.delete(0, tk.END)
        self.entry_sell_qty.delete(0, tk.END)
        self.entry_buy_type.delete(0, tk.END)
        self.entry_sell_type.delete(0, tk.END)
        self.entry_depo.delete(0, tk.END)

        self.entry_key.insert(0, data['api_key'] if 'api_key' in data else '')
        self.entry_secret.insert(0, data['api_secret'] if 'api_secret' in data else '')
        self.entry_optkey.insert(0, data['opt_key'] if 'opt_key' in data else '')
        self.entry_exchange.insert(0, data['exchange'].capitalize() if 'exchange' in data else '')
        self.entry_depo.insert(0, data['depo'] if 'depo' in data else '0.0')
        self.entry_pair.insert(0, data['pair'] if 'pair' in data else '')
        self.entry_order_life.insert(0, data['order_life'] if 'order_life' in data else '0.0')
        self.entry_pause.insert(0, data['pause'] if 'pause' in data else '0.0')
        self.entry_update_time.insert(0, data['upd_time'] if 'upd_time' in data else '0.0')
        self.entry_buy_price.insert(0, data['buy_price'] if 'buy_price' in data else '0.0')
        self.entry_sell_price.insert(0, data['sell_price'] if 'sell_price' in data else '0.0')
        self.entry_buy_qty.insert(0, data['buy_qty'] if 'buy_qty' in data else '0.0')
        self.entry_sell_qty.insert(0, data['sell_qty'] if 'sell_qty' in data else '0.0')
        self.entry_buy_type.insert(0, data['buy_type'].capitalize() if 'buy_type' in data else 'Quote')
        self.entry_sell_type.insert(0, data['sell_type'].capitalize() if 'sell_type' in data else 'Quote')

        if self.app.user.activation.check():
            self.entry_set.delete(0, tk.END)
            self.entry_set.insert(0, data['num_set'] if 'num_set' in data else '')


class ChartWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window()
            self.draw()
        else:
            self.destroy()

    def init_window(self):
        self.title('Candlestick chart')
        self.geometry('400x300'+self.app.gui.rand_xy())
        self.resizable(False, False)
        self.bar = tk.Frame(self, bg='#ffffff', bd=0, width=400, height=300)
        self.bar.pack(side=tk.TOP, fill=tk.BOTH)
        self.canvas = tk.Canvas(self.bar, bg='#ffffff', bd=0, width=400, height=300)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.canvas.create_line(10, 10, 390, 10, fill="#dddddd")
        self.canvas.create_line(10, 66, 390, 66, fill="#dddddd")
        self.canvas.create_line(10, 122, 390, 122, fill="#dddddd")
        self.canvas.create_line(10, 178, 390, 178, fill="#dddddd")
        self.canvas.create_line(10, 234, 390, 234, fill="#dddddd")
        self.canvas.create_line(390, 10, 390, 290, fill="#dddddd")
        self.canvas.create_line(10, 290, 390, 290, fill="#dddddd")

    def draw(self):

        ohlc_raw = self.app.kline.kline_1m[-30:]
        ohlc = dict()
        ohlc['time'] = list()
        ohlc['open'] = list()
        ohlc['high'] = list()
        ohlc['low'] = list()
        ohlc['close'] = list()
        for i in range(len(ohlc_raw)):
            ohlc['time'].append(ohlc_raw[i].t)
            ohlc['open'].append(ohlc_raw[i].o)
            ohlc['high'].append(ohlc_raw[i].h)
            ohlc['low'].append(ohlc_raw[i].l)
            ohlc['close'].append(ohlc_raw[i].c)
        if ohlc == dict():
            ohlc['time'].append(0)
            ohlc['open'].append(0)
            ohlc['high'].append(0)
            ohlc['low'].append(0)
            ohlc['close'].append(0)
        min_prices = list()
        max_prices = list()

        if self.app.user.orders:
            for order in self.app.user.orders:
                if order['side'] == 'buy':
                    min_prices.append(order['price'])
                if order['side'] == 'sell':
                    max_prices.append(order['price'])
        if len(ohlc_raw) > 0:

            min_prices.append(min(ohlc['low']))
            max_prices.append(max(ohlc['high']))
            fig_low, fig_high, ystep, n = self.__look_ranges(min(min_prices), max(max_prices))
            xstep = 380 // len(ohlc['time'])
            bar_width = xstep / 2
            pp = (fig_high - fig_low) / 280

            self.canvas.delete('my_chart')

            for i in range(len(ohlc['time'])):
                x1 = x2 = 10 + i * xstep + xstep / 2
                y1 = self.__get_y(fig_high, ohlc['low'][i], pp)
                y2 = self.__get_y(fig_high, ohlc['high'][i], pp)
                self.canvas.create_line(x1, y1, x2, y2, fill="#cccccc", tags='my_chart')

                x1 = 10 + i * xstep + xstep / 2 - bar_width / 2
                x2 = 10 + i * xstep + xstep / 2 + bar_width / 2
                y1 = self.__get_y(fig_high, ohlc['open'][i], pp)
                y2 = self.__get_y(fig_high, ohlc['close'][i], pp)
                color = '#3399cc' if ohlc['close'][i] > ohlc['open'][i] else '#ff3300'
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#cccccc", fill=color, width=1, tags='my_chart')

            x = 390
            y = self.__get_y(fig_high, ohlc['close'][-1], pp)
            self.canvas.create_text(x, y-1, anchor=tk.E, font='Arial 8', text='Last ' + self.app.gui.fp(ohlc['close'][-1]) + '►', tags='my_chart')

            self.canvas.create_text(100, 20, anchor=tk.W, font='Arial 9', text=self.app.bot.pair.upper()+' 1m', tags='my_chart')
            self.canvas.create_text(20, 20, anchor=tk.W, font='Arial 9', text=str(fig_high), tags='my_chart')
            self.canvas.create_text(20, 280, anchor=tk.W, font='Arial 9', text=str(fig_low), tags='my_chart')
            self.canvas.create_text(20, 66, anchor=tk.W, font='Arial 9', text=str(round(fig_high - 2 * ystep, 9)), fill='#666666', tags='my_chart')
            self.canvas.create_text(20, 122, anchor=tk.W, font='Arial 9', text=str(round(fig_high - 4 * ystep, 9)), fill='#666666', tags='my_chart')
            self.canvas.create_text(20, 178, anchor=tk.W, font='Arial 9', text=str(round(fig_high - 6 * ystep, 9)), fill='#666666', tags='my_chart')
            self.canvas.create_text(20, 234, anchor=tk.W, font='Arial 9', text=str(round(fig_high - 8 * ystep, 9)), fill='#666666', tags='my_chart')

            for order in self.app.user.orders:
                y = self.__get_y(fig_high, order['price'], pp)
                if order['side'] == 'buy':
                    self.canvas.create_text(390, y-1, anchor=tk.E, font='Arial 9', text='Buy Order '+self.app.gui.fp(order['price'])+'▲ —', fill='#003366', tags='my_chart')
                elif order['side'] == 'sell':
                    self.canvas.create_text(390, y-1, anchor=tk.E, font='Arial 9', text='Sell Order '+self.app.gui.fp(order['price'])+'▼ —', fill='#663300', tags='my_chart')

            self.canvas.pack(fill=tk.BOTH, expand=1)

    @staticmethod
    def __look_ranges(m, M):
        s = (round(log10(M - m)) - 1) if M - m > 0 else 0
        l = m - m % 10 ** s
        h = M - M % 10 ** s + 10 ** s
        step = (h - l) / 10
        return round(l, 9), round(h, 9), step, s - 1

    @staticmethod
    def __get_y(fh, p, pp):
        return (fh - p) / pp + 10


class AlarmWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.__init_window()
        else:
            self.destroy()

    def __init_window(self):
        self.title('Alarm window')
        self.geometry('300x170'+self.app.gui.rand_xy())
        self.resizable(False, False)

        bar = tk.Frame(self, bg='#ffffff', bd=0, width=300, height=400)
        bar.pack(side=tk.TOP, fill=tk.BOTH)

        y = 10
        tk.Label(bar, bg='#ffffff', text='Alarm').place(x=10, y=y)
        self.entry_on = ttk.Combobox(bar, values=[u'On', u'Off'])
        self.entry_on.place(x=60, y=y, width=60)

        y -= 2
        self.val_buy = tk.BooleanVar()
        self.val_buy.set(False)
        self.cb_buy = tk.Checkbutton(bar, bg='#ffffff', text='Buys', variable=self.val_buy, onvalue=True, offvalue=False)
        self.cb_buy.place(x=125, y=y)

        self.val_sell = tk.BooleanVar()
        self.val_sell.set(False)
        self.cb_sell = tk.Checkbutton(bar, bg='#ffffff', text='Sells', variable=self.val_sell, onvalue=True, offvalue=False)
        self.cb_sell.place(x=175, y=y)

        self.val_stat = tk.BooleanVar()
        self.val_stat.set(False)
        self.cb_stat = tk.Checkbutton(bar, bg='#ffffff', text='Stat', variable=self.val_stat, onvalue=True, offvalue=False)
        self.cb_stat.place(x=225, y=y)

        y += 30
        tk.Label(bar, bg='#ffffff', text='Every time').place(x=10, y=y)
        self.entry_every = ttk.Combobox(bar, values=[u'Event', u'Period', u'Day'])
        self.entry_every.place(x=100, y=y, width=60)

        self.entry_h = ttk.Combobox(bar, values=[u'00', u'01', u'02', u'03', u'04', u'05', u'06', u'07', u'08', u'09',
                                                 u'10', u'11', u'12', u'13', u'14', u'15', u'16', u'17', u'18', u'19',
                                                 u'20', u'21', u'22', u'23'])
        self.entry_h.set(u'00')
        self.entry_h.place(x=180, y=y, width=40)
        self.entry_m = ttk.Combobox(bar, values=[u'00', u'05', u'10', u'15', u'20', u'25',
                                                 u'30', u'35', u'40', u'45', u'50', u'55',
                                                ])
        self.entry_m.set(u'00')
        self.entry_m.place(x=230, y=y, width=40)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Telegram token').place(x=10, y=y)
        self.entry_token = ttk.Entry(bar)
        self.entry_token.place(x=100, y=y, width=170)

        y += 25
        tk.Label(bar, bg='#ffffff', text='Chat ID').place(x=10, y=y)
        self.entry_chat_id = ttk.Entry(bar)
        self.entry_chat_id.place(x=100, y=y, width=170)

        y += 35
        ttk.Button(bar, text='Apply', command=self.save_alarm).place(x=10, y=y, width=125, height=23)
        ttk.Button(bar, text='Close', command=self.destroy).place(x=145, y=y, width=125, height=23)

    def view_alarm(self):
        data = self.app.alarm.get_set_data()

        self.entry_on.delete(0, tk.END)
        self.entry_every.delete(0, tk.END)
        self.entry_h.delete(0, tk.END)
        self.entry_m.delete(0, tk.END)
        self.entry_chat_id.delete(0, tk.END)
        self.entry_token.delete(0, tk.END)

        self.entry_on.insert(0, data['on'] if 'on' in data else 'Off')
        self.val_buy.set(data['buy'] if 'buy' in data else False)
        self.val_sell.set(data['sell'] if 'sell' in data else False)
        self.val_stat.set(data['stat'] if 'stat' in data else False)
        self.entry_every.insert(0, data['every'] if 'every' in data else '')
        self.entry_h.insert(0, data['h'] if 'h' in data else '00')
        self.entry_m.insert(0, data['m'] if 'm' in data else '00')
        self.entry_chat_id.insert(0, data['chat_id'] if 'chat_id' in data else '')
        self.entry_token.insert(0, data['token'] if 'token' in data else '')

    def save_alarm(self):

        data = dict()
        data['on'] = self.entry_on.get()

        data['buy'] = self.val_buy.get()
        data['sell'] = self.val_sell.get()
        data['stat'] = self.val_stat.get()
        data['every'] = self.entry_every.get()
        data['h'] = self.entry_h.get()
        data['m'] = self.entry_m.get()
        data['chat_id'] = self.entry_chat_id.get()
        data['token'] = self.entry_token.get()

        self.app.alarm.upd(data)
        try:
            self.app.db.save_alarm(self.app.bot.exchange, self.app.bot.pair, data)
        except Exception as e:
            self.app.errors.error(114, e)
        self.app.gui.log('Alarm saved')


class PositionWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.root = root
        self.app = app
        if apply:
            self.init_window()
        else:
            self.destroy()
        self.thread_started = 0
        if not self.thread_started:
            Thread(target=self.update_position, daemon=True).start()
            self.thread_started = 1

    def init_window(self):
        self.title('Position window')
        self.geometry('500x90'+self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bg='#ffffff', bd=0, width=500, height=40)
        tool_bar.pack(side=tk.TOP, fill=tk.X)

        tk.Label(tool_bar, text='Position', bg='#ffffff', font='Arial 10 bold').place(x=10, y=10)
        ttk.Button(tool_bar, text='Reset', command=self.reset_position).place(x=340, y=10, width=70, height=23)
        ttk.Button(tool_bar, text='Edit', command=self.__check_for_pos_edit_window).place(x=420, y=10, width=70, height=23)

        self.tree = ttk.Treeview(self)
        sbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sbar.set)

        self.tree['columns'] = ('exchange', 'pair', 'lprice', 'pprice', 'amount', 'sum', 'profit')
        self.tree.column('#0', width=30, minwidth=24, stretch=tk.NO)
        self.tree.column('exchange', width=70, minwidth=70, stretch=tk.NO)
        self.tree.column('pair', width=64, minwidth=64, stretch=tk.NO)
        self.tree.column('lprice', width=64, minwidth=64, stretch=tk.NO)
        self.tree.column('pprice', width=64, minwidth=64, stretch=tk.NO)
        self.tree.column('amount', width=64, minwidth=64, stretch=tk.NO)
        self.tree.column('sum', width=64, minwidth=64, stretch=tk.NO)
        self.tree.column('profit', width=64, minwidth=48)

        self.tree.heading('#0', text='N', anchor=tk.W)
        self.tree.heading('exchange', text='Exchange', anchor=tk.W)
        self.tree.heading('pair', text='Pair', anchor=tk.W)
        self.tree.heading('lprice', text='Last Price', anchor=tk.W)
        self.tree.heading('pprice', text='Pos. Price', anchor=tk.W)
        self.tree.heading('amount', text='Amount', anchor=tk.W)
        self.tree.heading('sum', text='Sum', anchor=tk.W)
        self.tree.heading('profit', text='P/L', anchor=tk.W)

        if self.app.user.pos_is_init and self.app.user.bot_is_init:
            self.tree.insert('', 'end', 'pos', text='1', values=(self.app.bot.exchange.capitalize(), self.app.bot.pair, self.app.user.last_price,
                                                                 self.app.gui.fp(self.app.position.price), self.app.gui.fq(self.app.position.qty), self.app.gui.fp(self.app.position.qty*self.app.position.price), '0.0'))
        else:
            self.tree.insert('', 'end', 'pos', text='1', values=('exchange', 'pair', '0.0', '0.0', '0.0', '0.0', '0.0'))
        self.tree.pack(fill=tk.X)

    def __check_for_pos_edit_window(self):
        try:
            self.app.gui.win_edit_position.focus()
        except:
            self.app.gui.win_edit_position = EditPositionWindow(True, self.root, self.app, price=self.app.position.price, qty=self.app.position.qty, buy_num_step=self.app.strategy.last_buy_step,
                                        sell_num_step=self.app.strategy.last_sell_step, start_price=self.app.strategy.start_price)

    def update_position(self):
        while True:
            try:
                profit = ((self.app.user.last_price - self.app.position.price) / self.app.position.price) * 100 if self.app.position.price > 0.0 else 0.0

                self.app.gui.win_position.tree.set('pos', 'exchange', self.app.position.exchange)
                self.app.gui.win_position.tree.set('pos', 'pair', self.app.position.pair)
                self.app.gui.win_position.tree.set('pos', 'lprice', self.app.user.last_price)
                self.app.gui.win_position.tree.set('pos', 'pprice', self.app.position.price)
                self.app.gui.win_position.tree.set('pos', 'amount', self.app.position.qty)
                self.app.gui.win_position.tree.set('pos', 'sum', self.app.position.price * self.app.position.qty)
                if profit > 0:
                    self.app.gui.win_position.tree.set('pos', 'profit', '+' + str(profit))
                else:
                    self.app.gui.win_position.tree.set('pos', 'profit', profit)

            except:
                pass
            sleep(1)

    def reset_position(self):
        self.app.common.reset_position()

class EditPositionWindow(tk.Toplevel):

    def __init__(self, apply, root, app, price=0.0, qty=0.0, buy_num_step=0, sell_num_step=0, start_price=0.0):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window(price, qty, buy_num_step, sell_num_step, start_price)
        else:
            self.destroy()

    def init_window(self, price, qty, buy_num_step, sell_num_step, start_price):
        self.title('Edit position')
        self.geometry('280x200'+self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bg='#ffffff', bd=0, width=280, height=200)
        tool_bar.pack(side=tk.TOP, fill=tk.BOTH)

        label_desc = tk.Label(tool_bar, text='Edit position', bg='#ffffff', font='Arial 10 bold')
        label_desc.place(x=10, y=10)

        label_price = tk.Label(tool_bar, text='Average price', bg='#ffffff')
        label_price.place(x=10, y=35)
        self.entry_price = ttk.Entry(tool_bar)
        self.entry_price.place(x=150, y=35, width=120)
        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, self.app.gui.fp(price))

        label_qty = tk.Label(tool_bar, text='Position amount', bg='#ffffff')
        label_qty.place(x=10, y=60)
        self.entry_qty = ttk.Entry(tool_bar)
        self.entry_qty.place(x=150, y=60, width=120)
        self.entry_qty.delete(0, tk.END)
        self.entry_qty.insert(0, self.app.gui.fq(qty))

        label_buy = tk.Label(tool_bar, text='Buy steps', bg='#ffffff')
        label_buy.place(x=10, y=85)
        self.entry_buy = ttk.Entry(tool_bar)
        self.entry_buy.place(x=150, y=85, width=120)
        self.entry_buy.delete(0, tk.END)
        self.entry_buy.insert(0, buy_num_step)

        label_sell = tk.Label(tool_bar, text='Sell steps', bg='#ffffff')
        label_sell.place(x=10, y=110)
        self.entry_sell = ttk.Entry(tool_bar)
        self.entry_sell.place(x=150, y=110, width=120)
        self.entry_sell.delete(0, tk.END)
        self.entry_sell.insert(0, sell_num_step)

        label_sell = tk.Label(tool_bar, text='Start price', bg='#ffffff')
        label_sell.place(x=10, y=135)
        self.entry_start_price = ttk.Entry(tool_bar)
        self.entry_start_price.place(x=150, y=135, width=120)
        self.entry_start_price.delete(0, tk.END)
        self.entry_start_price.insert(0, self.app.gui.fp(start_price))

        btn_apply = ttk.Button(tool_bar, text='Apply', command=self.edit_position)
        btn_apply.place(x=10, y=170, width=120, height=25)

        btn_cancel = ttk.Button(tool_bar, text='Cancel', command=self.destroy)
        btn_cancel.place(x=150, y=170, width=120, height=25)

    def edit_position(self):

        price = float(self.entry_price.get())
        qty = float(self.entry_qty.get())
        num_buy = int(self.entry_buy.get())
        num_sell = int(self.entry_sell.get())
        start_price = float(self.entry_start_price.get())

        self.app.position.edit(price=price, qty=qty)
        try:
            self.app.db.save_position(exchange=self.app.bot.exchange, pair=self.app.bot.pair, price=price, qty=qty)
        except Exception as e:
            self.app.errors.error(110, e)

        if num_buy > 0 and num_sell == 0:
            last_buy_price = price
            last_buy_step = num_buy
            last_sell_price = 0.0
            last_sell_step = 0
        elif num_sell > 0 and num_buy == 0:
            last_buy_price = 0.0
            last_buy_step = 0
            last_sell_price = price
            last_sell_step = num_sell
        else:
            last_buy_price = price
            last_buy_step = num_buy
            last_sell_price = price
            last_sell_step = num_sell

        depo_ex = price * qty

        self.app.strategy.edit(start_price=start_price, last_buy_price=last_buy_price, last_sell_price=last_sell_price,
                last_buy_step=last_buy_step, last_sell_step=last_sell_step, depo_ex=depo_ex)
        try:
            self.app.db.save_strategy(exchange=self.app.bot.exchange, pair=self.app.bot.pair,
                             data={'sell_price': self.app.bot.sell_price, 'buy_price': self.app.bot.buy_price,
                                   'sell_qty': self.app.bot.sell_qty, 'buy_qty': self.app.bot.buy_qty,
                                   'depo': self.app.bot.depo, 'depo_ex': self.app.strategy.depo_ex, 'exchange': self.app.bot.exchange,
                                   'pair': self.app.bot.pair, 'buy_type': self.app.bot.buy_type, 'sell_type': self.app.bot.sell_type})
        except Exception as e:
            self.app.errors.error(112, e)

        self.destroy()

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
                             data={'sell_price': self.app.bot.sell_price, 'buy_price': self.app.bot.buy_price,
                                   'sell_qty': self.app.bot.sell_qty, 'buy_qty': self.app.bot.buy_qty,
                                   'depo': self.app.bot.depo, 'depo_ex': self.app.strategy.depo_ex, 'exchange': self.app.bot.exchange,
                                   'pair': self.app.bot.pair, 'buy_type': self.app.bot.buy_type, 'sell_type': self.app.bot.sell_type})
        except Exception as e:
            self.app.errors.error(112, e)
        self.app.gui.log('Position cleared')
        return 0


class StatisticWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.__init_window()
            self.draw()
        else:
            self.destroy()

    def __init_window(self):
        self.title('Statistic window')
        self.geometry('400x300' + self.app.gui.rand_xy())
        self.resizable(False, False)
        self.bar = tk.Frame(self, bg='#ffffff', bd=0, width=400, height=300)
        self.bar.pack(side=tk.TOP, fill=tk.BOTH)
        self.canvas = tk.Canvas(self.bar, bg='#ffffff', bd=0, width=400, height=300)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.canvas.create_line(10, 10, 390, 10, fill="#dddddd")
        self.canvas.create_line(10, 66, 390, 66, fill="#dddddd")
        self.canvas.create_line(10, 122, 390, 122, fill="#dddddd")
        self.canvas.create_line(10, 178, 390, 178, fill="#dddddd")
        self.canvas.create_line(10, 234, 390, 234, fill="#dddddd")
        self.canvas.create_line(390, 10, 390, 290, fill="#dddddd")
        self.canvas.create_line(10, 290, 390, 290, fill="#dddddd")

    def draw(self):
        line_raw = self.app.stat.get_list()

        line = list()

        if len(line_raw) > 1:
            start_time = strftime('%d.%m.20%y', localtime(self.app.stat.start_time))
            last_time = strftime('%d.%m.20%y', localtime(time()))

            first = line_raw[0]
            for i in range(len(line_raw)):
                line.append(line_raw[i] / first * 100)

            if len(line) > 1:

                fig_low, fig_high, ystep, n = self.__look_ranges(min(line), max(line))
                xstep = 380 // (len(line) + 1)
                bar_width = xstep / 2
                pp = (fig_high - fig_low) / 280
                x1 = 0
                self.canvas.delete('my_stat_chart')

                self.canvas.create_text(10, 280, anchor=tk.W, font='Arial 8', text=start_time, tags='my_stat_chart')
                self.canvas.create_text(390, 280, anchor=tk.E, font='Arial 8', text=last_time, tags='my_stat_chart')

                y1 = self.__get_y(fig_high, line[0], pp)
                self.canvas.create_text(10, y1, anchor=tk.W, font='Arial 8', text='◄ 100%', tags='my_stat_chart')

                for i in range(len(line) - 1):
                    if i < 1:
                        x1 = bar_width
                    else:
                        x1 += xstep
                    x2 = x1 + xstep

                    y1 = self.__get_y(fig_high, line[i], pp)
                    y2 = self.__get_y(fig_high, line[i+1], pp)
                    self.canvas.create_line(x1, y1, x2, y2, fill="#3399cc", tags='my_stat_chart', width=2)

                x = 390
                y = self.__get_y(fig_high, line[-1], pp)
                self.canvas.create_text(x, y-1, anchor=tk.E, font='Arial 8', text=str(round(line[-1], 2)) + '% ►', tags='my_stat_chart')

    @staticmethod
    def __look_ranges(m, M):
        s = (round(log10(M - m)) - 1) if M - m > 0 else 0
        l = m - m % 10 ** s
        h = M - M % 10 ** s + 10 ** s
        step = (h - l) / 10
        return round(l, 9), round(h, 9), step, s - 1

    @staticmethod
    def __get_y(fh, p, pp):
        return (fh - p) / pp + 10


class DebugWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app
        if apply:
            self.init_window()
        else:
            self.destroy()

    def init_window(self):
        self.title('Debug window')
        self.geometry('260x400'+self.app.gui.rand_xy())
        self.resizable(False, False)

        label_params = tk.Label(self, text='Params', font='Arial 10 bold')
        label_params.place(x=10, y=10)

        self.box = tk.Text(self, font='Arial 10', wrap=tk.WORD)
        sbar = tk.Scrollbar(self.box)
        sbar['command'] = self.box.yview
        self.box['yscrollcommand'] = sbar.set
        self.box.place(x=10, y=35, width=240, height=360)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)

        req = dict()

        req['app_ver'] = self.app.user.ver
        req['app_build'] = self.app.user.build
        req['app_shared_key'] = self.app.user.shared_key
        req['app_demo_mode'] = self.app.user.demo_mode
        req['bot__________'] = ''
        req['bot_exchange'] = self.app.bot.exchange
        req['bot_pair'] = self.app.bot.pair
        req['bot_order_life'] = self.app.bot.order_life
        req['bot_depo'] = self.app.bot.depo
        req['bot_upd_time'] = self.app.bot.upd_time
        req['bot_pause'] = self.app.bot.pause
        req['pos__________'] = ''
        req['pos_price'] = self.app.position.price
        req['pos_qty'] = self.app.position.qty
        req['pos_exchange'] = self.app.position.exchange
        req['pos_pair'] = self.app.position.pair
        try:
            req['rules________'] = ''
            req['rules_min_price'] = self.app.user.rules[self.app.bot.pair]['minPrice']
            req['rules_max_price'] = self.app.user.rules[self.app.bot.pair]['maxPrice']
            req['rules_min_qty'] = self.app.user.rules[self.app.bot.pair]['minQty']
            req['rules_max_qty'] = self.app.user.rules[self.app.bot.pair]['maxQty']
            req['rules_min_sum'] = self.app.user.rules[self.app.bot.pair]['minSum']
            req['rules_max_sum'] = self.app.user.rules[self.app.bot.pair]['maxSum']
        except:
            pass
        req['user__________'] = ''
        req['user_api_init'] = self.app.user.api_is_init
        req['user_bot_init'] = self.app.user.bot_is_init
        req['user_bot_run'] = self.app.user.bot_is_run
        req['user_pos_init'] = self.app.user.pos_is_init
        req['user_kl_init'] = self.app.user.kl_is_init
        req['user_st_init'] = self.app.user.st_is_init
        req['user_last_price'] = self.app.user.last_price
        req['user_curr_base'] = self.app.user.curr_base
        req['user_curr_quote'] = self.app.user.curr_quote
        req['user_start_buy_trade'] = strftime('%y-%m-%d %H:%M', localtime(self.app.user.start_buy_trading))
        req['user_start_sell_trade'] = strftime('%y-%m-%d %H:%M', localtime(self.app.user.start_sell_trading))
        req['strategy__________'] = ''
        req['strategy_buy_price'] = self.app.strategy.buy_price
        req['strategy_buy_qty'] = self.app.strategy.buy_qty
        req['strategy_buy_type'] = self.app.strategy.buy_type
        req['strategy_sell_price'] = self.app.strategy.sell_price
        req['strategy_sell_qty'] = self.app.strategy.sell_qty
        req['strategy_sell_type'] = self.app.strategy.sell_type

        list_keys = list(req.keys())
        list_keys.sort()

        param_string = ''
        for item in list_keys:
            param_string += item + ': ' + str(req[item]) + '\n'

        self.box.insert(tk.END, param_string)
        self.box.configure(state='disabled')
        self.box.yview_moveto(1)


class InfoWindow(tk.Toplevel):

    def __init__(self, apply, root, app):
        super().__init__(root)
        self.app = app

        self.big_logo = tk.PhotoImage(data='R0lGODlhQABAAKIAAP70Av3oPfjfrfmcCZ9fCt6eZEQSAP///yH/C05FVFNDQVBFMi4wAwEAAAAh+QQEAAAAACwAAAAAQABAAAAD/3i63P4wykmrvTjrzbv/YCiOZGmeaKqupCCA7loMARgMhTrQ9q7zn9sgJdi9PsXB0TQDLDsCAA4VADhh1tqpGnhyBNxTFKBtCAqznRrtVVSvpXH5rK7b64Xlu23L0q2AgYKDOGBZJlw7g4uMgDthLVKKjgSVBpeYmZUEA4FqcCJJgQSZpaalBJ5KJDeOp6+wnVZAMK1WpLC5pqmzXUgBtgO6w6WyNL5fwLIAuMTEvFLAfBXAts2YaM7ZqL3AG2C2AKg5BwXXu+TmpY7SGlHBpeQKBbny5cW9oBeJt5n286/+3cPEiwYZDVUmXRNI7xRDTbM6ldknqZ8/Bg0DYuRWcbeihYSyzhFId27cPJERD2ZIycxhRl3bOE5CWLGls5uXCkqkKcUiTmcFD2UYY+znTWNWpkkgCqik0V2Okm54U/RpLqQq3c1qWs/BS6hb9Q0NKw7WSDRonWKKKtbdJylWTRkzIqLSqLgGoDEjQMLcJClqc3FyNGDkiSaeNileXGnZLIFxEDeaLCUPCwV0HFOWZPkyAxeZ7+AB7VkCGtE4IJeOAJr06tewY8ueTbu27du4c+vezbs3iwQAOw==')

        if apply:
            self.__init_window()
        else:
            self.destroy()

    def __init_window(self):
        self.title('About')
        self.geometry('260x300'+self.app.gui.rand_xy())
        self.resizable(False, False)

        tool_bar = tk.Frame(self, bg='#ffffff', bd=0, width=260, height=300)
        tool_bar.pack(side=tk.TOP, fill=tk.BOTH)

        y = 10
        tk.Label(tool_bar, image=self.big_logo, bd=0).place(x=10, y=0)
        tk.Label(tool_bar, text=self.app.user.name+' '+self.app.user.ver, bg='#ffffff', font='Arial 10 bold').place(x=90, y=y)

        y += 20
        tk.Label(tool_bar, text='Build '+self.app.user.build, bg='#ffffff', font='Arial 10').place(x=90, y=y)

        y += 40
        tk.Label(tool_bar, text='Automated trading bot based on ', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        y += 20
        tk.Label(tool_bar, text='price set manually. ', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        y += 40
        tk.Label(tool_bar, text='YouTube:', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        label_youtube = tk.Label(tool_bar, text='youtu.be/hiMJ49Ba_GE', fg='blue', cursor="hand2", bg='#ffffff', font='Arial 10')
        label_youtube.place(x=69, y=y)
        label_youtube.bind("<Button-1>", self.callback_youtube)

        y += 20
        tk.Label(tool_bar, text='GitHub: ', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        label_github = tk.Label(tool_bar, text='github.com/savinkirillnick/...', fg='blue', cursor="hand2", bg='#ffffff', font='Arial 10')
        label_github.place(x=58, y=y)
        label_github.bind("<Button-1>", self.callback_github)

        y += 40
        tk.Label(tool_bar, text='Registration and download last versions', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        y += 20
        tk.Label(tool_bar, text='Telegram:', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        label_telegram = tk.Label(tool_bar, text='@savin_account_manager_bot', fg='blue', cursor="hand2", bg='#ffffff', font='Arial 10')
        label_telegram.place(x=71, y=y)
        label_telegram.bind("<Button-1>", self.callback_telegram)

        y += 40
        tk.Label(tool_bar, text='Developed by Kirill Savin', bg='#ffffff', font='Arial 10').place(x=10, y=y)

        y += 20
        tk.Label(tool_bar, text='2017-2024', bg='#ffffff', font='Arial 10').place(x=10, y=y)

    @staticmethod
    def callback_youtube(event):
        webbrowser.open_new('https://www.youtube.com/watch?v=hiMJ49Ba_GE')

    @staticmethod
    def callback_github(event):
        webbrowser.open_new('https://github.com/savinkirillnick/docs/tree/master/sniperbot')

    @staticmethod
    def callback_telegram(event):
        webbrowser.open_new('https://web.telegram.org/k/#@savin_account_manager_bot')

