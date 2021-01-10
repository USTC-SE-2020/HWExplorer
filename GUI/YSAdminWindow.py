
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QPushButton, QWidget, QLabel
from PyQt5.QtCore import Qt, QRect, pyqtSlot, pyqtSignal

# 样式表: 设置控件外观
AWStylesheet = """ 
#Background_Widget {
    background: #F7F5EE;
    border-radius: 20px;
}
#State_Bar_Label {
    background: #04040F;
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
}
#State_Bar_Title {
    font-size: 20px;
    color:#F7F5EE;
}
#Content_Widget {
    background: #FFEDD2;
    border-radius: 20px;
}
#Sperate_Line {
    background: red;
}

#Save_Button {
    border-radius: 10px;
    font-size: 15px;
    background: #FDD56C;
    color: black;
}
#Save_Button:pressed {
    background: #0E0D0C;
    color: white;
}
"""

# TODO: 管理员窗口
class AdminWindow(QMainWindow):

    back_wel_win = pyqtSignal()                                                 # 信号, 用于控制器控制窗口跳转回欢迎界面

    def __init__(self, *args, **kwargs):
        super(AdminWindow, self).__init__(*args, **kwargs)
        self.setObjectName('Custom_Window')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)                    # 窗口透明,用于设置背景圆角
        self.resize(800, 600)                                                   # 窗口尺寸: 宽800 x 高600
        self.setStyleSheet(AWStylesheet)                                        # 设置样式表
        self.setMaximumSize(800, 600)                                           # 窗口尺寸: 最大宽度800 x 最大高度600
        self.setMinimumSize(800, 600)                                           # 窗口尺寸: 最小宽度800 x 最小高度600
        self.initUI()                                                           # 初始化界面布局
        self.center()                                                           # 窗口居中


    # 初始化界面布局
    def initUI(self):
        # 背景Widget, 用于设置圆角窗口
        self.background_widget = QWidget(self)
        self.background_widget.setObjectName('Background_Widget')
        self.background_widget.setGeometry(QRect(0, 0, 800, 600))

        # 添加顶部状态栏
        self.state_bar_label = QLabel(self.background_widget)
        self.state_bar_label.setGeometry(QRect(0, 0, 800, 48))
        self.state_bar_label.setObjectName("State_Bar_Label")
        # 添加顶部状态栏标题
        self.state_bar_title = QLabel(self.state_bar_label)
        self.state_bar_title.setGeometry(QRect(320, 0, 150, 50))
        self.state_bar_title.setObjectName("State_Bar_Title")
        self.state_bar_title.setText("管理员模式")
        self.state_bar_title.setAlignment(Qt.AlignCenter)

        # 添加中间: 650 x 300
        self.content_view = QWidget(self.background_widget)
        self.content_view.setObjectName("Content_Widget")
        self.content_view.setGeometry(QRect(75, 120, 650, 350))

        # 分割线
        self.sperate_line = QWidget(self.content_view)
        self.sperate_line.setObjectName("Sperate_Line")
        self.sperate_line.setGeometry(QRect(0, 150, 650, 2))


        # 按钮: 保存设置
        self.save_button = QPushButton(self.background_widget)
        self.save_button.setGeometry(QRect(330, 530, 120, 50))
        self.save_button.setObjectName("Save_Button")
        self.save_button.setText("保存并退出")
        self.save_button.clicked.connect(self.save_and_back_to_welcome)

        pass

    # 窗口居中
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2 - 50)

    @pyqtSlot()
    # 保存修改并返回欢迎界面
    def save_and_back_to_welcome(self):
        self.back_wel_win.emit()
