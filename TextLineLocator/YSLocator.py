
import threading
from GUI.config import Locate_Show_Area_Width, Locate_Show_Area_Height
from TextLineLocator.YSTextLineLocator import TextLineLocator
from TextLineLocator.DBNet.dbnet_interface import locate_text_lines_with_dbnet

# TODO: 定位模型的整体封装接口
# 定位器: 单例模式
class Locator(object):
    _instance_lock = threading.Lock()   # 加锁保证线程安全

    def __init__(self):
        # 加载训练好的定位模型
        self.locater = self.load_pre_trained_models()
        pass

    # 单例实现
    def __new__(cls, *args, **kwargs):
        if not hasattr(Locator, "_instance"):
            with Locator._instance_lock:
                if not hasattr(Locator, "_instance"):
                    Locator._instance = object.__new__(cls)
        return Locator._instance

    # 加载预训练好的模型: 只会调用一次
    def load_pre_trained_models(self):
        return TextLineLocator()

    # 形态学 定位出图片上的文本行, img_path: 图像路径
    def locate_lines_in_image(self, img_path):
        return self.locater.locate_textLine_with_cv(img_path)

    # DBNet 定位出图像上的文本行, img_path: 图像路径, 返回值: (定位后的图像, [文本行图像], [(文本行图像的rect)])
    def locate_lines_with_dbnet(self, img_path):
        return locate_text_lines_with_dbnet(img_path=img_path)


