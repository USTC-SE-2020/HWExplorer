
import threading
import TextLineRecognizer.CRNN.crnn_interface as crnn



# TODO: 识别模型的整体封装接口

# 识别器: 单例模式
class Recognizer(object):
    _instance_lock = threading.Lock()   # 加锁保证线程安全

    def __init__(self):
        self.model, self.decoder = self.load_pre_trained_models()      # 加载模型和对应的解码器

    # 单例实现
    def __new__(cls, *args, **kwargs):
        if not hasattr(Recognizer, "_instance"):
            with Recognizer._instance_lock:
                if not hasattr(Recognizer, "_instance"):
                    Recognizer._instance = object.__new__(cls)
        return Recognizer._instance

    # 加载预训练好的模型: 只会调用一次
    def load_pre_trained_models(self):
        return crnn.load_pre_trained_model()

    # 识别出文本行图片上的文字信息, imgs: 文本行图像list, 返回值: [string]
    def recognize_text_in_images(self, imgs):
        return crnn.predict_with_image_list(imgs, model=self.model, decoder=self.decoder)

    # 识别出文本行图片上的文字信息, img_paths: 文本行图像路径, 返回值: [string]
    def recognize_texts_with_img_paths(self, img_paths):
        return crnn.predict_with_image_path(img_paths, model=self.model, decoder=self.decoder)

    # 停止模型预测,释放占用资源
    def stop_recognize(self):
        pass