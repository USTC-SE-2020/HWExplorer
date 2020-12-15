
# Frameworks
import cv2 as cv
import numpy as np

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
        roi_imgs = []
        for contours in contours_list:
            rotated_rect = cv.minAreaRect(contours)
            rect_points = cv.boxPoints(rotated_rect)
            rect_points = np.int0(rect_points)
            xs = [x[1] for x in rect_points]
            ys = [y[0] for y in rect_points]
            # 忽略外接矩形在图像外的子区域
            if (min(xs) < 0) or (max(xs) < 0) or (min(ys) < 0) or (max(ys) < 0):
                continue
            src_roi = src[min(xs):max(xs), min(ys):max(ys)]         # 截取外接矩形区域
            roi_imgs.append(src_roi)
            cv.drawContours(src_rect, [rect_points], 0, (0, 255, 0), 2)
        return src_rect, roi_imgs   # 画出文本行轮廓的图, 文本行图像list




# TODO: 测试

# /Users/soyou/Desktop/11/23D3AE31C8A3236C664222100D69ADDC.jpg
# /Users/soyou/Desktop/11/48E4C457ECE1B94C6588B9E9DF061C3F.jpg
# /Users/soyou/Desktop/11/364EADA55771093126867349F22C3326.jpg
# /Users/soyou/Desktop/11/B38FADCBF661A2AA7392EE5CB2F6F22F.jpg
# /Users/soyou/Desktop/11/D56BDE7494C9C1495EDC1AE084303601.jpg
# /Users/soyou/Desktop/11/D05123EAFBF9542B944F801F1037F674.jpg
# /Users/soyou/Desktop/11/FE2BD83D5351148175B35F507BD19066.jpg


img_path = "/Users/soyou/Desktop/11/FE2BD83D5351148175B35F507BD19066.jpg"
locater = TextLineLocator()
rect, _ = locater.locate_textLine_with_cv(img_path)
cv.imshow("1", rect)
#
# for i, img in enumerate(roi_imgs):
#     cv.imshow("roi{}".format(i), img)

k = cv.waitKey(0)
if k == 27:
    cv.destroyAllWindows()







