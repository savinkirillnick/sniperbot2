class Api:
    def __init__(self):
        self.exchanges = [
            'binance',
            'bithumb',
            'cex',
            'exmo',
            'huobi',
            'kucoin',
            'okcoin',
            'yobit'
        ]
        pass

    def fetch_time(self):
        return True

    def load_markets(self):
        # Получение правил биржи, монет и символов
        # pairs - set()
        # coins - set()
        # rules - dict()
        return dict()

    def fetch_order_book(self, *req):
        # Получение стакана
        # Сначала спредовые
        # depth = dict()
        return dict()

    def fetch_ticker(self, *req):
        # Получение последней цены
        return 0.0

    # Авторизованные методы

    def fetch_balance(self):
        # Получение балансов
        return dict()

    def fetch_my_trades(self, *req):
        # Получение истории ордеров
        # Сначала старые, в конце новые
        return list()

    def fetch_open_orders(self, *req):
        # Получение активных ордеров
        # Сначала старые, в конце новые
        return list()

    def cancel_order(self, *req):
        # Отмена ордера
        # orderId
        return dict()

    def create_order(self, *req):
        # Отправка ордера
        # orderId
        return dict()

    def create_limit_order(self, *req):
        # Отправка ордера
        # orderId
        return dict()

    def create_limit_buy_order(self, *req):
        # Отправка ордера
        # orderId
        return dict()

    def create_limit_sell_order(self, *req):
        # Отправка ордера
        # orderId
        return dict()

    def fetch_markets(self, *req):
        # Получение всех пар
        return dict()

    def fetch_ohlcv(self, *req):
        # получение графика
        return dict()
