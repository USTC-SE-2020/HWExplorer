
import os
import time
import difflib
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QFileDialog
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, pyqtSlot, QUrl
from PyQt5.QtGui import QPixmap, QImage
from GUI.config import *
from Tools import FileManager as fm
from GUI.YSLocateBackThread import LocateBackThread
from GUI.YSRecogBackThread import RecogBackThread
from GUI.YSDBNetThread import DBNetBackThread
from GUI.YSPaintTextView import PaintTextView
from GUI.YSSwitchButton import SwitchButton
from Tools.DataFormatter import calculate_ar_cr

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
#Mid_Circle_Area {
    background: red;
    border-radius: 25px;
}
#Mid_Zoom_Btn {
    background: white;
    border-radius: 20px;
}
#Mid_Zoom_Btn:pressed {
    background: #FDD56C;
    border-radius: 20px;
}
#Full_Size_Content_Widget {
    background: #CACCC6;
    border-radius: 20px;
}
#Exit_Full_Button {
    background: #FDD56C;
    color: black;
    border-radius: 10px;
    font-size: 16px;
}
#Exit_Full_Button:pressed {
    background: black;
    color: white;
    border-radius: 10px;
    font-size: 16px;
}
#Show_Area_Widget {
    background: #CACCC6;
    border-radius: 20px;
}
#Diff_Web_View {
    border-radius: 20px;
}
#Ori_Image_View {
    background: #B08B7C;
    border-radius: 20px;
}
#Text_Area_Widget {
    font-size: 15px;
    background: #E6E8DB;
    color: black;
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
#Sim_Ratio_Label {
    font-size: 15px;
}
#Switch_Label {
    font-size: 15px;
}
#AR_Label {
    font-size: 15px;
}
#CR_Label {
    font-size: 15px;
}
"""

# TODO: 定位+识别页面
class LocateRecognizeView(QWidget):

    def __init__(self, *args, **kwargs):
        super(LocateRecognizeView, self).__init__(*args, **kwargs)
        self.ori_image_path = None                  # 选中的原图像路径
        self.ori_label_list = []                    # 选中图像对应的文本信息, 若没有则为空
        self.res_image_list = None                  # [(定位出文本行的图像, [文本行图像])]
        self.start_flag = False                     # 当前是否正在定位识别
        self.show_diff_flag = False                 # 是否显示对比结果视图,默认为False(选中图像无对应txt文件)
        self.locate_start_timer = 0                 # 定位计时器起始时间
        self.locate_end_timer = 0                   # 定位计时器结束时间
        self.rec_start_timer = 0                    # 识别计时器起始时间
        self.rec_end_timer = 0                      # 识别计时器结束时间
        self.setStyleSheet(LRStylesheet)            # 初始化GUI样式
        self.initUi()                               # 初始化GUI布局

        self.texts_rect = []                        # 文本行图像位置

        self.dbnetThread = None                     # 初始化DBNet定位后台线程
        self.backThread = None                      # 初始化形态学定位后台线程
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

        # 启用DBNet按钮
        self.switch_button = SwitchButton(self.content_view)
        self.switch_button.setGeometry(QRect(680, 90, 70, 30))
        self.switch_button.setObjectName("Switch_Button")
        self.switch_label = QLabel(self.content_view)
        self.switch_label.setObjectName("Switch_Label")
        self.switch_label.setGeometry(QRect(665, 120, 100, 30))
        self.switch_label.setAlignment(Qt.AlignCenter)
        self.switch_label.setText("启用DBNet")

        # 全尺寸背景视图
        self.full_size_content_widget = QWidget(self.content_view)
        self.full_size_content_widget.setObjectName("Full_Size_Content_Widget")
        self.full_size_content_widget.setGeometry(QRect(60, 150, Locate_Show_Area_Width * 2 + 50 + 25 * 2, Locate_Show_Area_Height + 120))
        # 全尺寸webview
        self.full_size_web_view = QWebEngineView(self.full_size_content_widget)
        self.full_size_web_view.setObjectName("Full_Size_Web_View")
        self.full_size_web_view.setGeometry(QRect(20, 20, Locate_Show_Area_Width * 2 + 50 + 10, Locate_Show_Area_Height + 30))
        self.full_size_web_view.setHidden(True)  # 默认隐藏
        # 退出全尺寸按钮
        self.exit_full_button = QPushButton(self.full_size_content_widget)
        self.exit_full_button.setObjectName("Exit_Full_Button")
        self.exit_full_button.setGeometry(QRect(590, 765, 100, 40))
        self.exit_full_button.setText("退出")
        self.exit_full_button.clicked.connect(self.exit_full_size_view_mode)

        # 中间识别区域
        self.show_area_widget = QWidget(self.content_view)
        self.show_area_widget.setObjectName("Show_Area_Widget")
        self.show_area_widget.setGeometry(QRect(60, 150, Locate_Show_Area_Width * 2 + 50 + 25 * 2, Locate_Show_Area_Height + 120))

        # 左侧图像区域: 显示定位出文本行的图片
        self.ori_image_View = QLabel(self.show_area_widget)
        self.ori_image_View.setGeometry(QRect(25, 25, Locate_Show_Area_Width, Locate_Show_Area_Height))
        self.ori_image_View.setObjectName("Ori_Image_View")
        self.ori_image_View.setScaledContents(True)             # 对图像进行缩放显示
        # 中间放大按钮区域
        self.mid_circle_area = QLabel(self.show_area_widget)
        self.mid_circle_area.setObjectName("Mid_Circle_Area")
        self.mid_circle_area.setGeometry(QRect(Locate_Show_Area_Width+25, 320, 50, 50))
        self.mid_circle_area.setHidden(True)                # 默认隐藏, 显示对比视图时再显示
        # 放大按钮
        self.mid_zoom_btn = QPushButton(self.mid_circle_area)
        self.mid_zoom_btn.setObjectName("Mid_Zoom_Btn")
        self.mid_zoom_btn.setGeometry(QRect(5, 5, 40, 40))
        self.mid_zoom_btn.clicked.connect(self.show_full_size_view)

        # 右侧识别文字区域
        self.text_area_widget = QLabel(self.show_area_widget)
        self.text_area_widget.setGeometry(QRect(25 + Locate_Show_Area_Width + 50, 25, Locate_Show_Area_Width, Locate_Show_Area_Height))
        self.text_area_widget.setObjectName("Text_Area_Widget")
        # 自定义textview: 无对应标签时展示
        self.res_text_view = PaintTextView(self.text_area_widget)
        self.res_text_view.setGeometry(QRect(20, 20, Locate_Show_Area_Width - 20 * 2, Locate_Show_Area_Height - 20 * 2))
        self.res_text_view.setObjectName("Res_Text_View")
        # web界面: 有对应标签时展示
        self.diff_web_view = QWebEngineView(self.text_area_widget)
        self.diff_web_view.setObjectName("Diff_Web_View")
        self.diff_web_view.setGeometry(QRect(20, 20, Locate_Show_Area_Width - 20 * 2, Locate_Show_Area_Height - 20 * 2))
        self.diff_web_view.setHidden(True)              # 默认隐藏
        self.diff_web_view.setZoomFactor(0.70)          # 缩放

        # 下方状态信息栏
        self.bottom_state_bar = QWidget(self.show_area_widget)
        self.bottom_state_bar.setGeometry(QRect(250, 740, 800, 60))
        self.bottom_state_bar.setObjectName("Bottom_State_Bar")
        # 定位总时长Label
        self.locate_time_label = QLabel(self.bottom_state_bar)
        self.locate_time_label.setGeometry(QRect(20, 20, 200, 20))
        self.locate_time_label.setObjectName("Locate_Time_Label")
        self.locate_time_label.setAlignment(Qt.AlignLeft)
        # AR label
        self.ar_label = QLabel(self.bottom_state_bar)
        self.ar_label.setGeometry(QRect(260, 20, 100, 20))
        self.ar_label.setObjectName("AR_Label")
        self.ar_label.setAlignment(Qt.AlignLeft)
        # 相似度Label
        self.sim_ratio_label = QLabel(self.bottom_state_bar)
        self.sim_ratio_label.setGeometry(QRect(360, 20, 100, 20))
        self.sim_ratio_label.setObjectName("Sim_Ratio_Label")
        self.sim_ratio_label.setAlignment(Qt.AlignCenter)
        # CR label
        self.cr_label = QLabel(self.bottom_state_bar)
        self.cr_label.setGeometry(QRect(500, 20, 100, 20))
        self.cr_label.setObjectName("CR_Label")
        self.cr_label.setAlignment(Qt.AlignLeft)
        # 识别总时长Label
        self.rec_time_label = QLabel(self.bottom_state_bar)
        self.rec_time_label.setGeometry(QRect(560, 20, 200, 20))
        self.rec_time_label.setObjectName("Rec_Time_Label")
        self.rec_time_label.setAlignment(Qt.AlignRight)


    # 事件响应
    @pyqtSlot()
    # 选择单个图像文件
    def choose_img_file(self):
        if self.start_flag:                 # 正在处理中，则不再响应
            return

        # 获取图像路径: 支持的图像类型(jpg, png)
        file_path, file_type = QFileDialog.getOpenFileName(self, "选取文件", fm.get_Curr_Dir(), "Images (*.jpg *.png)")
        if file_path == "":  # 取消选择
            return

        # 重置参数
        self.show_diff_flag = False
        self.ori_image_path = None
        self.ori_label_list = []
        self.res_image_list = None
        self.locate_start_timer = 0
        self.locate_end_timer = 0
        self.rec_start_timer = 0
        self.rec_end_timer = 0
        self.backThread = None
        self.dbnetThread = None
        self.exit_full_size_view_mode()
        self.mid_circle_area.setHidden(True)                                # 默认隐藏放大按钮区域
        self.res_text_view.clear_text_for_update()                          # 清除上次显示的残留信息
        self.diff_web_view.load(QUrl(""))                                   # 清除上次显示的残留信息

        txt_file_path = file_path.split('.')[0] + ".txt"                    # 查找与选择图像同名的txt文件
        if os.path.exists(txt_file_path):                                   # 图像有对应的标签txt文件
            self.res_text_view.setHidden(True)                              # 隐藏自定义textview
            self.diff_web_view.setHidden(False)                             # 显示对比视图
            self.show_diff_flag = True                                      # 修改对比视图显示标志, 也即存在标签标志

            with open(txt_file_path, 'r', encoding='gbk') as f:             # gbk格式打开
                texts = f.readlines()
                for line in texts:
                    self.ori_label_list.append(line.strip('\n'))
            f.close()
        else:                                                               # 图像没有对应的标签txt文件
            self.res_text_view.setHidden(False)                             # 显示自定义textview
            self.diff_web_view.setHidden(True)                              # 隐藏对比视图
            self.show_diff_flag = False                                     # 修改对比视图显示标志

        self.start_flag = True                                              # 开始处理, 修改Start_Flag
        self.ori_image_path = file_path
        self.ori_image_View.setPixmap(QPixmap(file_path))                   # 先显示原图像
        self.locate_start_timer = time.perf_counter()                       # 定位计时器开始计时

        self.locate_time_label.setText("DBNet定位中,请等待...")
        self.rec_time_label.setText("")                                     # 状态栏label置空
        self.sim_ratio_label.setText("")
        self.ar_label.setText("")
        self.cr_label.setText("")

        if self.switch_button.state:                                        # True, 启用DBNet
            print("启用DBNet")
            self.dbnetThread = DBNetBackThread(self.ori_image_path)         # 初始化 DBNet 后台线程处理图片
            self.dbnetThread._signal.connect(self.update_dbnet_res_img)     # 设置 DBNet 后台线程回调函数
            self.dbnetThread.start()                                        # 启动DBNet后台线程
        else:                                                               # False, 启用形态学
            print("启用形态学")
            self.backThread = LocateBackThread([self.ori_image_path])       # 初始化 形态学 后台线程处理图片
            self.backThread._signal.connect(self.update_Res_ImageView)      # 设置 形态学 后台线程回调函数
            self.backThread.start()                                         # 启动形态学后台线程

    # 更新 DBNet 定位结果视图, qImg:(定位出文本行的图像, [文本行图像], [文本行图像位置])
    def update_dbnet_res_img(self, qImg):
        self.ori_image_View.setPixmap(QPixmap.fromImage(qImg[0]))                        # 更新定位出文本行的图像
        self.texts_rect = qImg[2]                                                        # 保存文本行图像位置
        self.locate_end_timer = time.perf_counter()                                      # 定位计时器结束计时
        duration = (self.locate_end_timer - self.locate_start_timer) * 1000              # 更新计时Label
        self.locate_time_label.setText("DBNet 定位时长: {:.2f} ms".format(duration))
        self.rec_time_label.setText("CRNN识别中,请等待...")

        # 识别定位出的文本行
        self.rec_start_timer = time.perf_counter()                                      # 识别计时器开始计时
        self.recogBackThread = RecogBackThread([qImg[1]])                               # 初始化识别后台线程处理图片
        self.recogBackThread._signal.connect(self.update_texts_in_textView)             # 设置后台线程回调函数
        self.recogBackThread.start()                                                    # 启动后台线程


    # 刷新形态学定位结果视图
    def update_Res_ImageView(self, qImg):
        self.res_image_list = qImg                                                       # [(定位出文本行的图像, [文本行图像], [文本行图像位置])]
        self.ori_image_View.setPixmap(QPixmap.fromImage(self.res_image_list[0][0]))      # 结果数组中只有一个元素(只选择一张图片定位)
        self.texts_rect = self.res_image_list[0][2]                                      # 保存文本行图像位置
        self.locate_end_timer = time.perf_counter()                                      # 定位计时器结束计时
        duration = (self.locate_end_timer - self.locate_start_timer) * 1000              # 更新计时Label
        self.locate_time_label.setText("形态学 定位时长: {:.2f} ms".format(duration))

        # 识别定位出的文本行
        self.rec_start_timer = time.perf_counter()                            # 识别计时器开始计时
        self.recogBackThread = RecogBackThread([self.res_image_list[0][1]])   # 初始化一个新的后台线程处理图片
        self.recogBackThread._signal.connect(self.update_texts_in_textView)   # 设置后台线程回调函数
        self.recogBackThread.start()                                          # 启动后台线程

    # 更新识别出的文字信息, texts: [[str1,str2,...], [str1, str2, ....]]
    def update_texts_in_textView(self, texts):
        self.start_flag = False                                               # 定位识别完成,修改当前状态
        self.rec_end_timer = time.perf_counter()                              # 识别计时器结束计时
        duration = (self.rec_end_timer - self.rec_start_timer) * 1000         # 更新计时Label
        self.rec_time_label.setText("识别时长: {:.2f} ms".format(duration))

        self.sim_ratio_label.setText("相似度计算中,请等待...")
        if self.show_diff_flag:                                                                         # 显示对比视图
            self.mid_circle_area.setHidden(False)                                                       # 显示放大按钮区域
            diff = difflib.HtmlDiff().make_file(self.ori_label_list, texts[0])                          #
            save_path = "/Users/soyou/Documents/EProjects/HWExplorer/diff.html"
            outfile = open(save_path, 'w')                                                              # TODO: 绝对路径修改
            outfile.write(diff)                                                                         # 保存html文件
            outfile.close()
            self.diff_web_view.load(QUrl.fromLocalFile(save_path))                                      # 显示对比视图
            seq = difflib.SequenceMatcher(None, '.'.join(self.ori_label_list), '.'.join(texts[0]))
            ratio = seq.ratio()
            self.sim_ratio_label.setText("相似度: {:.3f}".format(ratio))                                 # 设置文本相似度

            num, ar_num, cr_num = calculate_ar_cr('.'.join(self.ori_label_list), '.'.join(texts[0]))
            self.ar_label.setText("AR: {:.2f}".format(ar_num/num))                                      # 计算AR
            self.cr_label.setText("CR: {:.2f}".format(cr_num/num))                                      # 计算CR

        else:                                                                                           # 隐藏对比视图
            self.sim_ratio_label.setText(" ")                                                           # 文本相似度置空
            self.res_text_view.redraw_text_in_view(texts[0], self.texts_rect)                           # 自定义textview绘制文字信息

    # 显示全尺寸视图
    def show_full_size_view(self):
        self.show_area_widget.setHidden(True)
        self.full_size_web_view.setHidden(False)
        # TODO:  使用项目内相对路径
        self.full_size_web_view.load(QUrl.fromLocalFile("/Users/soyou/Documents/EProjects/HWExplorer/diff.html"))

    # 退出全尺寸视图模式
    def exit_full_size_view_mode(self):
        self.show_area_widget.setHidden(False)
        self.full_size_web_view.setHidden(True)


