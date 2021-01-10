

from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QFileDialog
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, pyqtSlot
from PyQt5.QtGui import QPixmap
from Tools import FileManager as fm
from GUI.YSRecogBackThread import RecogBackThread
from GUI.config import *
import time

# 样式表
LRViewStylesheet = """
#Content_View {
    background: #F1F4FA;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
}
#Top_State_Bar {
    background: #CACCC6;
    border-top-right-radius: 20px;
}
#Choose_Dir_Btn {
    border-radius: 10px;
    background: #04040F;
    font-size: 15px;
    color: white;
}
#Choose_Dir_Btn:pressed {
    background: #FDD56C;
    color: black;
}
#Show_Area_Widget {
    background: #CACCC6;
    border-radius: 20px;
}
#Top_Image_View {
    background: #E6E8DB;
    border-radius: 20px;
}
#Bottom_Text_Label {
    background: #B08B7C;
    border-radius: 20px;
    font-size: 20px;
}
#Bottom_Control_Bar {
    background: #F1F4FA;
    border-radius: 20px;
}
#Num_Label {
    font-size: 25px;
}
#Total_Time_Label {
    font-size: 12px;
}
#Aver_Time_Label {
    font-size: 12px;
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
"""


# TODO: 文本行识别页面
class LineRecognizeView(QWidget):

    def __init__(self, *args, **kwargs):
        super(LineRecognizeView, self).__init__(*args, **kwargs)
        self.line_img_paths = []                    # 文本行图像路径, [path1, path2,...]
        self.res_texts = []                         # 文本行识别结果, [str1, str2,...]
        self.rec_start_timer = 0                    # 识别定时器起始时间
        self.rec_end_timer = 0                      # 识别定时器结束时间
        self.curr_img_index = 0                     # 当前选中的图像下标
        self.start_flag = False                     # 当前是否已经识别
        self.setStyleSheet(LRViewStylesheet)        # 初始化GUI样式
        self.initUi()                               # 初始化GUI布局

        self.recogBackThread = None                 # 识别后台线程

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
        # 顶部状态栏按钮: 选择文件夹
        self.choose_dir_btn = QPushButton(self.top_state_bar)
        self.choose_dir_btn.setGeometry(QRect(Top_State_Bar_Width / 2 - 50, 10, 100, 60))
        self.choose_dir_btn.setObjectName("Choose_Dir_Btn")
        self.choose_dir_btn.setText("选择文件夹")
        self.choose_dir_btn.clicked.connect(self.choose_diretory)

        # 中间识别区域
        self.show_area_widget = QWidget(self.content_view)
        self.show_area_widget.setObjectName("Show_Area_Widget")
        self.show_area_widget.setGeometry(QRect(60, 120, Locate_Show_Area_Width * 2 + 50 + 25 * 2, Locate_Show_Area_Height + 120))
        # 上方图像label
        self.top_image_view = QLabel(self.show_area_widget)
        self.top_image_view.setGeometry(QRect(150, 220, 1000, 100))
        self.top_image_view.setObjectName("Top_Image_View")
        self.top_image_view.setScaledContents(True)  # 对图像进行缩放显示
        # 下方识别文字label
        self.bottom_text_label = QLabel(self.show_area_widget)
        self.bottom_text_label.setGeometry(QRect(150, 350, 1000, 100))
        self.bottom_text_label.setObjectName("Bottom_Text_Label")
        self.bottom_text_label.setAlignment(Qt.AlignCenter)

        # 添加下方控制栏
        self.bottom_control_bar = QWidget(self.show_area_widget)
        self.bottom_control_bar.setGeometry(QRect(350, 740, 600, 60))
        self.bottom_control_bar.setObjectName("Bottom_Control_Bar")

        # AR Label
        self.ar_label = QLabel(self.bottom_control_bar)
        self.ar_label.setGeometry(QRect(200, 0, 200, 60))
        self.ar_label.setAlignment(Qt.AlignCenter)
        self.ar_label.setObjectName("AR_Label")

        # 添加当前数量Label
        self.num_label = QLabel(self.bottom_control_bar)
        self.num_label.setGeometry(QRect(200, 0, 200, 60))
        self.num_label.setAlignment(Qt.AlignCenter)
        self.num_label.setObjectName("Num_Label")

        # CR Label
        self.cr_label = QLabel(self.bottom_control_bar)
        self.cr_label.setGeometry(QRect(200, 0, 200, 60))
        self.cr_label.setAlignment(Qt.AlignCenter)
        self.cr_label.setObjectName("CR_Label")

        # 按钮: 上一张
        self.preBtn = QPushButton(self.bottom_control_bar)
        self.preBtn.setGeometry(QRect(30, 10, 70, 40))
        self.preBtn.setObjectName("preBtn")
        self.preBtn.setText("上一张")
        self.preBtn.clicked.connect(self.choose_pre_Image)
        # 按钮: 下一张
        self.nextBtn = QPushButton(self.bottom_control_bar)
        self.nextBtn.setGeometry(QRect(600 - 70 - 30, 10, 70, 40))
        self.nextBtn.setObjectName("nextBtn")
        self.nextBtn.setText("下一张")
        self.nextBtn.clicked.connect(self.choose_next_Image)

    # 事件响应
    @pyqtSlot()
    # 选择上一张图像
    def choose_pre_Image(self):
        if self.start_flag and self.curr_img_index - 1 >= 0:
            self.curr_img_index -= 1
            self.top_image_view.setPixmap(QPixmap(self.line_img_paths[self.curr_img_index]))                # 更新文本行图像
            self.bottom_text_label.setText(self.res_texts[self.curr_img_index][0])                          # 更新对应的识别文字
            self.num_label.setText("{} / {}".format(self.curr_img_index + 1, len(self.line_img_paths)))     # 更新当前位置

    # 选择下一张图像
    def choose_next_Image(self):
        if self.start_flag and self.curr_img_index + 1 < len(self.line_img_paths) and self.curr_img_index + 1 < len(self.res_texts):
            self.curr_img_index += 1
            self.top_image_view.setPixmap(QPixmap(self.line_img_paths[self.curr_img_index]))                # 更新文本行图像
            self.bottom_text_label.setText(self.res_texts[self.curr_img_index][0])                          # 更新对应的识别文字
            self.num_label.setText("{} / {}".format(self.curr_img_index + 1, len(self.line_img_paths)))     # 更新当前位置

    # 选择文件夹
    def choose_diretory(self):
        # 重置参数
        self.line_img_paths = []
        self.res_texts = []
        self.rec_start_timer = 0
        self.rec_end_timer = 0
        self.curr_img_index = 0
        self.start_flag = False

        dir_path = QFileDialog.getExistingDirectory(self, "getExistingDirectory", fm.get_Curr_Dir())
        fm.get_Images_In_Dir(dir_path, self.line_img_paths)         # 获取文件夹下的所有图片路径
        if len(self.line_img_paths) == 0:
            print("文件夹为空!")
            return

        self.start_flag = True                                                              # 置为开始状态, 修改Start_Flag
        self.top_image_view.setPixmap(QPixmap(self.line_img_paths[self.curr_img_index]))    # 初始时设置原图像
        self.num_label.setText("1 / {}".format(len(self.line_img_paths)))                   # 更新数量下标
        self.rec_start_timer = time.perf_counter()                                          # 开始计时
        self.recogBackThread = RecogBackThread(self.line_img_paths, type="path")            # 初始化识别后台进程
        self.recogBackThread._signal.connect(self.update_texts_in_textView)                 # 设置回调函数
        self.recogBackThread.start()                                                        # 启动后台线程

    # 回调函数: 更新识别结果数组
    def update_texts_in_textView(self, texts):
        self.res_texts = texts
        if len(self.res_texts) == 1:
            self.bottom_text_label.setText(self.res_texts[0][0])

