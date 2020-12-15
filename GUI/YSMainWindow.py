
# Frameworks
import sys
import time
import cv2 as cv
from Tools import DataFormatter as df
from Tools import FileManager as fm
from TextLineLocator.YSTextLineLocator import TextLineLocator
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from PyQt5.QtGui import QPixmap, QFont, QImage, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, pyqtSlot, pyqtSignal, QThread
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QFileDialog

from GUI.config import *
from TextLineRecognizer.YSRecognizer import Recognizer




# TODO: 多视图切换测试
from GUI.YSLineRecView import LineRecognizeView
from GUI.YSLocRecView import LocateRecognizeView
from GUI.YSAboutView import AboutView



# 样式表: 设置控件外观
Stylesheet = """
#Background_Widget {
    background: #04040F;
    border-radius: 20px;
}
#Top_State_Bar {
    background: #CACCC6;
    border-top-right-radius: 20px;
}
#Left_Menu_Bar {
    background: transparent;
}
#Logo_Label {
    background: #CACCC6;
    font-family: "Times New Roman";
    font-size: 20px;
    color: black;
}
#Locate_Rec_Button {
    border: none;
    background: #B08B7C;
    color: white;
    border-radius: 10px;
    font-size: 15px;
    text-align: left;
}
#Text_Line_Button {
    border: none;
    background: #F93625;
    color: white;
    border-radius: 10px;
    font-size: 15px;
}
#About_Button {
    border: none;
    background: #CACCC6;
    color: black;
    border-radius: 10px;
    font-size: 15px;
}
#Exit_Button {
    qproperty-icon: url(" ");
    qproperty-iconSize: 1px 1px;
    background: transparent;
    background-image: url(Resources/Images/logout.png);
    background-position: center;
    background-repeat: no-repeat;
}
#Exit_Button:pressed {
    background-image: url(Resources/Images/logout_pressed.png);
    background-repeat: no-repeat;
}
#Right_Content_Widget {
    background: #F1F4FA;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
}
"""


