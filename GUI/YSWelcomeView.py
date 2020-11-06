
# Frameworks

# from SplashLoading import GifSplashScreen
import sys
import cv2 as cv
from PyQt5.QtWidgets import QApplication
from GUI.YSMainWindow import MainWindow
from PyQt5.QtGui import QPalette, QPixmap, QFont, QMovie
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget,\
    QGraphicsDropShadowEffect, QPushButton, QGridLayout, QSpacerItem,\
    QSizePolicy, QLabel

# 样式表: 设置控件外观
Stylesheet = """
#Custom_Widget {
    background: white;
    border-radius: 20px;
}
#stateBarLabel {
    background: #FDD56C;
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
}
#ImageLabel {
    border-radius: 20px;
}
#closeButton {
    min-width: 36px;
    min-height: 36px;
    font-family: "Webdings";
    qproperty-text: "r";
    border-radius: 10px;
}
#StartButton {
    min-width: 150px;
    min-height: 36px;
    border-radius: 10px;
    background: red;
    color: white;
}
#StartButton:pressed {
    background: #FDD56C;
    color: black;
}
#closeButton:hover {
    color: white;
    background: red;
}
"""

# Global Constants
slogon = "Amazing Recognizer for your \nChinese handwriting document!"
logo_path = "Resources/Images/logo_img.png"

# 自定义无边框Dialog类
class Dialog(QDialog):

    # 用于控制器控制窗口跳转
    switch_window = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)
        self.setObjectName('Custom_Dialog')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(Stylesheet)
        self.initUi()
        # 添加阴影
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(12)
        effect.setOffset(0, 0)
        effect.setColor(Qt.gray)
        self.setGraphicsEffect(effect)

    # 界面布局
    def initUi(self):
        layout = QVBoxLayout(self)
        # 重点： 这个widget作为背景和圆角
        self.widget = QWidget(self)
        self.widget.setObjectName('Custom_Widget')

        # 添加状态栏
        self.stateBarLabel = QLabel(self.widget)
        self.stateBarLabel.setGeometry(QRect(0, 0, 760, 48))
        self.stateBarLabel.setObjectName("stateBarLabel")
        self.stateBarLabel.setText("HWExplorer")
        self.stateBarLabel.setFont(QFont("Roman", 20, QFont.Bold))
        self.stateBarLabel.setAlignment(Qt.AlignCenter)

        # 添加Slogon
        self.slogonLabel = QLabel(self.widget)
        self.slogonLabel.setGeometry(QRect(20, 150, 361, 81))
        self.slogonLabel.setObjectName("slogonLabel")
        self.slogonLabel.setText(slogon)
        self.slogonLabel.setFont(QFont("Roman",24, QFont.Bold))

        # 添加开始按钮
        self.StartButton = QPushButton(self.widget)
        self.StartButton.setGeometry(QRect(20, 300, 112, 41))
        self.StartButton.setObjectName("StartButton")
        self.StartButton.setText("Get Started")
        self.StartButton.clicked.connect(self.show_mainWindow)

        # 添加图片
        self.ImageLabel = QLabel(self.widget)
        self.ImageLabel.setGeometry(QRect(390, 100, 350, 350))
        self.ImageLabel.setObjectName("ImageLabel")
        self.ImageLabel.setPixmap(QPixmap(logo_path))
        self.ImageLabel.setScaledContents(True)

        layout.addWidget(self.widget)
        # 在widget中添加ui
        layout = QGridLayout(self.widget)
        layout.addItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 0)
        layout.addWidget(QPushButton('r', self, clicked=self.accept, objectName='closeButton'), 0, 1)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum,
                                   QSizePolicy.Expanding), 1, 0)

    # 设置QDialog的尺寸
    def sizeHint(self):
        return QSize(800, 600)

    # 退出程序
    def accept(self):
        sys.exit()

    # 事件响应
    @pyqtSlot()
    # 跳转到主窗口
    def show_mainWindow(self):
        self.switch_window.emit()


