import sys
import time
import math
import cv2 as cv
from Tools import DataFormatter as df
from Tools import FileManager as fm
from TextLineLocator.YSTextLineLocator import TextLineLocator
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from PyQt5.QtGui import QPixmap, QFont, QImage, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, pyqtSlot, pyqtSignal, QThread
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QFileDialog


# Global Constants
Main_Win_Width = 1500
Main_Win_Height = 1000
Image_Area_Width = 400
Image_Area_Height = 700
Textline_Show_Width = 350
Textline_Show_Height = 60
# 样式表: 设置控件外观
Stylesheet = """
#Background_Widget {
    background: #04040F;
    border-radius: 20px;
}
#Left_Menu_Bar {
    background: transparent;
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
#Top_State_Bar {
    background: #CACCC6;
    border-top-right-radius: 20px;
}
#Add_Button {
    border-radius: 10px;
    background: #04040F;
    font-size: 15px;
    color: white;
}
#Image_Area_Widget {
    background: #CACCC6;
    border-radius: 20px;
}
#ori_Images_widget {
    background: #A52A2A;
    border-radius: 20px;
}
#resultshow_widgt {
    background: #CD853F;
    border-radius: 20px;
}
#ori_Images_label_widget{
    background: #8FBC8F;
    border-radius: 20px;
}
#Bottom_Control_Bar {
    background: #F1F4FA;
    border-radius: 20px;
}
#preBtn {
    border-radius: 10px;
    background: #04040F;
    color: white;
}
#preBtn:pressed {
    background: #FDD56C;
    color: black;
}
#nextBtn {
    border-radius: 10px;
    background: #04040F;
    color: white;
}
#nextBtn:pressed {
    background: #FDD56C;
    color: black;
}
#numLabel {
    font-size: 25px;
}
#Total_Time_Label {
    font-size: 12px;
}
#Aver_Time_Label {
    font-size: 12px;
}
#ori_Images_textlineView01 {
    background: #FAF0E6;
    border-radius: 20px;
}
#ori_Images_textlineView02 {
    background: #FAF0E6;
    border-radius: 20px;
}
#ori_Images_textlineView03 {
    background: #FAF0E6;
    border-radius: 20px;
}
#ori_Images_textlineView04 {
    background: #FAF0E6;
    border-radius: 20px;
}
#ori_Images_textlineView05 {
    background: #FAF0E6;
    border-radius: 20px;
}
#ori_Images_textlineView06 {
    background: #FAF0E6;
    border-radius: 20px;
}
#ori_Images_textlineView07 {
    background: #FAF0E6;
    border-radius: 20px;
}
#ori_Images_textlineView08 {
    background: #FAF0E6;
    border-radius: 20px;
}
#ori_Images_textlineView09 {
    background: #FAF0E6;
    border-radius: 20px;
}
#ori_Images_textlineView10 {
    background: #FAF0E6;
    border-radius: 20px;
}
#resultshow_textlineView01 {
    background: #F5F5DC;
    border-radius: 20px;
}
#resultshow_textlineView02 {
    background: #F5F5DC;
    border-radius: 20px;
}
#resultshow_textlineView03 {
    background: #F5F5DC;
    border-radius: 20px;
}
#resultshow_textlineView04 {
    background: #F5F5DC;
    border-radius: 20px;
}
#resultshow_textlineView05 {
    background: #F5F5DC;
    border-radius: 20px;
}
#resultshow_textlineView06 {
    background: #F5F5DC;
    border-radius: 20px;
}
#resultshow_textlineView07 {
    background: #F5F5DC;
    border-radius: 20px;
}
#resultshow_textlineView08 {
    background: #F5F5DC;
    border-radius: 20px;
}
#resultshow_textlineView09 {
    background: #F5F5DC;
    border-radius: 20px;
}
#resultshow_textlineView10 {
    background: #F5F5DC;
    border-radius: 20px;
}
#ori_Images_label_textlineView01{
    background: #F0FFF0;
    border-radius: 20px;
}
#ori_Images_label_textlineView02{
    background: #F0FFF0;
    border-radius: 20px;
}
#ori_Images_label_textlineView03{
    background: #F0FFF0;
    border-radius: 20px;
}
#ori_Images_label_textlineView04{
    background: #F0FFF0;
    border-radius: 20px;
}
#ori_Images_label_textlineView05{
    background: #F0FFF0;
    border-radius: 20px;
}
#ori_Images_label_textlineView06{
    background: #F0FFF0;
    border-radius: 20px;
}
#ori_Images_label_textlineView07{
    background: #F0FFF0;
    border-radius: 20px;
}
#ori_Images_label_textlineView08{
    background: #F0FFF0;
    border-radius: 20px;
}
#ori_Images_label_textlineView09{
    background: #F0FFF0;
    border-radius: 20px;
}
#ori_Images_label_textlineView10{
    background: #F0FFF0;
    border-radius: 20px;
}
"""

