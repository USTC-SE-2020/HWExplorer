
# Frameworks
import cv2 as cv
from PyQt5.QtGui import QImage


# 将openCV中的mat转为QT中的QImage
def convert_mat_To_QImage(mat):
    shrink = cv.cvtColor(mat, cv.COLOR_BGR2RGB)
    qImg = QImage(shrink.data,
                  shrink.shape[1],
                  shrink.shape[0],
                  shrink.shape[1] * 3,
                  QImage.Format_RGB888)
    return qImg

# 批量将mat数组转为QImage数组
def convert_mats_To_QImages(mats):
    res_list = []
    for mat in mats:
        res = convert_mat_To_QImage(mat)
        res_list.append(res)
    return res_list