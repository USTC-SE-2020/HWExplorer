
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

# 04040F  FDD56C
# 样式表: 设置控件外观
Stylesheet = """
#Custom_Widget {
    background: #F7F5EE;
    border-radius: 20px;
}
#Content_Widget {
    background: transparent;
    border-radius: 20px;
}
#Left_View {
    background: #FFEDD2;
    border-top-left-radius: 20px;
    border-bottom-left-radius: 20px;
}
#Right_View {
    background: #FDD56C;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
}
#stateBarLabel {
    background: #04040F;
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
    font-size: 15px;
    background: #FDD56C;
    color: black;
}
#StartButton:pressed {
    background: #0E0D0C;
    color: white;
}
#closeButton:hover {
    color: white;
    background: red;
}
"""

# Global Constants
logo_path = "Resources/Images/logo_explorer.png"
left_hw_path = "Resources/Images/hw_demo.png"
right_word_path = "Resources/Images/kai_black.png"

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

        # 添加顶部状态栏
        self.stateBarLabel = QLabel(self.widget)
        self.stateBarLabel.setGeometry(QRect(0, 0, 760, 48))
        self.stateBarLabel.setObjectName("stateBarLabel")

        # 添加Logo图片
        self.logoLabel = QLabel(self.widget)
        self.logoLabel.setGeometry(QRect(160, -120, 400, 400))
        self.logoLabel.setObjectName("logoLabel")
        self.logoLabel.setPixmap(QPixmap(logo_path))
        self.logoLabel.setScaledContents(True)

        # 添加中间对比视图: 650 x 300
        self.content_view = QWidget(self)
        self.content_view.setObjectName("Content_Widget")
        self.content_view.setGeometry(QRect(75, 170, 650, 300))
        # 添加左边手写视图
        self.left_view = QWidget(self.content_view)
        self.left_view.setObjectName("Left_View")
        self.left_view.setGeometry(QRect(0,0, 325, 300))
        self.left_image = QLabel(self.left_view)
        self.left_image.setGeometry(QRect(35, 25, 300, 250))
        self.left_image.setObjectName("Left_Image_Label")
        self.left_image.setPixmap(QPixmap(left_hw_path))
        self.left_image.setScaledContents(False)
        # 添加右边印刷体视图
        self.right_view = QWidget(self.content_view)
        self.right_view.setObjectName("Right_View")
        self.right_view.setGeometry(QRect(325, 0, 325, 300))
        self.right_image = QLabel(self.right_view)
        self.right_image.setGeometry(QRect(35, 25, 300, 250))
        self.right_image.setObjectName("Right_Image_Label")
        self.right_image.setPixmap(QPixmap(right_word_path))
        self.right_image.setScaledContents(False)

        # 添加开始按钮
        self.StartButton = QPushButton(self.widget)
        self.StartButton.setGeometry(QRect(300, 500, 112, 41))
        self.StartButton.setObjectName("StartButton")
        self.StartButton.setText("Get Started")
        self.StartButton.clicked.connect(self.show_mainWindow)

        # 添加图片
        # self.ImageLabel = QLabel(self.widget)
        # self.ImageLabel.setGeometry(QRect(390, 100, 350, 350))
        # self.ImageLabel.setObjectName("ImageLabel")
        # self.ImageLabel.setPixmap(QPixmap(logo_path))
        # self.ImageLabel.setScaledContents(True)

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


