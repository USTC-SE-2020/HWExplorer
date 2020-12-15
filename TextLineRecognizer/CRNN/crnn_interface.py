

import tensorflow as tf
from TextLineRecognizer.CRNN.models.config import WORK_PATH, TABLE_PATH
from TextLineRecognizer.CRNN.models.ctc_loss import CTCLoss
from TextLineRecognizer.CRNN.models.decode import Decoder
from TextLineRecognizer.CRNN.models.accuracy import WordAccuracy
from TextLineRecognizer.CRNN.models.data_prepare import load_and_preprocess_image_pridict, preprocess_image_with_cv


# 对单个图像文件进行预测: 图像文件路径
def predict_with_image_path(img_path, model, decoder):
    img = load_and_preprocess_image_pridict(img_path)       # 预处理图像
    imgs = tf.convert_to_tensor([img])                      # 将list转换成tensor
    raw_result = model.predict(imgs)                        # 使用模型预测
    result = decoder.decode(raw_result, method='greedy')    # 对预测结果进行贪心解码
    return result


# 对单个图像文件进行预测: 图像文件
def predict_with_image(img, model, decoder):
    img = preprocess_image_with_cv(img)
    imgs = tf.convert_to_tensor([img])
    raw_result = model.predict(imgs)
    result = decoder.decode(raw_result, method='greedy')
    return result


# 对多个图像文件进行预测: 图像列表
def predict_with_image_list(img_list, model, decoder):
    imgs = []
    for img in img_list:
        img = preprocess_image_with_cv(img)
        imgs.append(img)
    imgs = tf.convert_to_tensor(imgs)
    raw_result = model.predict(imgs)
    result = decoder.decode(raw_result, method='greedy')
    return result

# 从路径加载多个文本行图像进行预测: 图像列表
def predict_with_image_paths(img_paths, model, decoder):
    imgs = []
    for path in img_paths:
        img = load_and_preprocess_image_pridict(path)
        imgs.append(img)
    imgs = tf.convert_to_tensor(imgs)
    raw_result = model.predict(imgs)
    result = decoder.decode(raw_result, method='greedy')
    return result


# 加载预训练好的模型及对应的解码器
def load_pre_trained_model():
    model = tf.keras.models.load_model(WORK_PATH + 'TextLineRecognizer/CRNN/output/crnn_30.h5', compile=False)    # 加载预训练好的模型
    model.compile(optimizer=tf.keras.optimizers.Adam(0.001),                              # 配置优化器,损失函数,准确率计算函数
                  loss=CTCLoss(), metrics=[WordAccuracy()])
    with open(TABLE_PATH, 'r', encoding='utf-8') as f:                                    # 加载预训练模型对应的词库txt文件
        inv_table = [char.strip() for char in f] + [' '] * 2                              # TODO: 最后加两个空格???
    decoder = Decoder(inv_table)                                                          # 利用词库配置解码器
    return model, decoder






