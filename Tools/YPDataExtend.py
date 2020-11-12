# -*- coding: utf-8 -*-
import sys


import os
import time
from PIL import Image, ImageChops, ImageEnhance
import cv2

def image_blur(img, savefilepath, save_filename, strength):
    savepath = savefilepath + '/blur'
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    blr = cv2.medianBlur(img, strength)
    im = Image.fromarray(blr)
    im.save(savepath + '/' + save_filename)


def image_rotation(img, savefilepath, save_filename, degree):
    """图像旋转"""
    savepath = savefilepath + '/rotation'
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    out1 = img.rotate(degree)  # 旋转20度
    out1.save(savepath + '/' + save_filename)


def image_translation(img, savefilepath, save_filename, distancex, distancey):
    """图像平移"""
    savepath = savefilepath + '/translation'
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    out3 = ImageChops.offset(img, distancex, distancey)  # x正y正，向右下平移
    out3.save(savepath + '/' + save_filename)


def image_brightness(img, savefilepath, save_filename, strength):
    """亮度调整"""
    savepath = savefilepath + '/brightness'
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    bri = ImageEnhance.Brightness(img)
    bri_img1 = bri.enhance(0.8)  # 小于1为减弱, 大于1为增强
    bri_img1.save(savepath + '/' + save_filename)


def image_contrast(img, savefilepath, save_filename, strength):
    """对比度调整"""
    savepath = savefilepath + '/contrast'
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    con = ImageEnhance.Contrast(img)
    con_img1 = con.enhance(strength)  # 对比度减弱
    con_img1.save(savepath + '/' + save_filename)


def image_sharpness(img, savefilepath, save_filename, strength):
    """锐度调整"""
    savepath = savefilepath + '/sharpness'
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    sha = ImageEnhance.Sharpness(img)
    sha_img1 = sha.enhance(strength)  # 锐度减弱
    sha_img1.save(savepath + '/' + save_filename)



# 定义扩充图片函数
def image_expansion(filepath, savefilepath):
    """
    :param filepath: 图片路径
    :param savefilepath: 扩充保存图片路径
    :param save_prefix: 图片前缀
    :return: 图片扩充数据集
    """

    files = os.listdir(filepath)
    for file in files:
        save_prefix = file[:-4]
        image_path = filepath + '/' + file
        try:
            img = Image.open(image_path)
            img_cv = cv2.imread(image_path, 1)
            if img.mode == "P":
                img = img.convert('RGB')
            image_blur(img_cv, savefilepath, save_filename=save_prefix + '_' + str(1) + '.jpg', strength=9)
            image_rotation(img, savefilepath, save_filename=save_prefix + '_' + str(2) + '.jpg', degree=2)
            image_translation(img, savefilepath, save_filename=save_prefix + '_' + str(3) + '.jpg', distancex=15, distancey=15)
            image_brightness(img, savefilepath, save_filename=save_prefix + '_' + str(4) + '.jpg', strength=0.5)
            image_contrast(img, savefilepath, save_filename=save_prefix + '_' + str(5) + '.jpg', strength=1.5)
            image_sharpness(img, savefilepath, save_filename=save_prefix + '_' + str(6) + '.jpg', strength=8)
        except Exception as e:
            print(e)
            pass


if __name__ == '__main__':
    # 设置图片路径
    #filepath = 'F:/研一上学期/工程实践准备/dataset/test'
    filepath = 'F:/test'

    # 设置扩充保存图片路径
    savefilepath = 'F:/研一上学期/工程实践准备/dataset/test'


    # 设置前缀图片名称
    time1 = time.time()
    image_expansion(filepath, savefilepath)
    time2 = time.time()
    print('总共耗时：' + str(time2 - time1) + 's')
