

from Tools import DataFormatter as df
from PyQt5.QtCore import  pyqtSignal, QThread
from TextLineLocator.YSLocator import Locator

# 定位后台处理线程: 继承QThread
class LocateBackThread(QThread):
    #  通过类成员对象定义信号对象: object可传任何类型的对象
    _signal = pyqtSignal(object)

    def __init__(self, img_paths):
        super(LocateBackThread, self).__init__()
        self.img_paths = img_paths

    def __del__(self):
        self.wait()

    # 后台线程处理图像, 定位出文本行
    def run(self):
        locator = Locator()
        res_imgs_list = []              # [ (定位出文本行的图像, [文本行子图像]) ]
        for path in self.img_paths:
            # 获取定位模块处理后的图像: (定位出文本行的图像, [文本行子图像])
            img_line, roi_imgs = locator.locate_lines_in_image(path)
            res_imgs_list.append((df.convert_mat_To_QImage(img_line), roi_imgs))
            # 主线程刷新一次
            self._signal.emit(res_imgs_list)