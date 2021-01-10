
# Frameworks
import cv2 as cv
import numpy as np

from GUI.config import Locate_Show_Area_Width, Locate_Show_Area_Height

Min_Contours_Area = 15 * 15

class TextLineLocator:

    # 初始化
    def __int__(self):
        pass

    # 对文本行图像进行预处理
    def precess_Image(self, img):
        # src_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        # 灰度直方图均衡
        img = cv.equalizeHist(img)

    # 移除图像中的水平和垂直线
    def remove_all_lines(self, image):
        result = image.copy()
        # 1.转换成灰度图
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # 2.Otsu's二值化
        thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
        # 3.用水平kernel检测灰度图中的水平线: (Width, Height)
        horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (25, 1))
        remove_horizontal = cv.morphologyEx(thresh, cv.MORPH_OPEN, horizontal_kernel, iterations=2)
        cnts = cv.findContours(remove_horizontal, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv.drawContours(result, [c], -1, (255, 255, 255), 2)  # TODO: 填充水平线, 用背景色???
        # 4.用垂直kernel检测灰度图中的垂直线: (Height, Width)
        vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 25))
        remove_vertical = cv.morphologyEx(thresh, cv.MORPH_OPEN, vertical_kernel, iterations=2)
        cnts = cv.findContours(remove_vertical, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv.drawContours(result, [c], -1, (255, 255, 255), 2)  # TODO: 填充水平线, 用背景色???

        return result

    # 移除不符合条件的轮廓
    def remove_improper_contours(self, contours):
        res_contours = []
        for cont in contours:
            area = cv.contourArea(cont)
            if area < Min_Contours_Area:
                continue
            res_contours.append(cont)
        return res_contours


    def locate_textline(self, src_path):

        src = cv.imread(src_path)       # 读取RGB图像
        if src is None:                 # 解决windows下中文路径无法读取的问题
            src = cv.imdecode(np.fromfile(src_path, dtype=np.uint8), -1)

        src_nolines = self.remove_all_lines(src)    # 移除图像中的水平和垂直线, 返回RGB图像
        cv.imshow("line", src_nolines)
        cv.imshow("1", src)
        src_noline_gray = cv.cvtColor(src_nolines, cv.COLOR_BGR2GRAY)   # 图像灰度化

        # 二值化
        src_thresh = cv.threshold(src_noline_gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
        cv.imshow("thresh", src_thresh)

        # 闭运算找文字
        element = cv.getStructuringElement(cv.MORPH_RECT, (15, 3))
        src_closed = cv.morphologyEx(src_thresh, cv.MORPH_CLOSE, element)
        cv.imshow("texts", src_closed)

        # 取轮廓
        cnts = cv.findContours(src_closed, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        cnts = self.remove_improper_contours(cnts)          #  去除不合适的轮廓

        for c in cnts:
            rotated_rect = cv.minAreaRect(c)
            rect_points = cv.boxPoints(rotated_rect)
            rect_points = np.int0(rect_points)
            cv.drawContours(src, [rect_points], 0, (0, 255, 0), 2)

        cv.imshow("res", src)
        k = cv.waitKey(0)
        if k == 27:
            cv.destroyAllWindows()
        pass


    # 基于openCV定位文本行
    def locate_textLine_with_cv(self, src_path):
        # 读取RGB图像
        src = cv.imread(src_path)
        # 读取灰度图像
        src_gray = cv.imread(src_path, 0)
        # 解决windows下中文路径无法读取的问题
        if (src is None) or (src_gray is None):
            src = cv.imdecode(np.fromfile(src_path, dtype=np.uint8), -1)
            src_gray = cv.imdecode(np.fromfile(src_path, dtype=np.uint8), 0)

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

        # # 开运算
        # elem_opening = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
        # src_opening = cv.morphologyEx(src_closed, cv.MORPH_OPEN, elem_opening)

        # 提取外部轮廓
        src_contours = src_gray.copy()
        contours_list, hierarchy = cv.findContours(src_closed, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)[-2:]

        # 去除不符合条件的轮廓
        contours_list = self.remove_improper_contours(contours_list)
        cv.drawContours(src_contours, contours_list, -1, (0, 0, 255), 3)

        # 取轮廓的外接矩形
        src_rect = src.copy()
        roi_imgs = []                           # 轮廓图像list
        roi_rects = []                          # 轮廓图像坐标,对应PyQt5中的QRect: [(x, y, width, height)]
        for contours in contours_list:
            rotated_rect = cv.minAreaRect(contours)
            rect_points = cv.boxPoints(rotated_rect)
            rect_points = np.int0(rect_points)
            xs = [x[1] for x in rect_points]            # y
            ys = [y[0] for y in rect_points]            # x
            # 忽略外接矩形在图像外的子区域
            if (min(xs) < 0) or (max(xs) < 0) or (min(ys) < 0) or (max(ys) < 0):
                continue
            src_roi = src[min(xs):max(xs), min(ys):max(ys)]         # 截取外接矩形区域
            roi_imgs.append(src_roi)

            # OpenCV mat shape: (Height, Width, Channels)
            # 重新按比例计算(x, y, width, height) <=> (min(ys), min(xs), (max(ys)-min(ys)), (max(xs)-min(xs))
            x_loc = int((min(ys) / src.shape[1]) * Locate_Show_Area_Width)                             # 文本行显示区域 x
            y_loc = int((min(xs) / src.shape[0]) * Locate_Show_Area_Height)                            # 文本行显示区域 y
            new_width = int(((max(ys)-min(ys)) / src.shape[1]) * Locate_Show_Area_Width)         # 文本行显示区域 width
            new_height = int(((max(xs)-min(xs)) / src.shape[0]) * Locate_Show_Area_Height)       # 文本行显示区域 height

            roi_rects.append((x_loc, y_loc, new_width + 20, new_height + 10))                    # (x, y, width, height)
            cv.drawContours(src_rect, [rect_points], 0, (0, 255, 0), 2)

        roi_imgs = roi_imgs[::-1]
        roi_rects = roi_rects[::-1]

        return src_rect, roi_imgs, roi_rects   # 画出文本行轮廓的图, 文本行图像list, 轮廓图像坐标[(x, y, width, height)]










