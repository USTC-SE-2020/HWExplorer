
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
#LeftControlButton {
    background: transparent;
    border: none;
}
#AdminLabel {
    font-size: 20px;
    color: black;
}
#Right_View {
    background: #FDD56C;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
}
#RightControlButton {
    background: transparent;
    border: none;
}
#UserLabel {
    font-size: 20px;  
    color: white;
}
#stateBarLabel {
    background: #04040F;
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
}
#StateBarTitle {
    font-size: 20px;
    color:#F7F5EE;
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


# 自定义无边框Dialog类
class Dialog(QDialog):

    # 用于控制器控制窗口跳转
    switch_window = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)
        self.setObjectName('Custom_Dialog')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("HWExplorer")
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
        # 添加顶部状态栏标题
        self.stateBarTitle = QLabel(self.stateBarLabel)
        self.stateBarTitle.setGeometry(QRect(320, 0, 150, 50))
        self.stateBarTitle.setObjectName("StateBarTitle")
        self.stateBarTitle.setText("HWExplorer")
        self.stateBarTitle.setAlignment(Qt.AlignCenter)

        # 添加中间对比视图: 650 x 300
        self.content_view = QWidget(self)
        self.content_view.setObjectName("Content_Widget")
        self.content_view.setGeometry(QRect(75, 170, 650, 300))
        # 左侧管理员登陆视图
        self.left_view = QWidget(self.content_view)
        self.left_view.setObjectName("Left_View")
        self.left_view.setGeometry(QRect(0, 0, 325, 300))
        self.left_contorl = QPushButton(self.left_view)         # 按钮覆盖到父视图上来响应点击事件
        self.left_contorl.setGeometry(QRect(0, 0, 325, 300))    # 透明背景色, 无边框
        self.left_contorl.setObjectName("LeftControlButton")
        self.left_contorl.clicked.connect(self.change_to_admin_mode)
        self.admin_label = QLabel(self.left_view)
        self.admin_label.setGeometry(QRect(100, 120, 120, 30))
        self.admin_label.setObjectName("AdminLabel")
        self.admin_label.setText("管理员模式")
        self.admin_label.setAlignment(Qt.AlignCenter)
        self.left_circle_index = QLabel(self.left_view)
        self.left_circle_index.setGeometry(QRect(150, 160, 10, 10))
        self.left_circle_index.setObjectName("LeftCircleIndex")

        # 右侧普通用户登陆视图(默认选项)
        self.right_view = QWidget(self.content_view)
        self.right_view.setObjectName("Right_View")
        self.right_view.setGeometry(QRect(325, 0, 325, 300))
        self.right_contorl = QPushButton(self.right_view)         # 按钮覆盖到父视图上来响应点击事件
        self.right_contorl.setGeometry(QRect(0, 0, 325, 300))    # 透明背景色, 无边框
        self.right_contorl.setObjectName("RightControlButton")
        self.right_contorl.clicked.connect(self.change_to_user_mode)
        self.user_label = QLabel(self.right_view)
        self.user_label.setGeometry(QRect(100, 120, 120, 30))
        self.user_label.setObjectName("UserLabel")
        self.user_label.setText("用户模式")
        self.user_label.setAlignment(Qt.AlignCenter)
        self.right_circle_index = QLabel(self.right_view)
        self.right_circle_index.setGeometry(QRect(150, 160, 10, 10))
        self.right_circle_index.setObjectName("RightCircleIndex")
        self.right_circle_index.setStyleSheet("background: red; border-radius: 5px;")
        self.login_mode = "user"        # 用户模式为默认登陆选项

        # 添加开始按钮
        self.StartButton = QPushButton(self.widget)
        self.StartButton.setGeometry(QRect(300, 500, 112, 41))
        self.StartButton.setObjectName("StartButton")
        self.StartButton.setText("Get Started")
        self.StartButton.clicked.connect(self.show_mainWindow)


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

    # 切换到管理员登陆模式
    def change_to_admin_mode(self):
        self.login_mode = "admin"
        # 左侧(管理员模式)深色 #FDD56C
        left_admin_style = "background: #FDD56C; border-top-left-radius: 20px; border-bottom-left-radius: 20px;"
        # 右侧(用户模式)浅色 #FFEDD2
        right_user_style = "background: #FFEDD2; border-top-right-radius: 20px; border-bottom-right-radius: 20px;"
        self.left_view.setStyleSheet(left_admin_style)
        self.admin_label.setStyleSheet("color: white;")
        self.left_circle_index.setStyleSheet("background: red; border-radius: 5px;")
        self.right_view.setStyleSheet(right_user_style)
        self.user_label.setStyleSheet("color: black;")
        self.right_circle_index.setStyleSheet("background: transparent;")

    # 切换到用户登陆模式
    def change_to_user_mode(self):
        self.login_mode = "user"
        # 左侧(管理员模式)浅色 #FFEDD2
        left_admin_style = "background: #FFEDD2; border-top-left-radius: 20px; border-bottom-left-radius: 20px;"
        # 右侧(用户模式)深色 #FDD56C
        right_user_style = "background: #FDD56C; border-top-right-radius: 20px; border-bottom-right-radius: 20px;"
        self.left_view.setStyleSheet(left_admin_style)
        self.admin_label.setStyleSheet("color: black;")
        self.left_circle_index.setStyleSheet("background: transparent;")
        self.right_view.setStyleSheet(right_user_style)
        self.user_label.setStyleSheet("color: white")
        self.right_circle_index.setStyleSheet("background: red; border-radius: 5px;")


