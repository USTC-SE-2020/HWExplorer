

from PyQt5.QtCore import  pyqtSignal, QThread
from TextLineRecognizer.YSRecognizer import Recognizer


# TODO: 识别后台处理线程: 继承QThread
class RecogBackThread(QThread):
    #  通过类成员对象定义信号对象: object可传任何类型的对象
    _signal = pyqtSignal(object)

    # imgs: [[imgs1], [imgs2],...], 每个子数组为一幅图像定位出的所有文本行
    def __init__(self, param_list, type="image"):    # type参数类型: image-图像, path-路径
        super(RecogBackThread, self).__init__()
        self.param_list = param_list
        self.param_type = type

    def __del__(self):
        self.wait()

    # 后台线程处理图像, 识别出图像中的文本信息
    def run(self):
        res_text_list = []                                      # 二维数组: [[str1, str2, ..], [str1,str2,..],....]
        for param in self.param_list:
            recognizer = Recognizer()                           # 获取单例对象, 只会在程序启动时加载一次
            if self.param_type == "image":
                texts = recognizer.recognize_text_in_images(param)  # 识别出的文本信息: [str1, str2, str3,...]
            else:
                texts = recognizer.recognize_texts_with_img_paths(param)
            res_text_list.append(texts)
            self._signal.emit(res_text_list)                    # TODO: 每处理完一张就回调???