
import time
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QFileDialog
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage

from Tools import FileManager as fm
from GUI.YSLocateBackThread import LocateBackThread
from GUI.YSDBNetThread import DBNetBackThread
from GUI.config import *

# 样式表
LRStylesheet = """
#Content_View {
    background: #F1F4FA;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
}
#Top_State_Bar {
    background: #CACCC6;
    border-top-right-radius: 20px;
}
#Choose_Img_Btn {
    border-radius: 10px;
    background: #04040F;
    font-size: 15px;
    color: white;
}
#Choose_Img_Btn:pressed {
    background: #FDD56C;
    color: black;
}
#Show_Area_Widget {
    background: #CACCC6;
    border-radius: 20px;
}
#Dbnet_Label {
    font-size: 20px;
    color: red;
}
#Dbnet_Image_View {
    background: #B08B7C;
    border-radius: 20px;
}
#Morph_Label {
    font-size: 20px;
    color: red;
}
#Morph_Image_View {
    font-size: 15px;
    background: #E6E8DB;
    color: black;
    border-radius: 20px;
}
#Dbnet_Bottom_State_Bar {
    background: #F1F4FA;
    border-radius: 20px;
}
#Dbnet_Time_Label {
    font-size: 15px;
}
#Morph_Bottom_State_Bar {
    background: #F1F4FA;
    border-radius: 20px;
}
#Morph_Time_Label {
    font-size: 15px;
}
"""


