#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Frameworks
import sys
import cgitb
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QSplashScreen, QWidget

#
class GifSplashScreen(QSplashScreen):

    def __init__(self, *args, **kwargs):
        super(GifSplashScreen, self).__init__(*args, **kwargs)
        self.movie = QMovie('Resources/splash.gif')
        self.movie.frameChanged.connect(self.onFrameChanged)
        self.movie.start()

    #
    def onFrameChanged(self, _):
        self.setPixmap(self.movie.currentPixmap())

    # gif动画结束
    def finish(self, widget):
        self.movie.stop()
        super(GifSplashScreen, self).finish(widget)


if __name__ == '__main__':


    cgitb.enable(1, None, 5, '')

    app = QApplication(sys.argv)
    splash = GifSplashScreen()
    splash.show()


    def createWindow():
        app.w = QWidget()
        # 模拟初始5秒后再显示
        splash.showMessage('等待界面显示', Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
        QTimer.singleShot(3000, lambda: (
            splash.showMessage('初始化完成', Qt.AlignHCenter | Qt.AlignBottom, Qt.white), app.w.show(),
            splash.finish(app.w)))


    # 模拟耗时5秒。但是不能用sleep
    # 可以使用子线程加载耗时的数据
    # 主线程中循环设置UI可以配合QApplication.instance().processEvents()
    splash.showMessage('等待创建界面', Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
    QTimer.singleShot(3000, createWindow)

    sys.exit(app.exec_())