
# Frameworks
import difflib
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


# 计算AR与CR
def calculate_ar_cr(label_str, pred_str):
    CR_correct_char = max(len(label_str), len(pred_str))
    AR_correct_char = max(len(label_str), len(pred_str))
    N = max(len(label_str), len(pred_str))
    # CR_correct_char = len(label_str)
    # AR_correct_char = len(label_str)
    for block in difflib.SequenceMatcher(None, label_str, pred_str).get_opcodes():
        label_m = block[2] - block[1]
        pred_m = block[4] - block[3]
        if block[0] == 'delete':
            CR_correct_char -= label_m
            AR_correct_char -= label_m
        elif block[0] == 'insert':
            AR_correct_char -= pred_m
        elif block[0] == 'replace':
            if label_m >= pred_m:
                CR_correct_char -= label_m
                AR_correct_char -= label_m
            elif label_m < pred_m:
                CR_correct_char -= label_m
                AR_correct_char -= pred_m
    return N, CR_correct_char, AR_correct_char