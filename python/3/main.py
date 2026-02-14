from gui import *
from user import *
from bot import *
from errors import *
from common import *
from strategy import *
from kline import *
from db import *
from position import *
from statistic import *
from alarm import *
from api import *
from threadtimer import *
import sys


class App:
    def __init__(self):
        self.debug = False
        for i in sys.argv:
            a = i.split("=")
            if a[0] == '--debug':
                self.debug = True
        self.ttimer = ThreadTimer()
        self.alarm = Alarm()
        self.errors = Errors()
        self.bot = Bot()
        self.user = User()
        self.strategy = Strategy(self)
        self.kline = Kline()
        self.position = Position(self)
        self.stat = Statistic()
        self.api = Api()
        self.db = DB(self)
        self.common = Common(self)
        self.gui = Gui(self)

    def start(self):
        self.gui.run()


if __name__ == "__main__":

    app = App()
    app.start()

