

# TODO: 定位+识别页面
import time
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QFileDialog
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage

from Tools import FileManager as fm
from GUI.YSLocateBackThread import LocateBackThread
from GUI.YSRecogBackThread import RecogBackThread
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
#Ori_Image_View {
    background: #E6E8DB;
    border-radius: 20px;
}
#Res_Text_View {
    font-size: 20px;
    background: #B08B7C;
    color: white;
    border-radius: 20px;
}
#Bottom_State_Bar {
    background: #F1F4FA;
    border-radius: 20px;
}
#Locate_Time_Label {
    font-size: 15px;
}
#Rec_Time_Label {
    font-size: 15px;
}
"""


class LocateRecognizeView(QWidget):

    def __init__(self, *args, **kwargs):
        super(LocateRecognizeView, self).__init__(*args, **kwargs)
        self.ori_image_path = None                  # 选中的原图像路径
        self.res_image_list = None                  # [(定位出文本行的图像, [文本行图像])]
        self.start_flag = False                     # 当前是否正在定位识别
        self.locate_start_timer = 0                 # 定位计时器起始时间
        self.locate_end_timer = 0                   # 定位计时器结束时间
        self.rec_start_timer = 0                    # 识别计时器起始时间
        self.rec_end_timer = 0                      # 识别计时器结束时间
        self.setStyleSheet(LRStylesheet)            # 初始化GUI样式
        self.initUi()                               # 初始化GUI布局

        self.backThread = None                      # 初始化定位后台线程
        self.recogBackThread = None                 # 初始化识别后台线程

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
        self.choose_img_btn.setText("选择文件")
        self.choose_img_btn.clicked.connect(self.choose_img_file)

        # 中间识别区域
        self.show_area_widget = QWidget(self.content_view)
        self.show_area_widget.setObjectName("Show_Area_Widget")
        self.show_area_widget.setGeometry(QRect(60, 120, Locate_Show_Area_Width * 2 + 50 + 25 * 2, Locate_Show_Area_Height + 120))
        # 左侧图像区域: 显示定位出文本行的图片
        self.ori_image_View = QLabel(self.show_area_widget)
        self.ori_image_View.setGeometry(QRect(25, 25, Locate_Show_Area_Width, Locate_Show_Area_Height))
        self.ori_image_View.setObjectName("Ori_Image_View")
        self.ori_image_View.setScaledContents(True)             # 对图像进行缩放显示
        # 右侧识别文字区域: 显示识别出的文字信息
        self.res_text_View = QLabel(self.show_area_widget)
        self.res_text_View.setGeometry(QRect(25 + Locate_Show_Area_Width + 50, 25, Locate_Show_Area_Width, Locate_Show_Area_Height))
        self.res_text_View.setObjectName("Res_Text_View")
        self.res_text_View.setAlignment(Qt.AlignCenter)         # 文字居中显示
        self.res_text_View.setWordWrap(True)                    # 长文本自动换行, 字符串中用 '\n' 控制换行

        # 下方状态信息栏
        self.bottom_state_bar = QWidget(self.show_area_widget)
        self.bottom_state_bar.setGeometry(QRect(360, 740, 600, 60))
        self.bottom_state_bar.setObjectName("Bottom_State_Bar")
        # 定位总时长Label
        self.locate_time_label = QLabel(self.bottom_state_bar)
        self.locate_time_label.setGeometry(QRect(100, 0, 200, 60))
        self.locate_time_label.setObjectName("Locate_Time_Label")
        # 定位平均时长Label
        self.rec_time_label = QLabel(self.bottom_state_bar)
        self.rec_time_label.setGeometry(QRect(350, 0, 200, 60))
        self.rec_time_label.setObjectName("Rec_Time_Label")


    # 事件响应
    @pyqtSlot()
    # 选择单个图像文件
    def choose_img_file(self):
        # 重置参数
        self.ori_image_path = None
        self.res_image_list = None
        self.locate_start_timer = 0
        self.locate_end_timer = 0
        self.rec_start_timer = 0
        self.rec_end_timer = 0
        # 获取图像路径: 支持的图像类型(jpg, png)
        file_path, file_type = QFileDialog.getOpenFileName(self, "选取文件", fm.get_Curr_Dir(), "Images (*.jpg *.png)")
        if file_path == "":  # 取消选择
            return
        self.start_flag = True                                      # 开始处理, 修改Start_Flag
        self.ori_image_path = file_path
        self.ori_image_View.setPixmap(QPixmap(file_path))           # 先显示原图像
        self.locate_start_timer = time.perf_counter()               # 定位计时器开始计时
        self.backThread = LocateBackThread([self.ori_image_path])   # 初始化后台线程处理图片
        self.backThread._signal.connect(self.update_Res_ImageView)  # 设置后台线程回调函数
        self.backThread.start()                                     # 启动后台线程

    # 刷新定位结果视图
    def update_Res_ImageView(self, qImg):
        self.res_image_list = qImg                                                       # [(定位出文本行的图像, [文本行图像])]
        self.ori_image_View.setPixmap(QPixmap.fromImage(self.res_image_list[0][0]))      # 结果数组中只有一个元素
        self.locate_end_timer = time.perf_counter()                                      # 定位计时器结束计时
        duration = (self.locate_end_timer - self.locate_start_timer) * 1000              # 更新计时Label
        self.locate_time_label.setText("定位时长:{:.2f} ms".format(duration))

        # 识别定位出的文本行
        self.rec_start_timer = time.perf_counter()                            # 识别计时器开始计时
        self.recogBackThread = RecogBackThread([self.res_image_list[0][1]])   # 初始化一个新的后台线程处理图片
        self.recogBackThread._signal.connect(self.update_texts_in_textView)   # 设置后台线程回调函数
        self.recogBackThread.start()                                          # 启动后台线程

    # 更新识别出的文字信息, texts: [str1,str2,...]
    def update_texts_in_textView(self, texts):
        self.rec_end_timer = time.perf_counter()                              # 识别计时器结束计时
        duration = (self.rec_end_timer - self.rec_start_timer) * 1000         # 更新计时Label
        self.rec_time_label.setText("识别时长: {:.2f} ms".format(duration))
        texts = texts[0][::-1]                                                # 调整顺序 [str1,str2...] --> [strN,...,str1]
        res_str = ""
        for text in texts:
            text += '\n'
            res_str += text
        self.res_text_View.setText(res_str)