# 主窗口: 左侧菜单栏+右侧内容区域
class MainWindow(QMainWindow):
    # 用于控制窗口跳转
    switch_window = pyqtSignal()

    # 初始化
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setObjectName('Custom_Window')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(Main_Win_Width, Main_Win_Height)
        self.setMaximumSize(Main_Win_Width, Main_Win_Height)                # 设置窗口最大宽度,最大高度()
        self.setMinimumSize(Main_Win_Width, Main_Win_Height)                # 设置窗口最小宽度,最小高度
        self.start_flag = False             #
        self.center()                                                       # 窗口居中
        self.setWindowTitle("HWExplorer")                                   # 设置窗口标题
        self.setStyleSheet(Stylesheet)                                      # 初始化GUI样式
        self.initUi()                                                       # 初始化GUI布局
        self.change_menu_button_selected(self.locate_rec_button)            # 默认显示定位+识别视图

    # 界面布局
    def initUi(self):
        # 背景Widget, 用于设置圆角窗口
        self.background_widget = QWidget(self)
        self.background_widget.setObjectName('Background_Widget')
        self.background_widget.setGeometry(QRect(0,0,Main_Win_Width, Main_Win_Height))

        # 左侧菜单栏
        self.left_menu_bar = QWidget(self.background_widget)
        self.left_menu_bar.setObjectName("Left_Menu_Bar")
        self.left_menu_bar.setGeometry(QRect(0, 0, Left_Menu_Bar_Width, Left_Menu_Bar_Height))
        # 项目名称Label
        self.logo_label = QLabel(self.left_menu_bar)
        self.logo_label.setObjectName("Logo_Label")
        self.logo_label.setGeometry(QRect(0, 80, Left_Menu_Bar_Width, 60))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setText("HW\nExplorer")
        self.logo_label.setWordWrap(True)
        # 切换按钮: 定位+识别页面
        self.locate_rec_button = QPushButton(self.left_menu_bar)
        self.locate_rec_button.setObjectName("Locate_Rec_Button")
        self.locate_rec_button.setText("文章")
        self.locate_rec_button.setGeometry(QRect(15,  300, 80, 60))
        self.locate_rec_button.clicked.connect(self.change_to_locate_recognize_view)
        # 切换按钮: 文本行识别页面
        self.text_line_button = QPushButton(self.left_menu_bar)
        self.text_line_button.setObjectName("Text_Line_Button")
        self.text_line_button.setText("文本行")
        self.text_line_button.setGeometry(QRect(30, 500, 80, 60))
        self.text_line_button.clicked.connect(self.change_to_text_line_view)
        # 关于按钮: 项目详情页面
        self.about_button = QPushButton(self.left_menu_bar)
        self.about_button.setObjectName("About_Button")
        self.about_button.setText("关于")
        self.about_button.setGeometry(QRect(15, 700, 80, 60))
        self.about_button.clicked.connect(self.change_to_about_view)
        # 退出按钮: 左侧菜单栏
        self.exit_button = QPushButton(self.left_menu_bar)
        self.exit_button.setObjectName("Exit_Button")
        self.exit_button.setGeometry(QRect(20, Main_Win_Height - 100, 40, 40))
        self.exit_button.clicked.connect(self.exit_application)

        # 右侧内容Widget
        self.right_content_widget = QWidget(self.background_widget)
        self.right_content_widget.setObjectName("Right_Content_Widget")
        self.right_content_widget.setGeometry(QRect(Left_Menu_Bar_Width, 0, Right_Content_Width, Right_Content_Height))
        # 文本行识别视图
        self.text_line_view = LineRecognizeView(self.right_content_widget)
        self.text_line_view.setGeometry(QRect(0, 0, Sub_Win_Width, Sub_Win_Height))
        self.text_line_view.setVisible(False)
        # 文本行定位+识别视图
        self.locate_rec_view = LocateRecognizeView(self.right_content_widget)
        self.locate_rec_view.setGeometry(QRect(0, 0, Sub_Win_Width, Sub_Win_Height))
        self.locate_rec_view.setVisible(True)                                           # 默认显示定位+识别视图
        # 关于视图
        self.about_view = AboutView(self.right_content_widget)
        self.about_view.setGeometry(QRect(0, 0, Sub_Win_Width, Sub_Win_Height))
        self.about_view.setVisible(False)

    # 窗口居中
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2 - 50)

    # 事件响应
    @pyqtSlot()
    # TODO: 多视图切换测试
    # 切换到定位+识别页面
    def change_to_locate_recognize_view(self):
        self.change_menu_button_selected(self.locate_rec_button)            # 切换菜单栏按钮状态
        self.text_line_view.setVisible(False)                               # 隐藏文本行页面
        self.about_view.setVisible(False)                                   # 隐藏关于页面
        self.locate_rec_view.setVisible(True)                               # 显示定位+识别页面

    # 切换到文本行识别页面
    def change_to_text_line_view(self):
        self.change_menu_button_selected(self.text_line_button)             # 切换菜单栏按钮状态
        self.locate_rec_view.setVisible(False)                              # 隐藏定位+识别页面
        self.about_view.setVisible(False)                                   # 隐藏关于页面
        self.text_line_view.setVisible(True)                                # 显示文本行页面

    # 切换到关于页面
    def change_to_about_view(self):
        self.change_menu_button_selected(self.about_button)                 # 切换菜单栏按钮状态
        self.about_view.setVisible(True)                                    # 显示关于页面
        self.text_line_view.setVisible(False)                               # 隐藏文本行页面
        self.locate_rec_view.setVisible(False)                              # 隐藏定位+识别页面

    # 切换菜单栏按钮选中效果
    def change_menu_button_selected(self, selected_btn):

        selected_style = "border:none;background:red;color:white;border-radius:10px;font-size:15px;text-align:center;"
        default_style = "border:none;background:#CACCC6;color:black;border-radius:10px;font-size:15px;text-align:left;"

        if selected_btn == self.locate_rec_button:                          # 定位+识别
            self.locate_rec_button.setStyleSheet(selected_style)
            self.locate_rec_button.setGeometry(QRect(15, 300, 80, 60))

            self.text_line_button.setStyleSheet(default_style)
            self.text_line_button.setGeometry(QRect(30, 500, 80, 60))
            self.about_button.setStyleSheet(default_style)
            self.about_button.setGeometry(QRect(30, 700, 80, 60))
        elif selected_btn == self.text_line_button:                         # 文本行识别
            self.text_line_button.setStyleSheet(selected_style)
            self.text_line_button.setGeometry(QRect(15, 500, 80, 60))

            self.locate_rec_button.setStyleSheet(default_style)
            self.locate_rec_button.setGeometry(QRect(30, 300, 80, 60))
            self.about_button.setStyleSheet(default_style)
            self.about_button.setGeometry(QRect(30, 700, 80, 60))
        elif selected_btn == self.about_button:                             # 关于
            self.about_button.setStyleSheet(selected_style)
            self.about_button.setGeometry(QRect(15, 700, 80, 60))

            self.locate_rec_button.setStyleSheet(default_style)
            self.locate_rec_button.setGeometry(QRect(30, 300, 80, 60))
            self.text_line_button.setStyleSheet(default_style)
            self.text_line_button.setGeometry(QRect(30, 500, 80, 60))

    # 退出程序
    def exit_application(self):
        sys.exit()
