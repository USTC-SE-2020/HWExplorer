
import sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QRect



# TODO: 自定义TextView, 用于绘制多行文本信息
class PaintTextView(QWidget):

    # 文本行数组texts: [str1, str2,...], 文本行对应的位置: [(x,y,width,height), (x,y,width,height)...]
    def __init__(self, *args, **kwargs):
        super(PaintTextView, self).__init__(*args, **kwargs)
        self.texts = [""]                           # 要绘制的文字信息
        self.texts_rect = [(10,20,100,20)]          # 要绘制的文字对应位置
        self.painter = QPainter(self)               # 初始化画笔

    # 绘制文字到textview上
    def paintEvent(self, event):
        # print("调用paintEvent!!!")
        if self.texts and self.texts_rect:
            self.painter.begin(self)
            self.painter.setPen(QColor(0, 0, 0))  # 设置文字的颜色
            self.painter.setFont(QFont("SimSun", 15))
            for text, rect in zip(self.texts, self.texts_rect):
                # print("texts: {}, rect:{}".format(text, rect))
                self.painter.drawText(QRect(rect[0], rect[1], rect[2], rect[3]), Qt.AlignLeft, text)
            self.painter.end()

    # 在textview上重绘文字
    def redraw_text_in_view(self, texts, texts_rect):
        self.texts = texts
        self.texts_rect = texts_rect
        self.repaint()

    # 清空视图上的残留信息
    def clear_text_for_update(self):
        self.texts = [""]
        self.texts_rect = [(10, 20, 100, 20)]
        self.repaint()




























