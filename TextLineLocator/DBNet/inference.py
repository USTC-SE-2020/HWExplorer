# -*- coding: utf-8 -*-
# @Time    : 2020/6/16 23:51
# @Author  : zonas.wang
# @Email   : zonas.wang@gmail.com
# @File    : inference.py
import math
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import os.path as osp
import time

import tensorflow as tf
import cv2
import glob
import numpy as np
import pyclipper
from shapely.geometry import Polygon
from tqdm import tqdm

from TextLineLocator.DBNet.models.model import DBNet
from TextLineLocator.DBNet.config import DBConfig

from GUI.config import Locate_Show_Area_Width, Locate_Show_Area_Height

cfg = DBConfig()


def resize_image(image, image_short_side=736):
    height, width, _ = image.shape
    if height < width:
        new_height = image_short_side
        new_width = int(math.ceil(new_height / height * width / 32) * 32)
    else:
        new_width = image_short_side
        new_height = int(math.ceil(new_width / width * height / 32) * 32)
    resized_img = cv2.resize(image, (new_width, new_height))
    return resized_img


def box_score_fast(bitmap, _box):
    h, w = bitmap.shape[:2]
    box = _box.copy()
    xmin = np.clip(np.floor(box[:, 0].min()).astype(np.int), 0, w - 1)
    xmax = np.clip(np.ceil(box[:, 0].max()).astype(np.int), 0, w - 1)
    ymin = np.clip(np.floor(box[:, 1].min()).astype(np.int), 0, h - 1)
    ymax = np.clip(np.ceil(box[:, 1].max()).astype(np.int), 0, h - 1)

    mask = np.zeros((ymax - ymin + 1, xmax - xmin + 1), dtype=np.uint8)
    box[:, 0] = box[:, 0] - xmin
    box[:, 1] = box[:, 1] - ymin
    cv2.fillPoly(mask, box.reshape(1, -1, 2).astype(np.int32), 1)
    return cv2.mean(bitmap[ymin:ymax + 1, xmin:xmax + 1], mask)[0]


