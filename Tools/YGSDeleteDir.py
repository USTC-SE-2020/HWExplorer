import os
import shutil

#需要执行两次 分别删除标签以及图片
#delDir = 'F:/研一上学期/工程实践准备/dataset/temp_label/'
def deletetxt_image(delDir):
    delList = []
    delList = os.listdir(delDir )
    for f in delList:
        filePath = os.path.join( delDir, f )
        if os.path.isfile(filePath):
            os.remove(filePath)
        elif os.path.isdir(filePath):
            shutil.rmtree(filePath,True)