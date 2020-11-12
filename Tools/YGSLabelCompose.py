import os

filedir = 'F:/研一上学期/工程实践准备/dataset/temp_label/'

def txt_compose(filedir, m):
    # 获取当前文件夹中的文件名称列表
    filenames = os.listdir(filedir)
    # 在指定目录下创建txt文件 --其中txt的文件名需要进行计数
    f = open('F:/研一上学期/工程实践准备/dataset/final_label/' + str(m) + '.txt', 'w', encoding='UTF-8')
    # 先遍历文件名
    for filename in filenames:
        filepath = filedir + filename
        # 遍历单个文件，读取行数
        for line in open(filepath, encoding='UTF-8'):
            f.write(line)
    # 关闭文件
    f.close()