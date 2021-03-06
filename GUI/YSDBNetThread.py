

from Tools import DataFormatter as df
from PyQt5.QtCore import pyqtSignal, QThread
from TextLineLocator.YSLocator import Locator

# TODO: DBNet定位后台处理线程
class DBNetBackThread(QThread):
    #  通过类成员对象定义信号对象: object可传任何类型的对象
    _signal = pyqtSignal(object)

    # img_path: 图像路径
    def __init__(self, img_path):
        super(DBNetBackThread, self).__init__()
        self.img_path = img_path

    def __del__(self):
        self.wait()

    # 后台线程处理图像, DBNet定位出文本行
    def run(self):
        locator = Locator()
        res_img, roi_imgs, roi_rects = locator.locate_lines_with_dbnet(self.img_path)
        # 返回: (定位出文本行的图像, [文本行图像], [文本行图像位置])
        self._signal.emit((df.convert_mat_To_QImage(res_img), roi_imgs, roi_rects))