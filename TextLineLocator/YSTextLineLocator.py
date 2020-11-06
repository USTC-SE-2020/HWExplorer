
# Frameworks
import cv2 as cv
import numpy as np

Min_Contours_Area = 15 * 15

"""
    TODO:
        倾斜矫正
        1. 轮廓调整: 根据上下两个轮廓之间的空隙中的黑点的数量来判断是否应去除空隙中的连接线
        2. 轮廓调整: 结合直方图分布再次判断划分点
        合并小轮廓
"""
class TextLineLocator:

    # 初始化
    def __int__(self):
        pass

    # 对文本行图像进行预处理
    def precess_Image(self, img):
        # src_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # 灰度直方图均衡
        img = cv.equalizeHist(img)

    # 移除不符合条件的轮廓
    def remove_improper_contours(self, contours):
        res_contours = []
        for cont in contours:
            area = cv.contourArea(cont)
            if area < Min_Contours_Area:
                continue
            res_contours.append(cont)
        return res_contours

    # 基于openCV定位文本行
    def locate_textLine_with_cv(self, src_path):
        # 读取RGB图像
        src = cv.imread(src_path)
        # 读取灰度图像
        src_gray = cv.imread(src_path, 0)

        # Sobel运算
        x = cv.Sobel(src_gray, cv.CV_16S, 1, 0)
        y = cv.Sobel(src_gray, cv.CV_16S, 0, 1)
        abs_x = cv.convertScaleAbs(x)
        abs_y = cv.convertScaleAbs(y)
        src_sobel = cv.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)

        # 二值化
        ret, src_threshold = cv.threshold(src_sobel, 0, 255, cv.THRESH_OTSU + cv.THRESH_BINARY)

        # 闭运算
        element = cv.getStructuringElement(cv.MORPH_RECT, (20, 2))
        src_closed = cv.morphologyEx(src_threshold, cv.MORPH_CLOSE, element)
        # cv.imshow("close", src_closed)

        # 开运算
        elem_opening = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
        src_opening = cv.morphologyEx(src_closed, cv.MORPH_OPEN, elem_opening)
        # cv.imshow("opening", src_opening)

        # 提取外部轮廓
        src_contours = src_gray.copy()
        # CHAIN_APPROX_NONE
        contours_list, hierarchy = cv.findContours(src_opening, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

        # 去除不符合条件的轮廓
        contours_list = self.remove_improper_contours(contours_list)
        cv.drawContours(src_contours, contours_list, -1, (0, 0, 255), 3)
        # cv.imshow("contours", src_contours)

        # 取轮廓的外接矩形
        src_rect = src.copy()
        for contours in contours_list:
            rotated_rect = cv.minAreaRect(contours)
            rect_points = cv.boxPoints(rotated_rect)
            rect_points = np.int0(rect_points)
            cv.drawContours(src_rect, [rect_points], 0, (0, 255, 0), 2)
        # cv.imshow("rect", src_rect)
        return src_rect
        # # 等待键盘输入
        # k = cv.waitKey(0)
        # if k == 27:
        #     cv.destroyAllWindows()



