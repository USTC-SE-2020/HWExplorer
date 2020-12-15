

import sys
from TextLineLocator.YSTextLineLocator import TextLineLocator
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from PyQt5.QtGui import QPixmap, QFont, QImage, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, pyqtSlot, pyqtSignal, QThread
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QFileDialog

Win_Width = 500
Win_Height = 300


# QSS样式表
Stylesheet = """

#Custom_Window {
    background: white;
}

#Login_Widget {
    background: #fefbfa;
}

#User_Label {
    font-size: 25px;
}

#Login_Button {
    background: orange;
    color: red;
}
#Login_Button:pressed {
    background: red;
    color: orange;
}

"""


class CMWindow(QMainWindow):

    # 初始化
    def __init__(self, *args, **kwargs):
        super(CMWindow, self).__init__(*args, **kwargs)
        # 设置对象名: 用于设置QSS样式
        self.setObjectName('Custom_Window')

        # 定义窗口大小
        self.resize(Win_Width, Win_Height)

        # 设置放缩尺寸
        self.setMaximumSize(Win_Width, Win_Height)
        self.setMinimumSize(Win_Width, Win_Height)
        self.setWindowTitle("TEST")

        # QSS样式表: 应用于全局
        self.setStyleSheet(Stylesheet)

        # 界面布局
        self.initUi()


    # 界面布局
    def initUi(self):
        # 生成实例对象: 参数为父视图
        self.login_widget = QWidget(self)
        # 设置对象名
        self.login_widget.setObjectName("Login_Widget")
        # 指定大小和位置, QRect: x,y,width,height
        self.login_widget.setGeometry(QRect(100, 40, 300, 200))

        self.pressed = False


        # label, 父视图为login_widget
        self.user_label = QLabel(self.login_widget)
        self.user_label.setObjectName("User_Label")
        self.user_label.setGeometry(QRect(10, 10, 150, 40))
        self.user_label.setText("用户名:")

        # Button,
        self.login_button = QPushButton(self.login_widget)
        self.login_button.setObjectName("Login_Button")
        self.login_button.setGeometry(QRect(80, 100, 100, 60))
        self.login_button.setText("登陆")
        # 控制事件
        self.login_button.clicked.connect(self.change_text)



    @pyqtSlot()
    def change_text(self):
        self.pressed = not self.pressed
        if self.pressed:
            self.user_label.setText("更改了内容!")
        else:
            self.user_label.setText("用户名:")


def main():
    app = QApplication(sys.argv)
    cm_win = CMWindow()
    cm_win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()