

from PyQt5.QtWidgets import QPushButton, QWidget, QLabel
from PyQt5.QtGui import QPainter, QFont, QBrush, QColor, QPen
from PyQt5.QtCore import Qt, QRect, pyqtSlot

# TODO: 自定义开关按钮
class SwitchButton(QWidget):

    def __init__(self, parent=None):
        super(SwitchButton, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)        # 设置无边框
        self.setAttribute(Qt.WA_TranslucentBackground)                          # 设置背景透明
        self.resize(70, 30)
        self.state = False                                                      # 按钮状态：True表示开，False表示关

    # 鼠标点击事件：用于切换按钮状态
    def mousePressEvent(self, event):
        super(SwitchButton, self).mousePressEvent(event)
        self.state = False if self.state else True                              # 点击时切换状态 True <-> False
        self.update()                                                           # 更新UI布局

    # 绘制按钮
    def paintEvent(self, event):
        super(SwitchButton, self).paintEvent(event)

        # 创建绘制器并设置抗锯齿和图片流畅转换
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        # 定义字体样式
        font = QFont('Microsoft YaHei')
        font.setPixelSize(14)
        painter.setFont(font)

        # 开关为开的状态 - True
        if self.state:
            # 绘制背景
            painter.setPen(Qt.NoPen)
            brush = QBrush(QColor('#FF475D'))
            painter.setBrush(brush)
            painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2)

            # 绘制圆圈
            painter.setPen(Qt.NoPen)
            brush.setColor(QColor('#ffffff'))
            painter.setBrush(brush)
            painter.drawRoundedRect(43, 3, 24, 24, 12, 12)

            # 绘制文本
            painter.setPen(QPen(QColor('#ffffff')))
            painter.setBrush(Qt.NoBrush)
            painter.drawText(QRect(18, 4, 50, 20), Qt.AlignLeft, '开')
        # 开关为关的状态 - False
        else:
            # 绘制背景
            painter.setPen(Qt.NoPen)
            brush = QBrush(QColor('#CACCC6'))
            painter.setBrush(brush)
            painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height()//2, self.height()//2)

            # 绘制圆圈
            pen = QPen(QColor('#999999'))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRoundedRect(3, 3, 24, 24, 12, 12)

            # 绘制文本
            painter.setBrush(Qt.NoBrush)
            painter.drawText(QRect(38, 4, 50, 20), Qt.AlignLeft, '关')