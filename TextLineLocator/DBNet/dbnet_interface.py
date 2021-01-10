

import cv2

# TODO: DBNet接口
from TextLineLocator.DBNet.inference import locate_lines_in_image_with_path


# 使用DBNet定位文本行, (定位后的图像, [文本行图像], [(文本行图像的rect)])
def locate_text_lines_with_dbnet(img_path):
    return locate_lines_in_image_with_path(img_path)

