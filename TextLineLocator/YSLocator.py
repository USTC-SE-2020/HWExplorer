
import threading
from TextLineLocator.YSTextLineLocator import TextLineLocator

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

    # 定位出图片上的文本行, img_path: 图像路径
    def locate_lines_in_image(self, img_path):
        return self.locater.locate_textLine_with_cv(img_path)


