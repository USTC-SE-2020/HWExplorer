import os
import cv2
import random
import pickle
from pathlib import Path
import tensorflow as tf
from TextLineRecognizer.CRNN.models.config import TABLE_PATH, NUM_CLASSES, OUTPUT_SHAPE, WORK_PATH

#字典查询器
table = tf.lookup.StaticHashTable(
            tf.lookup.TextFileInitializer(
                TABLE_PATH, 
                tf.string, 
                tf.lookup.TextFileIndex.WHOLE_LINE, 
                tf.int64, tf.lookup.TextFileIndex.LINE_NUMBER
            ), 
        NUM_CLASSES-2)

# 处理opencv中的图像
def preprocess_image_with_cv(image):
    image_shape = (32, 720, 3)
    image = image / 255  # 将像素值缩放到 0~1之间
    image -= 0.5
    image /= 0.5
    imgH, imgW, imgC = image_shape
    resized_image = tf.image.resize(image, [imgH, imgW], preserve_aspect_ratio=True)  # 将所有图片缩放到指定size
    padding_im = tf.image.pad_to_bounding_box(resized_image, 0, 0, imgH, imgW)  # 用0填充放缩后的图片无像素的部分
    return padding_im
    pass


#数据预处理方法
def preprocess_image(image, mode = 'train'):
    image = tf.image.decode_jpeg(image, channels=3)
    if mode == 'train':
        image_shape = (32, 320, 3)      # 训练时: [Height, Width, Channels] = [32, 320, 3]
        # 饱和度
        image = tf.image.random_saturation(image, 0, 3)
        # 色调
        image = tf.image.random_hue(image, 0.3)
        # 对比度
        image = tf.image.random_contrast(image, 0.5, 5)
        # 亮度
        image = tf.image.random_brightness(image, max_delta=0.05)
    elif mode == 'val':
        image_shape = (32, 320, 3)      # 验证时: [Height, Width, Channels] = [32, 320, 3]
    else:
        image_shape = (32, 720, 3)      # 预测时: [Height, Width, Channels] = [32, 720, 3], 考虑到长文本的水平缩放问题
    image = image / 255                 # 将像素值缩放到 0~1之间
    image -= 0.5
    image /= 0.5
    imgH, imgW, imgC = image_shape
    resized_image = tf.image.resize(image, [imgH, imgW], preserve_aspect_ratio=True)   # 将所有图片缩放到指定size
    padding_im = tf.image.pad_to_bounding_box(resized_image, 0, 0, imgH, imgW)         # 用0填充放缩后的图片无像素的部分
    return padding_im


# 训练 -> 图像加载与预处理
def load_and_preprocess_image(path,label):
    image = tf.io.read_file(path)
    return preprocess_image(image), label


# 验证 -> 图像加载与预处理
def load_and_preprocess_image_val(path, label, mode='val'):
    image = tf.io.read_file(path)
    return preprocess_image(image, mode), label


# 预测 -> 图像加载与预处理
def load_and_preprocess_image_pridict(path, mode='predict'):
    image = tf.io.read_file(path)
    return preprocess_image(image, mode)


def load_and_preprocess_image_draw(path):
    image = tf.io.read_file(path)
    img = tf.image.decode_jpeg(image, channels=3)
    return img


# 将图像对应的标签编码成稀疏tensor
def decode_label(img, label):
    chars = tf.strings.unicode_split(label, "UTF-8")                # 将'UTF-8'编码的标签划分为unicode字符
    tokens = tf.ragged.map_flat_values(table.lookup, chars)         # 根据词库将字符编码成对应的数字
    tokens = tokens.to_sparse()                                     # 将转为稀疏tensor
    return img, tokens


# 获取图片路径列表,及其标签列表
def get_image_path(dir_path):
    if os.path.exists(WORK_PATH+'dataset/dataset.data'):
        with open(WORK_PATH+'dataset/dataset.data', 'rb') as f:
            train_all_image_paths, train_all_image_labels,val_all_image_paths,val_all_image_labels = pickle.load(f)
        print('数据集加载完毕！')
        return train_all_image_paths, train_all_image_labels,val_all_image_paths,val_all_image_labels
    else:
        print('开始获取数据集，请耐心等待...')
        images  = []                                # [(图像路径, 图像对应的标签)]
        train_all_image_paths = []                  # 训练集图像路径
        train_all_image_labels = []                 # 训练集图像对应标签
        val_all_image_paths = []                    # 验证集图像路径
        val_all_image_labels = []                   # 验证集图像对应标签
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if '.jpg' in file:                                  # 图像文件格式为jpg格式
                    file_path = os.path.join(root, file)
                    label_path = file_path.replace('.jpg','.txt')   # 标签文件格式为txt
                    if Path(file_path.replace('.jpg','.txt')).exists():
                        with open(label_path) as f:
                            label = f.read().strip()
                        imgs= cv2.imread(file_path)
                        if imgs.shape[1]/imgs.shape[0] <= 10 and len(label)>0:
                            images.append((file_path, label))               # 添加tuple (图像路径, 图像对应的标签)
        random.shuffle(images)                                              # 随机打乱顺序
        for image,label in images:
            random_num = random.randint(1,80)                               # 根据生成的随机数来划分训练集和测试集
            if random_num == 5:
                val_all_image_paths.append(image)
                val_all_image_labels.append(label)
            else:
                train_all_image_paths.append(image)
                train_all_image_labels.append(label)
        with open(WORK_PATH+'dataset/dataset.data', 'wb') as f:
            pickle.dump((train_all_image_paths, train_all_image_labels,val_all_image_paths,val_all_image_labels), f)
        print('数据集加载完毕！')
        return train_all_image_paths, train_all_image_labels,val_all_image_paths,val_all_image_labels