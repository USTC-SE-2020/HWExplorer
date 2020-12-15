

import cv2
import numpy as np

# /Users/soyou/Desktop/11/23D3AE31C8A3236C664222100D69ADDC.jpg
# /Users/soyou/Desktop/11/48E4C457ECE1B94C6588B9E9DF061C3F.jpg
# /Users/soyou/Desktop/11/364EADA55771093126867349F22C3326.jpg
# /Users/soyou/Desktop/11/B38FADCBF661A2AA7392EE5CB2F6F22F.jpg
# /Users/soyou/Desktop/11/D56BDE7494C9C1495EDC1AE084303601.jpg
# /Users/soyou/Desktop/11/D05123EAFBF9542B944F801F1037F674.jpg
# /Users/soyou/Desktop/11/FE2BD83D5351148175B35F507BD19066.jpg
# /Users/soyou/Desktop/11/D791962E6C315B8144CEABCDECA7D1FD.jpg

img_path = "/Users/soyou/Desktop/11/D791962E6C315B8144CEABCDECA7D1FD.jpg"


Min_Contours_Area = 5 * 5
Max_Contours_Area = 100 * 100

# 移除不符合条件的轮廓
def remove_improper_contours(contours):
    res_contours = []
    for cont in contours:
        area = cv2.contourArea(cont)
        if area < Min_Contours_Area:
            continue
        if area > Max_Contours_Area:
            continue
        res_contours.append(cont)
    return res_contours



# 移除水平线
def remove_horizontal_lines():
    # 0.读取图像
    image = cv2.imread(img_path)

    # 1.转换成灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2.Otsu's二值化
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # 3.用特殊的水平kernel检测灰度图中的水平线
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # 4.找轮廓
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(image, [c], -1, (255, 255, 255), 2)

    # 5.修复原图像
    repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 6))
    result = 255 - cv2.morphologyEx(255 - image, cv2.MORPH_CLOSE, repair_kernel, iterations=1)

    # 6.展示结果图像
    cv2.imshow('thresh', thresh)
    cv2.imshow('detected_lines', detected_lines)
    cv2.imshow('image', image)
    cv2.imshow('result', result)
    cv2.waitKey()


# 移除图像中的水平和垂直线
def remove_all_lines(image):

    result = image.copy()

    # 1.转换成灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2.Otsu's二值化
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # 3.用特殊的水平kernel检测灰度图中的水平线
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255, 255, 255), 2)       # 填充水平线

    # 4.用特殊的垂直kernel检测灰度图中的垂直线
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    remove_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255, 255, 255), 2)       # 填充垂直线

    return result

 # 基于openCV定位文本行
def locate_textLine_with_cv(src, image):

    # 读取灰度图像
    src_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 二值化
    src_thresh = cv2.threshold(src_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    cv2.imshow("thresh", src_thresh)

    # # 4.用特殊的垂直kernel检测灰度图中的文字
    # text_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    # src_texts = cv2.morphologyEx(src_thresh, cv2.MORPH_OPEN, text_kernel, iterations=2)

    # 闭运算
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    src_closed = cv2.morphologyEx(src_thresh, cv2.MORPH_CLOSE, element)
    cv2.imshow("texts", src_closed)

    # 取轮廓
    cnts = cv2.findContours(src_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    cnts = remove_improper_contours(cnts)

    for c in cnts:
        rotated_rect = cv2.minAreaRect(c)
        rect_points = cv2.boxPoints(rotated_rect)
        rect_points = np.int0(rect_points)
        cv2.drawContours(src, [rect_points], 0, (0, 255, 0), 2)

    cv2.imshow("res", src)
    cv2.waitKey()



def main():

    # 读取图像
    image = cv2.imread(img_path)

    # 移除水平和垂直线
    img_no_lines = remove_all_lines(image)
    cv2.imshow("no-lines", img_no_lines)

    locate_textLine_with_cv(image, img_no_lines)


    pass


if __name__ == '__main__':
    main()