# TODO: 定位方式比较页面
class CompareLocateView(QWidget):
    def __init__(self, *args, **kwargs):
        super(CompareLocateView, self).__init__(*args, **kwargs)

        self.ori_image_path = None                  # 选中的原图像路径
        self.dbnet_res_img = None                   # DBNet定位后的图像
        self.morph_res_img = None                   # 形态学定位后的图像
        self.start_flag = False                     # 当前是否正在定位识别, 避免多次响应
        self.morph_finished = False                 # 开始定位识别后, 形态学定位是否完成
        self.dbnet_finished = False                 # 开始定位识别后, dbnet定位是否完成

        self.dbnet_start_timer = 0                  # DBNet计时器起始时间
        self.dbnet_end_timer = 0                    # DBNet计时器结束时间
        self.morph_start_timer = 0                  # 形态学计时器起始时间
        self.morph_end_timer = 0                    # 形态许计时器结束时间

        self.dbnet_thread = None                    # DBNet定位后台线程
        self.morph_thread = None                    # 形态学定位后台线程

        self.setStyleSheet(LRStylesheet)            # 初始化GUI样式
        self.initUi()                               # 初始化GUI布局

    # 界面布局
    def initUi(self):

        # 内容视图, 管理所有的子视图
        self.content_view = QWidget(self)
        self.content_view.setObjectName("Content_View")
        self.content_view.setGeometry(QRect(0, 0, Sub_Win_Width, Sub_Win_Height))

        # 顶部状态栏
        self.top_state_bar = QWidget(self.content_view)
        self.top_state_bar.setObjectName("Top_State_Bar")
        self.top_state_bar.setGeometry(QRect(0, 0, Top_State_Bar_Width, Top_State_Bar_Height))
        # 选择文件按钮:
        self.choose_img_btn = QPushButton(self.top_state_bar)
        self.choose_img_btn.setGeometry(QRect(Top_State_Bar_Width / 2 - 50, 10, 100, 60))
        self.choose_img_btn.setObjectName("Choose_Img_Btn")
        self.choose_img_btn.setText("选择图片")
        self.choose_img_btn.clicked.connect(self.choose_img_file)

        # 中间识别区域
        self.show_area_widget = QWidget(self.content_view)
        self.show_area_widget.setObjectName("Show_Area_Widget")
        self.show_area_widget.setGeometry(QRect(60, 120, Locate_Show_Area_Width * 2 + 50 + 25 * 2, Locate_Show_Area_Height + 120))
        # 左侧 DBNET 定位区域
        self.dbnet_label  = QLabel(self.show_area_widget)
        self.dbnet_label.setObjectName("Dbnet_Label")
        self.dbnet_label.setGeometry(QRect(270, 5, 100, 50))
        self.dbnet_label.setText("DBNet")
        self.dbnet_image_View = QLabel(self.show_area_widget)
        self.dbnet_image_View.setGeometry(QRect(25, 50, Locate_Show_Area_Width, Locate_Show_Area_Height))
        self.dbnet_image_View.setObjectName("Dbnet_Image_View")
        self.dbnet_image_View.setScaledContents(True)             # 对图像进行缩放显示
        # 右侧 形态学 定位区域
        self.morph_label  = QLabel(self.show_area_widget)
        self.morph_label.setObjectName("Morph_Label")
        self.morph_label.setGeometry(QRect(950, 5, 100, 50))
        self.morph_label.setText("形态学")
        self.morph_image_view = QLabel(self.show_area_widget)
        self.morph_image_view.setGeometry(QRect(25 + Locate_Show_Area_Width + 50, 50, Locate_Show_Area_Width, Locate_Show_Area_Height))
        self.morph_image_view.setObjectName("Morph_Image_View")
        self.morph_image_view.setScaledContents(True)  # 对图像进行缩放显示

        # 下方 DBNET 状态信息栏
        self.dbnet_bottom_state_bar = QWidget(self.show_area_widget)
        self.dbnet_bottom_state_bar.setGeometry(QRect(160, 760, 350, 50))
        self.dbnet_bottom_state_bar.setObjectName("Dbnet_Bottom_State_Bar")
        # 定位总时长Label
        self.dbnet_time_label = QLabel(self.dbnet_bottom_state_bar)
        self.dbnet_time_label.setGeometry(QRect(10, 0, 300, 50))
        self.dbnet_time_label.setAlignment(Qt.AlignCenter)
        self.dbnet_time_label.setObjectName("Dbnet_Time_Label")
        self.dbnet_time_label.setText("DBNet 定位时长: XXXms")

        # 下方 形态学 状态信息栏
        self.morph_bottom_state_bar = QWidget(self.show_area_widget)
        self.morph_bottom_state_bar.setGeometry(QRect(840, 760, 350, 50))
        self.morph_bottom_state_bar.setObjectName("Morph_Bottom_State_Bar")
        # 定位总时长Label
        self.morph_time_label = QLabel(self.morph_bottom_state_bar)
        self.morph_time_label.setGeometry(QRect(100, 0, 200, 50))
        self.morph_time_label.setObjectName("Morph_Time_Label")
        self.morph_time_label.setText("形态学 定位时长: XXXms")

    # 事件响应
    @pyqtSlot()
    # 选择单个图像文件
    def choose_img_file(self):
        if self.start_flag == True:  # 正在处理中
            if not self.morph_finished or not self.dbnet_finished:  # 形态学定位/dbnet定位, 有未完成的则不再响应
                return
        # 重置参数
        self.ori_image_path = None
        self.dbnet_res_img = None
        self.morph_res_img = None
        self.start_flag = False
        self.dbnet_start_timer = 0
        self.dbnet_end_timer = 0
        self.morph_start_timer = 0
        self.morph_end_timer = 0
        self.morph_thread = None
        self.dbnet_thread = None
        self.morph_finished = False
        self.dbnet_finished = False
        # 获取图像路径: 支持的图像类型(jpg, png)
        file_path, file_type = QFileDialog.getOpenFileName(self, "选取文件", fm.get_Curr_Dir(), "Images (*.jpg *.png)")
        if file_path == "":  # 取消选择
            return
        self.start_flag = True                                          # 开始处理, 修改Start_Flag
        self.ori_image_path = file_path
        self.morph_image_view.setPixmap(QPixmap(file_path))             # 先显示原图像
        self.morph_start_timer = time.perf_counter()                    # 形态学定位计时器开始计时
        self.morph_thread = LocateBackThread([self.ori_image_path])     # 初始化形态学定位后台线程处理图片
        self.morph_thread._signal.connect(self.update_morph_view)       # 设置后台线程回调函数
        self.morph_thread.start()                                       # 启动后台线程

        self.dbnet_image_View.setPixmap(QPixmap(file_path))             # 先显示原图像
        self.dbnet_start_timer = time.perf_counter()                    # DBNet定位计时器开始计时
        self.dbnet_thread = DBNetBackThread(self.ori_image_path)        # 初始化DBNet定位后台线程处理图片
        self.dbnet_thread._signal.connect(self.update_dbnet_view)       # 设置后台线程回调函数
        self.dbnet_thread.start()                                       # 启动后台线程

    # 刷新 形态学定位 结果视图, qImg: [(定位出文本行的图像, [文本行图像], [文本行图像位置])]
    def update_morph_view(self, qImg):
        self.morph_image_view.setPixmap(QPixmap.fromImage(qImg[0][0]))                   # 结果数组中只有一个元素(只选择一张图片定位)
        self.morph_end_timer = time.perf_counter()                                       # 形态学定位计时器结束计时
        duration = (self.morph_end_timer - self.morph_start_timer) * 1000                # 更新计时Label
        self.morph_time_label.setText("形态学 定位时长: {:.3f} ms".format(duration))
        self.morph_finished = True                                                       # 形态学定位已完成

    # 刷新 DBNet定位 结果视图, qImg: (定位出文本行的图像, [文本行图像], [文本行图像位置])
    def update_dbnet_view(self, qImg):
        res_img = qImg[0]
        self.dbnet_image_View.setPixmap(QPixmap.fromImage(res_img))                      # qImg已转换成QImage格式
        self.dbnet_end_timer = time.perf_counter()                                       # 定位计时器结束计时
        duration = (self.dbnet_end_timer - self.dbnet_start_timer) * 1000                # 更新计时Label
        self.dbnet_time_label.setText("DBNet 定位时长: {:.3f} ms".format(duration))
        self.dbnet_finished = True                                                       # dbnet定位已完成

