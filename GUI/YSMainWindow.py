

import sys
import cv2 as cv
from Tools import FileManager as fm
from TextLineLocator.YSTextLineLocator import TextLineLocator
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from PyQt5.QtGui import QPalette, QPixmap, QFont, QImage
from PyQt5.QtCore import Qt, QSize, QTimer, QRect, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QWidget, QSpacerItem, QLabel, QFileDialog



# 样式表: 设置控件外观
Stylesheet = """
#bottomControlBar {
    background: orange;
}
#chooseDirBtn {
    border-radius: 10px;
    background: red;
    color: white;
}
#chooseDirBtn:pressed {
    border-radius: 10px;
    background: #FDD56C;
    color: black;
}
"""

# Global Constants
Main_Win_Width = 1500
Main_Win_Height = 1000

class MainWindow(QMainWindow):
    # 用于控制窗口跳转
    switch_window = pyqtSignal()

    # 初始化
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setObjectName('Custom_Window')
        self.resize(Main_Win_Width,Main_Win_Height)
        self.setMaximumSize(Main_Win_Width, Main_Win_Height)
        self.setMinimumSize(Main_Win_Width, Main_Win_Height)
        self.center()
        self.setWindowTitle("HWExplorer")
        self.setStyleSheet(Stylesheet)
        self.ori_Images = []
        self.res_Images = []
        self.curr_Img_Index = 0
        self.initUi()

    # 界面布局
    def initUi(self):

        # 添加图片: 左侧
        self.oriImageView = QLabel(self)
        self.oriImageView.setGeometry(QRect(30, 30, 700, 800))
        self.oriImageView.setObjectName("oriImageView")
        self.oriImageView.setScaledContents(True)

        # 添加图片: 右侧
        self.resImageView = QLabel(self)
        self.resImageView.setGeometry(QRect(750, 30, 700, 800))
        self.resImageView.setObjectName("resImageView")
        self.resImageView.setScaledContents(True)


        # 添加按钮: 选择文件夹
        self.chooseDirBtn = QPushButton(self)
        self.chooseDirBtn.setGeometry(QRect(Main_Win_Width / 2 - 50, Main_Win_Height - 150, 100, 40))
        self.chooseDirBtn.setObjectName("chooseDirBtn")
        self.chooseDirBtn.setText("选择文件夹")
        self.chooseDirBtn.clicked.connect(self.choose_Diretory)

        # 添加下方控制栏
        self.bottomControlBar = QWidget(self)
        self.bottomControlBar.setGeometry(QRect(Main_Win_Width / 2 - 400, Main_Win_Height - 100, 800, 80))
        self.bottomControlBar.setObjectName("bottomControlBar")

        # 添加Label
        self.numLabel = QLabel(self.bottomControlBar)
        self.numLabel.setGeometry(QRect(350, 10, 100, 60))
        self.numLabel.setObjectName("numLabel")
        self.numLabel.setText("1/55")
        self.numLabel.setFont(QFont("Roman", 20, QFont.Bold))

        # 添加按钮: 上一张
        self.preBtn = QPushButton(self.bottomControlBar)
        self.preBtn.setGeometry(QRect(30, 30, 70, 40))
        self.preBtn.setObjectName("preBtn")
        self.preBtn.setText("上一张")
        self.preBtn.clicked.connect(self.choose_pre_Image)

        # 添加按钮: 下一张
        self.nextBtn = QPushButton(self.bottomControlBar)
        self.nextBtn.setGeometry(QRect(700, 30, 70, 40))
        self.nextBtn.setObjectName("nextBtn")
        self.nextBtn.setText("下一张")
        self.nextBtn.clicked.connect(self.choose_next_Image)

    # 窗口居中
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    # 将openCV中的mat转为QT中的QImage
    def convert_mat_To_QImage(self, mat):
        shrink = cv.cvtColor(mat, cv.COLOR_BGR2RGB)
        qImg = QImage(shrink.data,
                                  shrink.shape[1],
                                  shrink.shape[0],
                                  shrink.shape[1] * 3,
                                  QImage.Format_RGB888)
        return qImg

    # 事件响应
    @pyqtSlot()
    # 选择文件夹
    def choose_Diretory(self):
        print("选择文件夹")
        dir_path = QFileDialog.getExistingDirectory(self, "getExistingDirectory", fm.get_Curr_Dir())
        fm.get_Images_In_Dir(dir_path, self.ori_Images)
        if len(self.ori_Images) == 0:
            return
        self.oriImageView.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
        self.numLabel.setText("1 / %d" % len(self.ori_Images))
        locator = TextLineLocator()
        for path in self.ori_Images:
            mat = locator.locate_textLine_with_cv(path)
            self.res_Images.append(self.convert_mat_To_QImage(mat))
            if len(self.res_Images) == 1:
                self.resImageView.setPixmap(QPixmap.fromImage(self.res_Images[self.curr_Img_Index]))
        self.curr_Img_Index += 1

    # 选择上一张图片
    def choose_pre_Image(self):
        if self.curr_Img_Index - 1 >= 0:
            self.curr_Img_Index -= 1
            self.oriImageView.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
            self.resImageView.setPixmap(QPixmap.fromImage(self.res_Images[self.curr_Img_Index]))
            self.numLabel.setText("%d / %d" % (self.curr_Img_Index, len(self.ori_Images)))

    # 选择下一张图片
    def choose_next_Image(self):
        if self.curr_Img_Index + 1 < len(self.ori_Images):
            self.curr_Img_Index += 1
            self.oriImageView.setPixmap(QPixmap(self.ori_Images[self.curr_Img_Index]))
            self.resImageView.setPixmap(QPixmap.fromImage(self.res_Images[self.curr_Img_Index]))
            self.numLabel.setText("%d / %d" % (self.curr_Img_Index, len(self.ori_Images)))


