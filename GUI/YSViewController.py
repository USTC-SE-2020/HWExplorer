

import sys
from PyQt5 import QtCore, QtWidgets
from GUI.YSWelcomeView import Dialog
from GUI.YSMainWindow import MainWindow
from GUI.YSAdminWindow import AdminWindow



# TODO: 视图控制器, 利用控制器来控制页面到跳转
class Controller:
    def __init__(self):
        pass

    # 显示欢迎界面
    def show_welcome(self):
        self.welcome = Dialog()                                     # 创建欢迎界面
        self.welcome.switch_window.connect(self.show_main)          # 跳转到主窗口, 绑定欢迎界面的 pyqtslot() 到控制器的事件上
        self.welcome.admin_window.connect(self.show_admin)          # 跳转到管理员界面, 绑定欢迎界面的 pyqtslot() 到控制器的事件上
        self.welcome.show()                                         # 显示欢迎界面

    # 显示主界面
    def show_main(self):
        self.window = MainWindow()                                  # 创建主窗口界面
        self.welcome.close()                                        # 关闭当前窗口-欢迎界面
        self.window.show()                                          # 显示主窗口界面

    # 显示管理员界面
    def show_admin(self):
        self.admin_win = AdminWindow()                              # 创建管理员窗口界面
        self.admin_win.back_wel_win.connect(self.back_welcome)      # 从管理员窗口退回到欢迎界面
        self.welcome.close()                                        # 关闭当前窗口-欢迎界面
        self.admin_win.show()                                       # 显示管理员界面窗口

    # 重新显示欢迎界面
    def back_welcome(self):
        self.admin_win.close()
        self.show_welcome()
