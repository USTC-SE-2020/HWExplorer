
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

# 后台处理线程: 继承QThread
class BackThread(QThread):
    #  通过类成员对象定义信号对象: object可传任何类型的对象
    _signal = pyqtSignal(object)

    def __init__(self, img_paths):
        super(BackThread, self).__init__()
        self.img_paths = img_paths

    def __del__(self):
        self.wait()

    # 后台线程处理图像
    def run(self):
        locator = TextLineLocator()
        res_imgs_list = []
        for path in self.img_paths:
            # 获取图像生成的所有中间图像
            mat_imgs = locator.locate_textLine_with_cv(path)
            res_imgs_list.append(df.convert_mats_To_QImages(mat_imgs))
            # 主线程刷新一次
            self._signal.emit(res_imgs_list)

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
#Image_Area_Widget {
    background: #CACCC6;
    border-radius: 20px;
}
#Ori_Image_View {
    background: #E6E8DB;
    border-radius: 20px;
}
#Res_Image_View {
    background: #B08B7C;
    border-radius: 20px;
}
#Bottom_Control_Bar {
    background: #F1F4FA;
    border-radius: 20px;
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
#Up_Button {
    background: #04040F;
    color: white;
    font-size: 20px;
    border-radius: 20px;
    
}
#Up_Button:pressed {
    background: #FDD56C;
    color: black;    
}
#Down_Button {
    background: #04040F;
    color: white;
    font-size: 20px;
    border-radius: 20px;
}
#Down_Button:pressed {
    background: #FDD56C;
    color: black;
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
#Add_Button {
    border-radius: 10px;
    background: #04040F;
    font-size: 15px;
    color: white;
}
#Add_Button:pressed {
    background: #FDD56C;
    color: black;
}
"""

# Global Constants
Main_Win_Width = 1500
Main_Win_Height = 1000
Image_Area_Width = 600
Image_Area_Height = 700


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
        self.res_Images = []
        self.locate_start_timer = 0
        self.locate_end_timer = 0
        self.curr_Img_Index = 0
        self.index_of_imgs_in_locate = 0
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
        self.image_area_widget.setGeometry(QRect(60, 100, Image_Area_Width * 2 + 50 + 25 * 2, Image_Area_Height + 120))
        # 添加上切换按钮
        self.up_button = QPushButton(self.image_area_widget)
        self.up_button.setObjectName("Up_Button")
        self.up_button.setGeometry(QRect(25 + Image_Area_Width + 5,250,40,40))
        self.up_button.setText("⬆")
        self.up_button.clicked.connect(self.choose_pre_locate_image)
        # 添加下切换按钮
        self.down_button = QPushButton(self.image_area_widget)
        self.down_button.setObjectName("Down_Button")
        self.down_button.setGeometry(QRect(25 + Image_Area_Width + 5, 400, 40, 40))
        self.down_button.setText("⬇")
        self.down_button.clicked.connect(self.choose_next_locate_image)
        # 添加左侧图片
        self.oriImageView = QLabel(self.image_area_widget)
        self.oriImageView.setGeometry(QRect(25, 25, Image_Area_Width, Image_Area_Height))
        self.oriImageView.setObjectName("Ori_Image_View")
        self.oriImageView.setScaledContents(True)
        # 添加右侧图片
        self.resImageView = QLabel(self.image_area_widget)
        self.resImageView.setGeometry(QRect(25 + Image_Area_Width + 50, 25, Image_Area_Width, Image_Area_Height))
        self.resImageView.setObjectName("Res_Image_View")
        self.resImageView.setScaledContents(True)
        # 添加下方控制栏
        self.bottom_control_bar = QWidget(self.image_area_widget)
        self.bottom_control_bar.setGeometry(QRect(350, 740, 600, 60))
        self.bottom_control_bar.setObjectName("Bottom_Control_Bar")
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

        # 添加按钮: 上一张
        self.preBtn = QPushButton(self.bottom_control_bar)
        self.preBtn.setGeometry(QRect(30, 10, 70, 40))
        self.preBtn.setObjectName("preBtn")
        self.preBtn.setText("上一张")
        self.preBtn.clicked.connect(self.choose_pre_Image)
        # 添加按钮: 下一张
        self.nextBtn = QPushButton(self.bottom_control_bar)
        self.nextBtn.setGeometry(QRect(600 - 70 - 30, 10, 70, 40))
        self.nextBtn.setObjectName("nextBtn")
        self.nextBtn.setText("下一张")
        self.nextBtn.clicked.connect(self.choose_next_Image)

    # 窗口居中
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2 - 50)

    # 刷新识别结果视图
    def update_Res_ImageView(self, qImg):
        self.res_Images = qImg
        if len(self.res_Images) == 1:
            # 定位中间结果数组(共7个): 原图,灰度图,Sobel图,二值化图,闭运算图,轮廓图,结果图
            self.resImageView.setPixmap(QPixmap.fromImage(self.res_Images[0][6]))
        # 定位完所有图片
        if len(self.res_Images) == len(self.ori_Images):
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
        self.oriImageView.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.numLabel.setText("1 / %d" % len(self.ori_Images))
        # 开始计时
        self.locate_start_timer = time.perf_counter()
        # 后台线程处理图片
        self.backThread = BackThread(self.ori_Images)
        # 设置回调函数
        self.backThread._signal.connect(self.update_Res_ImageView)
        # 启动后台线程
        self.backThread.start()

    # 选择上一张图片
    def choose_pre_Image(self):
        if self.start_flag and self.curr_Img_Index - 1 >= 0:
            # 初始化定位中间图像的index
            self.index_of_imgs_in_locate = 0
            self.curr_Img_Index -= 1
            self.oriImageView.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
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

    # 选择定位中间图像的上一张
    def choose_pre_locate_image(self):
        if self.start_flag and self.index_of_imgs_in_locate - 1 >= 0:
            self.index_of_imgs_in_locate -= 1
            self.oriImageView.setPixmap(QPixmap.fromImage(self.res_Images[self.curr_Img_Index][self.index_of_imgs_in_locate]))

    # 选择定位中间图像的下一张
    def choose_next_locate_image(self):
        if self.start_flag and self.index_of_imgs_in_locate + 1 < 6:
            self.index_of_imgs_in_locate += 1
            self.oriImageView.setPixmap(QPixmap.fromImage(self.res_Images[self.curr_Img_Index][self.index_of_imgs_in_locate]))

    # 退出程序
    def exit_application(self):
        sys.exit()
