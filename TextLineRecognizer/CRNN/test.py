import tensorflow as tf
from TextLineRecognizer.CRNN.models.ctc_loss import CTCLoss
from TextLineRecognizer.CRNN.models.accuracy import WordAccuracy
from TextLineRecognizer.CRNN.models.decode import Decoder
from TextLineRecognizer.CRNN.models.config import BATCH_SIZE, BUFFER_SIZE, WORK_PATH,TEST_PATH, is_save_model, TABLE_PATH, export_path
from TextLineRecognizer.CRNN.models.data_prepare import load_and_preprocess_image, decode_label,load_and_preprocess_image_pridict
import numpy as np
import random
import json
import time
import os



test_all_image_paths = [TEST_PATH + img for img in sorted(os.listdir(TEST_PATH))]     # 获取测试集的所有图片路径
test_images_num = len(test_all_image_paths)                                           # 获取测试集的图片数量
test_steps_per_epoch = test_images_num                                                # 用于测试的每个epoch的图片数量
test_ds = tf.data.Dataset.from_tensor_slices(test_all_image_paths)                    # 创建Dataset, 其中每个元素为图片的路径字符串
test_ds = test_ds.map(                    # 对Dataset中的元素做map变换, 即每个元素都会被当作函数的输入, 并将函数返回值作为新的Dataset
    load_and_preprocess_image_pridict,    # map操作后Dataset中每个元素为处理后的图片
    num_parallel_calls=tf.data.experimental.AUTOTUNE)                                 # num_parallel_calls用于并行处理变换
test_ds = test_ds.repeat()                                                            # 将序列重复多次
test_ds = test_ds.batch(2)                                                            # 将多个元素组合成batch
test_ds = test_ds.apply(tf.data.experimental.ignore_errors())                         # TODO:
test_ds = test_ds.prefetch(tf.data.experimental.AUTOTUNE)                             # 预读取数据

model = tf.keras.models.load_model(WORK_PATH + 'output/crnn_30.h5', compile=False)
model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
              loss=CTCLoss(), metrics=[WordAccuracy()])

test_data = next(iter(test_ds))
start = time.time()
result = model.predict(test_data)
print(time.time()-start)

with open(TABLE_PATH, 'r', encoding='utf-8') as f:
    inv_table = [char.strip() for char in f] + [' '] * 2

decoder = Decoder(inv_table)
#
# font = FontProperties(fname='./dataset/fonts/msyh.ttc', size=16)
#
# y_pred = decoder.decode(result, method='greedy')
#
# for i, sentense in enumerate(y_pred):
#     print('---------------------------------------')
#     plt.figure(figsize=(16, 32))
#     plt.subplot(len(y_pred), 1, i + 1)
#     plt.imshow(load_and_preprocess_image_draw(test_all_image_paths[i]))
#     plt.xlabel('识别结果： ' + sentense, fontproperties=font)
#     plt.show()