def unclip(box, unclip_ratio=1.5):
    poly = Polygon(box)
    distance = poly.area * unclip_ratio / poly.length
    offset = pyclipper.PyclipperOffset()
    offset.AddPath(box, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
    expanded = np.array(offset.Execute(distance))
    return expanded


def get_mini_boxes(contour):
    if not contour.size:
        return [], 0
    bounding_box = cv2.minAreaRect(contour)
    points = sorted(list(cv2.boxPoints(bounding_box)), key=lambda x: x[0])

    index_1, index_2, index_3, index_4 = 0, 1, 2, 3
    if points[1][1] > points[0][1]:
        index_1 = 0
        index_4 = 1
    else:
        index_1 = 1
        index_4 = 0
    if points[3][1] > points[2][1]:
        index_2 = 2
        index_3 = 3
    else:
        index_2 = 3
        index_3 = 2

    box = [points[index_1], points[index_2],
           points[index_3], points[index_4]]
    return box, min(bounding_box[1])


# 在位图上绘制多边形
def polygons_from_bitmap(pred, bitmap, dest_width, dest_height, max_candidates=500, box_thresh=0.7):
    pred = pred[..., 0]
    bitmap = bitmap[..., 0]
    height, width = bitmap.shape
    boxes = []
    scores = []

    contours = cv2.findContours((bitmap * 255).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    # 最多筛选 max_candidates 个边框
    for contour in contours[:max_candidates]:
        epsilon = 0.001 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        points = approx.reshape((-1, 2))
        if points.shape[0] < 4:
            continue
        score = box_score_fast(pred, points.reshape(-1, 2))
        if box_thresh > score:
            continue
        if points.shape[0] > 2:
            box = unclip(points, unclip_ratio=2.0)
            if len(box) > 1:
                continue
        else:
            continue

        box = box.reshape(-1, 2)
        _, sside = get_mini_boxes(box.reshape((-1, 1, 2)))
        if sside < 5:
            continue

        box[:, 0] = np.clip(np.round(box[:, 0] / width * dest_width), 0, dest_width)
        box[:, 1] = np.clip(np.round(box[:, 1] / height * dest_height), 0, dest_height)
        boxes.append(box.tolist())
        scores.append(score)
    return boxes, scores


# 根据图像路径定位图像上的文本行
def locate_lines_in_image_with_path(img_path):
    BOX_THRESH = 0.5
    mean = np.array([103.939, 116.779, 123.68])

    model_path = "/Users/soyou/Documents/EProjects/HWExplorer/TextLineLocator/DBNet/db_model.h5"  # TODO: 更改模型路径
    model = DBNet(cfg, model='inference')                               # 初始化推理模型
    model.load_weights(model_path, by_name=True, skip_mismatch=True)    # 加载预训练模型权重

    image = cv2.imread(img_path)                                        # 读取图像, OpenCV shape: (Height, Width, Channels)
    src_image = image.copy()                                            # 复制原图像
    src_back = image.copy()                                             # 复制原图像
    h, w = image.shape[:2]                                              # 获取图像的高:h, 宽:w
    image = resize_image(image)                                         # 图像尺寸归一化
    image = image.astype(np.float32)                                    # 图像格式转换成numpy float类型
    image -= mean                                                       # 图像特征缩放
    image_input = np.expand_dims(image, axis=0)                         # 扩展图像维度
    image_input_tensor = tf.convert_to_tensor(image_input)              # 将numpy类型的图像转为tensor类型
    p = model.predict(image_input_tensor)[0]                            # 使用模型进行预测

    bitmap = p > 0.3
    boxes, scores = polygons_from_bitmap(p, bitmap, w, h, box_thresh=BOX_THRESH)     # 根据模型预测的结果在原图像上计算多边形
    roi_imgs = []
    roi_rects = []
    for box in boxes:
        res_rect = cal_rect_with_poly_box(box)
        sub_img = src_back[res_rect[2]-5:res_rect[3]+5, res_rect[0]-5:res_rect[1]+5]                        # 截取子区域 [子区域最小的y:子区域最大的y, 子区域最小的x:子区域最大的x]
        roi_imgs.append(sub_img)                                                                            # 保存文本行图像
        sub_rect = (res_rect[0], res_rect[2], res_rect[1]-res_rect[0], res_rect[3]-res_rect[2])             # 计算 (x,y,width,height)
        new_x = (sub_rect[0] / src_back.shape[1]) * Locate_Show_Area_Width - 5
        new_y = (sub_rect[1] / src_back.shape[0]) * Locate_Show_Area_Height - 5
        new_width = (sub_rect[2] / src_back.shape[1]) * Locate_Show_Area_Width + 10
        new_height = (sub_rect[3] / src_back.shape[0]) * Locate_Show_Area_Height + 10
        roi_rects.append((new_x, new_y, new_width, new_height))
        cv2.drawContours(src_image, [np.array(box)], -1, (0, 255, 0), 2)                                    # 在原图像上绘制多边形

    # 返回: (定位后的图像, [文本行图像], [(文本行图像的rect)])
    roi_imgs = roi_imgs[::-1]                                                                               # 逆序
    roi_rects = roi_rects[::-1]                                                                             # 逆序
    return src_image, roi_imgs, roi_rects

# 根据多边形的坐标计算外接矩形框, 返回值: (坐标中最小的x, 坐标中最大的x, 坐标中最小的y, 坐标中最大的y)
def cal_rect_with_poly_box(box):
    MIN_X = 999999                      # 多边形坐标中最小的x
    MAX_X = -1                          # 多边形坐标中最大的x
    MIN_Y = 999999                      # 多边形坐标中最小的y
    MAX_Y  = -1                         # 多边形坐标中最大的y
    for points in box:
        if points[0] < MIN_X:
            MIN_X = points[0]
        if points[0] > MAX_X:
            MAX_X = points[0]
        if points[1] < MIN_Y:
            MIN_Y = points[1]
        if points[1] > MAX_Y:
            MAX_Y = points[1]
    # (坐标中最小的x, 坐标中最大的x, 坐标中最小的y, 坐标中最大的y)
    return (MIN_X, MAX_X, MIN_Y, MAX_Y)


# def main():
#     BOX_THRESH = 0.5
#     mean = np.array([103.939, 116.779, 123.68])
#
#     model_path = "db_model.h5"                              # 模型路径
#
#     img_dir = '/Users/soyou/Desktop/testData/article'
#     img_names = os.listdir(img_dir)
#
#     model = DBNet(cfg, model='inference')                               # 初始化推理模型
#     model.load_weights(model_path, by_name=True, skip_mismatch=True)    # 加载预训练模型权重
#
#     for img_name in tqdm(img_names):
#         img_path = osp.join(img_dir, img_name)
#         image = cv2.imread(img_path)
#         src_image = image.copy()
#         h, w = image.shape[:2]
#         image = resize_image(image)
#         image = image.astype(np.float32)
#         image -= mean
#         image_input = np.expand_dims(image, axis=0)
#         image_input_tensor = tf.convert_to_tensor(image_input)          # 转为tensor
#
#         start_time = time.time()                                        # 定位开始时间
#         p = model.predict(image_input_tensor)[0]
#         end_time = time.time()                                          # 定位结束时间
#         print("time: ", end_time - start_time)
#
#         bitmap = p > 0.3
#         boxes, scores = polygons_from_bitmap(p, bitmap, w, h, box_thresh=BOX_THRESH)
#         for box in boxes:
#             print("box: ", box)
#             cv2.drawContours(src_image, [np.array(box)], -1, (0, 255, 0), 2)
#         image_fname = osp.split(img_path)[-1]
#         cv2.imwrite('datasets/test/output/' + image_fname, src_image)


# if __name__ == '__main__':
#     main()
#
