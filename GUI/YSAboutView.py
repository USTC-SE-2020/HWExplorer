

# TODO: 关于页面
import time
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QFileDialog
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage

from Tools import FileManager as fm
from GUI.config import *

AboutStyleSheet = """
#Content_View {
    background: #F1F4FA;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
}
#Show_Area_Widget {
    background: #CACCC6;
    border-radius: 30px;
}
#Detail_Area_Widget {
    background: #B08B7C;
    border-radius: 20px;
}
#Logo_Label {
    color: white;
    background: transparent;
    font-family: "Times";
    font-size: 35px;
    font-weight: bold;
}
#Version_Label {
    color: white;
    background: transparent;
    font-family: "Times";
    font-size: 20px;
}
#Frame_Label {
    color: white;
    background: transparent;
    font-family: "Times";
    font-size: 22px;
    font-weight: bold;
}
#Frame_Detail_Label {
    color: white;
    background: transparent;
    font-family: "times";
    font-size: 18px;
}
#Team_Mem_Label {
    color: white;
    background: transparent;
    font-family: "Times";
    font-size: 22px;
    font-weight: bold;
}
#Team_Detail_Label {
    color: white;
    background: transparent;
    font-family: "times";
    font-size: 18px;
}
#CopyRight_Label {
    color: white;
    background: transparent;
    font-family: "Times";
    font-size: 22px;
    font-weight: bold;
}
#About_Us_Label {
    color: white;
    background: transparent;
    font-family: "Times";
    font-size: 22px;
    font-weight: bold;
}
#Github_Link {
    color: white;
    background: transparent;
    font-family: "Times";
    font-size: 18px;
}
"""

class AboutView(QWidget):

    def __init__(self, *args, **kwargs):
        super(AboutView, self).__init__(*args, **kwargs)
        self.setStyleSheet(AboutStyleSheet)         # 初始化GUI样式
        self.initUi()                               # 初始化GUI布局


    # 界面布局
    def initUi(self):

        # 内容视图, 管理所有的子视图
        self.content_view = QWidget(self)
        self.content_view.setObjectName("Content_View")
        self.content_view.setGeometry(QRect(0, 0, Sub_Win_Width, Sub_Win_Height))

        # 中间显示区域
        self.show_area_widget = QWidget(self.content_view)
        self.show_area_widget.setObjectName("Show_Area_Widget")
        self.show_area_widget.setGeometry(QRect(90, 90, Locate_Show_Area_Width * 2 + 50, Locate_Show_Area_Height + 120))
        # 内部区域
        self.detail_area_widget = QWidget(self.show_area_widget)
        self.detail_area_widget.setObjectName("Detail_Area_Widget")
        self.detail_area_widget.setGeometry(QRect(60, 60, Locate_Show_Area_Width * 2 - 70, Locate_Show_Area_Height))
        # 项目名称label
        self.logo_label = QLabel(self.detail_area_widget)
        self.logo_label.setObjectName("Logo_Label")
        self.logo_label.setGeometry(QRect(480, 60, 200, 80))
        self.logo_label.setText("HWExplorer")
        self.logo_label.setAlignment(Qt.AlignCenter)
        # 版本label
        self.version_label = QLabel(self.detail_area_widget)
        self.version_label.setObjectName("Version_Label")
        self.version_label.setGeometry(QRect(760, 110, 200, 80))
        self.version_label.setText("版本: v1.0.0 BETA")
        # 框架label
        self.frame_label = QLabel(self.detail_area_widget)
        self.frame_label.setObjectName("Frame_Label")
        self.frame_label.setGeometry(QRect(200, 200, 200, 80))
        self.frame_label.setText("使用框架: ")
        # 框架细节label
        self.frame_detail_label = QLabel(self.detail_area_widget)
        self.frame_detail_label.setObjectName("Frame_Detail_Label")
        self.frame_detail_label.setGeometry(QRect(200, 240, 450, 80))
        self.frame_detail_label.setText("TensorFlow 2.3.1  OpenCV 4.3.2  PyQT 5.3.1")
        # 开发人员label
        self.team_mem_label = QLabel(self.detail_area_widget)
        self.team_mem_label.setObjectName("Team_Mem_Label")
        self.team_mem_label.setGeometry(QRect(200, 300, 200, 80))
        self.team_mem_label.setText("开发人员: ")
        # 开发人员细节label
        self.team_detail_label = QLabel(self.detail_area_widget)
        self.team_detail_label.setObjectName("Team_Detail_Label")
        self.team_detail_label.setGeometry(QRect(200, 330, 300, 80))
        self.team_detail_label.setText("余森, 袁鹏, 姚劲嵩, 袁欣卓")
        # 关于我们
        self.about_us_label = QLabel(self.detail_area_widget)
        self.about_us_label.setObjectName("About_Us_Label")
        self.about_us_label.setGeometry(QRect(200, 400, 100, 80))
        self.about_us_label.setText("关于我们: ")
        # 项目地址
        self.github_link = QLabel(self.detail_area_widget)
        self.github_link.setObjectName("Github_Link")
        self.github_link.setGeometry(QRect(200, 440, 100, 80))
        self.github_link.setOpenExternalLinks(True)
        self.github_link.setText("<a href={0}>{1}</a>".format("https://github.com/USTC-SE-2020/HWExplorer", "项目地址"))

        # 版权label
        self.copyright_label = QLabel(self.detail_area_widget)
        self.copyright_label.setObjectName("CopyRight_Label")
        self.copyright_label.setGeometry(QRect(770, 435, 200, 80))
        self.copyright_label.setText("©️USTC-2020-bd03")