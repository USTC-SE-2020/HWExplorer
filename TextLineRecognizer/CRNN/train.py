
import tensorflow as tf
from models.crnn import model
from models.ctc_loss import CTCLoss
from models.accuracy import WordAccuracy
from models.config import BATCH_SIZE, BUFFER_SIZE, WORK_PATH
from models.data_prepare import load_and_preprocess_image, decode_label, get_image_path
import numpy as np
import json
import time
import os

# 1.查看是否有可用GPU
print("当前可用GPU数量： ", len(tf.config.experimental.list_physical_devices('GPU')))

# 2.获取训练集,测试集
train_all_image_paths, train_all_image_labels, val_all_image_paths, val_all_image_labels = get_image_path(WORK_PATH+'dataset/train/')
print(len(train_all_image_paths), len(train_all_image_labels), len(val_all_image_paths), len(val_all_image_labels))

# 3.训练集数据预处理
train_images_num = len(train_all_image_paths)                   # 训练集的样本数量
train_steps_per_epoch = train_images_num//BATCH_SIZE            # 计算每个epoch中的batch数
train_ds = tf.data.Dataset.from_tensor_slices((train_all_image_paths, train_all_image_labels))          # 创建Dataset,每个元素为(图像路径, 图像对应的标签)
train_ds = train_ds.map(load_and_preprocess_image, num_parallel_calls=tf.data.experimental.AUTOTUNE)    # 对Dataset中的每个元素做map变换,(加载图像, 返回原标签)
train_ds = train_ds.shuffle(buffer_size=BUFFER_SIZE)                                                    # 打乱数据集
train_ds = train_ds.repeat()                                                                            # 将序列重复多次
train_ds = train_ds.batch(BATCH_SIZE)                                                                   # TODO: 将多个元素组合成batch
train_ds = train_ds.map(decode_label, num_parallel_calls=tf.data.experimental.AUTOTUNE)                 # TODO: 对Dataset中的每个??元素/Batch??做map变换,(返回图像,标签转换成稀疏矩阵)
train_ds = train_ds.apply(tf.data.experimental.ignore_errors())                                         #
train_ds = train_ds.prefetch(tf.data.experimental.AUTOTUNE)                                             # 预读取

# 4.测试集数据预处理
val_images_num = len(val_all_image_paths)
val_steps_per_epoch = val_images_num//BATCH_SIZE
val_ds = tf.data.Dataset.from_tensor_slices((val_all_image_paths, val_all_image_labels))
val_ds = val_ds.map(load_and_preprocess_image, num_parallel_calls=tf.data.experimental.AUTOTUNE)
val_ds = val_ds.shuffle(buffer_size=BUFFER_SIZE)
val_ds = val_ds.repeat()
val_ds = val_ds.batch(BATCH_SIZE)
val_ds = val_ds.map(decode_label, num_parallel_calls=tf.data.experimental.AUTOTUNE)
val_ds = val_ds.apply(tf.data.experimental.ignore_errors())
val_ds = val_ds.prefetch(tf.data.experimental.AUTOTUNE)

# 5.加载模型及配置
model = tf.keras.models.load_model(WORK_PATH + 'output/crnn_30.h5', compile=False)
model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
              loss=CTCLoss(), metrics=[WordAccuracy()])
callbacks = [tf.keras.callbacks.ModelCheckpoint(WORK_PATH + 'output/crnn_{epoch}.h5', monitor='val_loss', verbose=1)]

# 6.模型训练
model.fit(train_ds,
          epochs=20,
          steps_per_epoch=train_steps_per_epoch,
          validation_data=val_ds,
          validation_steps=val_steps_per_epoch,
          initial_epoch=0,
          callbacks=callbacks)