class MainWindow(QMainWindow):
    # 用于控制窗口跳转
    switch_window = pyqtSignal()

    # 初始化
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setObjectName('Custom_Window')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(Main_Win_Width,Main_Win_Height)
        self.setMaximumSize(Main_Win_Width, Main_Win_Height)
        self.setMinimumSize(Main_Win_Width, Main_Win_Height)
        self.ori_Images = []
        self.resultshow_Images = []
        self.ori_Images_label  = []
        self.locate_start_timer = 0
        self.locate_end_timer = 0
        self.curr_Img_Index = 0
        self.start_flag = False
        self.center()
        self.setWindowTitle("HWExplorer")
        self.setStyleSheet(Stylesheet)
        self.initUi()
        # 初始化后台线程
        self.backThread = None

    # 界面布局
    def initUi(self):
        # 背景Widget, 用于设置圆角窗口
        self.background_widget = QWidget(self)
        self.background_widget.setObjectName('Background_Widget')
        self.background_widget.setGeometry(QRect(0,0,Main_Win_Width, Main_Win_Height))

        # 左侧菜单栏
        self.left_menu_bar = QWidget(self.background_widget)
        self.left_menu_bar.setObjectName("Left_Menu_Bar")
        self.left_menu_bar.setGeometry(QRect(0,0,80, Main_Win_Height))
        # 退出按钮: 左侧菜单栏
        self.exit_button = QPushButton(self.left_menu_bar)
        self.exit_button.setObjectName("Exit_Button")
        self.exit_button.setGeometry(QRect(20, Main_Win_Height - 100, 40, 40))
        self.exit_button.clicked.connect(self.exit_application)

        # 右侧内容Widget
        self.right_content_widget = QWidget(self.background_widget)
        self.right_content_widget.setObjectName("Right_Content_Widget")
        self.right_content_widget.setGeometry(QRect(80,0,Main_Win_Width - 80,Main_Win_Height))
        # 顶部状态栏
        self.top_state_bar = QWidget(self.right_content_widget)
        self.top_state_bar.setObjectName("Top_State_Bar")
        self.top_state_bar.setGeometry(QRect(0, 0, Main_Win_Width - 80, 80))
        # 添加按钮
        self.add_Button = QPushButton(self.top_state_bar)
        self.add_Button.setGeometry(QRect((Main_Win_Width - 80) / 2 - 50, 10, 100, 60))
        self.add_Button.setObjectName("Add_Button")
        self.add_Button.setText("选择文件夹")
        self.add_Button.clicked.connect(self.choose_Diretory)

        # 图片区域Widget
        self.image_area_widget = QWidget(self.right_content_widget)
        self.image_area_widget.setObjectName("Image_Area_Widget")
        self.image_area_widget.setGeometry(QRect(60, 100, Image_Area_Width * 3 + 30 * 2 + 20 * 2, Image_Area_Height + 120))

        # 原始图像Widget
        self.ori_Images_widget = QWidget(self.image_area_widget)
        self.ori_Images_widget.setObjectName("ori_Images_widget")
        self.ori_Images_widget.setGeometry(QRect(20,20,Image_Area_Width,Image_Area_Height))

        # 原始图像中10个文本行展示
        self.ori_Images_textlineView01 = QWidget(self.ori_Images_widget)
        self.ori_Images_textlineView01.setObjectName("ori_Images_textlineView01")
        self.ori_Images_textlineView01.setGeometry(QRect(25,5,Textline_Show_Width,Textline_Show_Height))

        self.ori_Images_textlineView02 = QWidget(self.ori_Images_widget)
        self.ori_Images_textlineView02.setObjectName("ori_Images_textlineView02")
        self.ori_Images_textlineView02.setGeometry(QRect(25, 5 + 10 + Textline_Show_Height, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_textlineView03 = QWidget(self.ori_Images_widget)
        self.ori_Images_textlineView03.setObjectName("ori_Images_textlineView03")
        self.ori_Images_textlineView03.setGeometry(
            QRect(25, 5 + 10 * 2 + Textline_Show_Height * 2, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_textlineView04 = QWidget(self.ori_Images_widget)
        self.ori_Images_textlineView04.setObjectName("ori_Images_textlineView04")
        self.ori_Images_textlineView04.setGeometry(
            QRect(25, 5 + 10 * 3 + Textline_Show_Height * 3, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_textlineView05 = QWidget(self.ori_Images_widget)
        self.ori_Images_textlineView05.setObjectName("ori_Images_textlineView05")
        self.ori_Images_textlineView05.setGeometry(
            QRect(25, 5 + 10 * 4 + Textline_Show_Height * 4, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_textlineView06 = QWidget(self.ori_Images_widget)
        self.ori_Images_textlineView06.setObjectName("ori_Images_textlineView06")
        self.ori_Images_textlineView06.setGeometry(
            QRect(25, 5 + 10 * 5 + Textline_Show_Height * 5, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_textlineView07 = QWidget(self.ori_Images_widget)
        self.ori_Images_textlineView07.setObjectName("ori_Images_textlineView07")
        self.ori_Images_textlineView07.setGeometry(
            QRect(25, 5 + 10 * 6 + Textline_Show_Height * 6, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_textlineView08 = QWidget(self.ori_Images_widget)
        self.ori_Images_textlineView08.setObjectName("ori_Images_textlineView08")
        self.ori_Images_textlineView08.setGeometry(
            QRect(25, 5 + 10 * 7 + Textline_Show_Height * 7, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_textlineView09 = QWidget(self.ori_Images_widget)
        self.ori_Images_textlineView09.setObjectName("ori_Images_textlineView09")
        self.ori_Images_textlineView09.setGeometry(
            QRect(25, 5 + 10 * 8 + Textline_Show_Height * 8, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_textlineView10 = QWidget(self.ori_Images_widget)
        self.ori_Images_textlineView10.setObjectName("ori_Images_textlineView10")
        self.ori_Images_textlineView10.setGeometry(
            QRect(25, 5 + 10 * 9 + Textline_Show_Height * 9, Textline_Show_Width, Textline_Show_Height))


        # 预测结果Widgt
        self.resultshow_widgt =  QWidget(self.image_area_widget)
        self.resultshow_widgt.setObjectName("resultshow_widgt")
        self.resultshow_widgt.setGeometry(QRect(20+Image_Area_Width + 30,20,Image_Area_Width,Image_Area_Height))

        # 10个文本行预测结果Widgt
        self.resultshow_textlineView01 = QWidget(self.resultshow_widgt)
        self.resultshow_textlineView01.setObjectName("resultshow_textlineView01")
        self.resultshow_textlineView01.setGeometry(QRect(25, 5, Textline_Show_Width, Textline_Show_Height))

        self.resultshow_textlineView02 = QWidget(self.resultshow_widgt)
        self.resultshow_textlineView02.setObjectName("resultshow_textlineView02")
        self.resultshow_textlineView02.setGeometry(QRect(25, 5 + 10 + Textline_Show_Height, Textline_Show_Width, Textline_Show_Height))

        self.resultshow_textlineView03 = QWidget(self.resultshow_widgt)
        self.resultshow_textlineView03.setObjectName("resultshow_textlineView03")
        self.resultshow_textlineView03.setGeometry(
            QRect(25, 5 + 10 * 2 + Textline_Show_Height * 2, Textline_Show_Width, Textline_Show_Height))

        self.resultshow_textlineView04 = QWidget(self.resultshow_widgt)
        self.resultshow_textlineView04.setObjectName("resultshow_textlineView04")
        self.resultshow_textlineView04.setGeometry(
            QRect(25, 5 + 10 * 3 + Textline_Show_Height * 3, Textline_Show_Width, Textline_Show_Height))

        self.resultshow_textlineView05 = QWidget(self.resultshow_widgt)
        self.resultshow_textlineView05.setObjectName("resultshow_textlineView05")
        self.resultshow_textlineView05.setGeometry(
            QRect(25, 5 + 10 * 4 + Textline_Show_Height * 4, Textline_Show_Width, Textline_Show_Height))

        self.resultshow_textlineView06 = QWidget(self.resultshow_widgt)
        self.resultshow_textlineView06.setObjectName("resultshow_textlineView06")
        self.resultshow_textlineView06.setGeometry(
            QRect(25, 5 + 10 * 5 + Textline_Show_Height * 5, Textline_Show_Width, Textline_Show_Height))

        self.resultshow_textlineView07 = QWidget(self.resultshow_widgt)
        self.resultshow_textlineView07.setObjectName("resultshow_textlineView07")
        self.resultshow_textlineView07.setGeometry(
            QRect(25, 5 + 10 * 6 + Textline_Show_Height * 6, Textline_Show_Width, Textline_Show_Height))

        self.resultshow_textlineView08 = QWidget(self.resultshow_widgt)
        self.resultshow_textlineView08.setObjectName("resultshow_textlineView08")
        self.resultshow_textlineView08.setGeometry(
            QRect(25, 5 + 10 * 7 + Textline_Show_Height * 7, Textline_Show_Width, Textline_Show_Height))

        self.resultshow_textlineView09 = QWidget(self.resultshow_widgt)
        self.resultshow_textlineView09.setObjectName("resultshow_textlineView09")
        self.resultshow_textlineView09.setGeometry(
            QRect(25, 5 + 10 * 8 + Textline_Show_Height * 8, Textline_Show_Width, Textline_Show_Height))

        self.resultshow_textlineView10 = QWidget(self.resultshow_widgt)
        self.resultshow_textlineView10.setObjectName("resultshow_textlineView10")
        self.resultshow_textlineView10.setGeometry(
            QRect(25, 5 + 10 * 9 + Textline_Show_Height * 9, Textline_Show_Width, Textline_Show_Height))

        # 标签Widgt
        self.ori_Images_label_widget = QWidget(self.image_area_widget)
        self.ori_Images_label_widget.setObjectName("ori_Images_label_widget")
        self.ori_Images_label_widget.setGeometry(
            QRect(20 + 30 * 2 + 2 * Image_Area_Width,20,Image_Area_Width,Image_Area_Height))


        # 10个标签Widgt
        self.ori_Images_label_textlineView01 = QWidget(self.ori_Images_label_widget)
        self.ori_Images_label_textlineView01.setObjectName("ori_Images_label_textlineView01")
        self.ori_Images_label_textlineView01.setGeometry(
            QRect(25, 5 , Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_label_textlineView02 = QWidget(self.ori_Images_label_widget)
        self.ori_Images_label_textlineView02.setObjectName("ori_Images_label_textlineView02")
        self.ori_Images_label_textlineView02.setGeometry(
            QRect(25, 5 + 10 + Textline_Show_Height, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_label_textlineView03 = QWidget(self.ori_Images_label_widget)
        self.ori_Images_label_textlineView03.setObjectName("ori_Images_label_textlineView03")
        self.ori_Images_label_textlineView03.setGeometry(
            QRect(25, 5 + 10 * 2 + Textline_Show_Height * 2, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_label_textlineView04 = QWidget(self.ori_Images_label_widget)
        self.ori_Images_label_textlineView04.setObjectName("ori_Images_label_textlineView04")
        self.ori_Images_label_textlineView04.setGeometry(
            QRect(25, 5 + 10 * 3 + Textline_Show_Height * 3, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_label_textlineView05 = QWidget(self.ori_Images_label_widget)
        self.ori_Images_label_textlineView05.setObjectName("ori_Images_label_textlineView05")
        self.ori_Images_label_textlineView05.setGeometry(
            QRect(25, 5 + 10 * 4 + Textline_Show_Height * 4, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_label_textlineView06 = QWidget(self.ori_Images_label_widget)
        self.ori_Images_label_textlineView06.setObjectName("ori_Images_label_textlineView06")
        self.ori_Images_label_textlineView06.setGeometry(
            QRect(25, 5 + 10 * 5 + Textline_Show_Height * 5, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_label_textlineView07 = QWidget(self.ori_Images_label_widget)
        self.ori_Images_label_textlineView07.setObjectName("ori_Images_label_textlineView07")
        self.ori_Images_label_textlineView07.setGeometry(
            QRect(25, 5 + 10 * 6 + Textline_Show_Height * 6, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_label_textlineView08 = QWidget(self.ori_Images_label_widget)
        self.ori_Images_label_textlineView08.setObjectName("ori_Images_label_textlineView08")
        self.ori_Images_label_textlineView08.setGeometry(
            QRect(25, 5 + 10 * 7 + Textline_Show_Height * 7, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_label_textlineView09 = QWidget(self.ori_Images_label_widget)
        self.ori_Images_label_textlineView09.setObjectName("ori_Images_label_textlineView09")
        self.ori_Images_label_textlineView09.setGeometry(
            QRect(25, 5 + 10 * 8 + Textline_Show_Height * 8, Textline_Show_Width, Textline_Show_Height))

        self.ori_Images_label_textlineView10 = QWidget(self.ori_Images_label_widget)
        self.ori_Images_label_textlineView10.setObjectName("ori_Images_label_textlineView10")
        self.ori_Images_label_textlineView10.setGeometry(
            QRect(25, 5 + 10 * 9 + Textline_Show_Height * 9, Textline_Show_Width, Textline_Show_Height))

        # 添加下方控制栏
        self.bottom_control_bar = QWidget(self.image_area_widget)
        self.bottom_control_bar.setGeometry(QRect(350, 740, 600, 60))
        self.bottom_control_bar.setObjectName("Bottom_Control_Bar")

        # 添加按钮: 上一页
        self.preBtn = QPushButton(self.bottom_control_bar)
        self.preBtn.setGeometry(QRect(30, 10, 70, 40))
        self.preBtn.setObjectName("preBtn")
        self.preBtn.setText("上一页")
        #self.preBtn.clicked.connect(self.choose_pre_Image)
        # 添加按钮: 下一页
        self.nextBtn = QPushButton(self.bottom_control_bar)
        self.nextBtn.setGeometry(QRect(600 - 70 - 30, 10, 70, 40))
        self.nextBtn.setObjectName("nextBtn")
        self.nextBtn.setText("下一页")
        #self.nextBtn.clicked.connect(self.choose_next_Image)
        # 添加当前数量Label
        self.numLabel = QLabel(self.bottom_control_bar)
        self.numLabel.setGeometry(QRect(300 - 30, 0, 100, 60))
        self.numLabel.setObjectName("numLabel")
        # 定位总时长Label
        self.total_time_label = QLabel(self.bottom_control_bar)
        self.total_time_label.setGeometry(QRect(150, 0, 120, 60))
        self.total_time_label.setObjectName("Total_Time_Label")
        # 定位平均时长Label
        self.aver_time_label = QLabel(self.bottom_control_bar)
        self.aver_time_label.setGeometry(QRect(370, 0, 120, 60))
        self.aver_time_label.setObjectName("Aver_Time_Label")


    # 窗口居中
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2 - 50)

    # 刷新识别结果视图
    def update_resultshow_Images(self, qImg):
        self.resultshow_Images = qImg
        self.resImageView.setPixmap(QPixmap.fromImage(self.resultshow_Images[0]))
    # 定位完所有图片
        if len(self.resultshow_Images) == len(self.ori_Images):
            self.locate_end_timer = time.perf_counter()
            # 更新计时Label
            duration = (self.locate_end_timer - self.locate_start_timer) * 1000
            aver_duration = duration / (len(self.ori_Images))
            self.total_time_label.setText("总: %d ms" % duration)
            self.aver_time_label.setText("平均: %d ms" % aver_duration)


# 事件响应
    @pyqtSlot()
    # 选择文件夹
    def choose_Diretory(self):
        # 重置参数
        self.ori_Images = []
        self.locate_start_timer = 0
        self.locate_end_timer = 0
        # 获取文件夹下的所有图片
        dir_path = QFileDialog.getExistingDirectory(self, "getExistingDirectory", fm.get_Curr_Dir())
        fm.get_Images_In_Dir(dir_path, self.ori_Images)
        if len(self.ori_Images) == 0:
            return
        # 修改Start_Flag
        self.start_flag = True
        self.ori_Images_textlineView01.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1
        self.ori_Images_textlineView02.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1
        self.ori_Images_textlineView03.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1
        self.ori_Images_textlineView04.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1
        self.ori_Images_textlineView05.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1
        self.ori_Images_textlineView06.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1
        self.ori_Images_textlineView07.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1
        self.ori_Images_textlineView08.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1
        self.ori_Images_textlineView09.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1
        self.ori_Images_textlineView10.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1
        self.numLabel.setText("1 / %d" % math.ceil((len(self.ori_Images)/10.0)))
        # 开始计时
        self.locate_start_timer = time.perf_counter()
        # 后台线程处理图片
        self.backThread = BackThread(self.ori_Images)
        # 设置回调函数
        self.backThread._signal.connect(self.update_resultshow_widgt)
        # 启动后台线程
        self.backThread.start()

        # 选择上页的10张图片
        def choose_pre_Image(self):
            if self.start_flag and self.curr_Img_Index >= 10:
                self.curr_Img_Index -= 10
                #self.oriImageView.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.ori_Images_textlineView01.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.curr_Img_Index += 1
                self.ori_Images_textlineView02.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.curr_Img_Index += 1
                self.ori_Images_textlineView03.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.curr_Img_Index += 1
                self.ori_Images_textlineView04.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.curr_Img_Index += 1
                self.ori_Images_textlineView05.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.curr_Img_Index += 1
                self.ori_Images_textlineView06.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.curr_Img_Index += 1
                self.ori_Images_textlineView07.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.curr_Img_Index += 1
                self.ori_Images_textlineView08.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.curr_Img_Index += 1
                self.ori_Images_textlineView09.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.curr_Img_Index += 1
                self.ori_Images_textlineView10.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.curr_Img_Index += 1
                self.resImageView.setPixmap(QPixmap.fromImage(self.res_Images[self.curr_Img_Index][6]))
                self.numLabel.setText("%d / %d" % (self.curr_Img_Index + 1, len(self.ori_Images)))


        # 选择下一张图片
        def choose_next_Image(self):
            if self.start_flag and self.curr_Img_Index + 1 < len(self.ori_Images):
                # 初始化定位中间图像的index
                self.index_of_imgs_in_locate = 0
                self.curr_Img_Index += 1
                if self.curr_Img_Index == len(self.ori_Images):
                    self.nextBtn.setEnabled(False)
                self.preBtn.setEnabled(True)
                self.oriImageView.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
                self.resImageView.setPixmap(QPixmap.fromImage(self.res_Images[self.curr_Img_Index][6]))
                self.numLabel.setText("%d / %d" % (self.curr_Img_Index + 1, len(self.ori_Images)))

    # 退出程序
    def exit_application(self):
                sys.exit()

def main():
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()