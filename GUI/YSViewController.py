

import sys
from PyQt5 import QtCore, QtWidgets
from GUI.YSWelcomeView import Dialog
from GUI.YSMainWindow import MainWindow



# 利用控制器来控制页面到跳转
class Controller:
    def __init__(self):
        pass

    # 显示欢迎界面
    def show_welcome(self):
        self.welcome = Dialog()
        self.welcome.switch_window.connect(self.show_main)
        self.welcome.show()

    # 显示主界面
    def show_main(self):
        self.window = MainWindow()
        self.welcome.close()
        self.window.show()