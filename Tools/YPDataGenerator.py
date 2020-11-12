import os
import shutil
import random

# 全局变量
from Tools.YGSDeleteDir import deletetxt_image
from Tools.YGSFileMove import startimagefile, moveFile
from Tools.YGSImageCompose import image_compose
from Tools.YGSLabelCompose import txt_compose

data_path = "F:/研一上学期/工程实践准备/dataset/HWDB2.0Test_label"
files = os.listdir(data_path)
image_path = "F:/研一上学期/工程实践准备/dataset/Gnt1.0Test_images"
files_image = os.listdir(image_path)
label_path = "F:/研一上学期/工程实践准备/dataset/Gnt1.0Test_label"
files_label = os.listdir(label_path)
dict_char = {}  # 映射每一个字符和它的数量
count = 0  # 字符种类数
root = "F:/研一上学期/工程实践准备/dataset/"  # 文件夹根目录
k = 1  # k用来复制文件夹，首先只在1000多个字符中处理

#需要传入源图片以及标签路径参数 （其中 具体文件夹编号需要用变量存储
startimagefile ='F:/研一上学期/工程实践准备/dataset/generate_image/' #源图片文件夹路径
starttxtfile = 'F:/研一上学期/工程实践准备/dataset/generate_label/'  #源图片标签路径

#目的图片以及标签路径可以指定
endtimagefile = 'F:/研一上学期/工程实践准备/dataset/temp_image/'    #目的文件夹路径
endttxtfile= 'F:/研一上学期/工程实践准备/dataset/temp_label/'  #目的图片标签路径


def char_count(filename, fo):
    global count
    with open(filename, 'r', encoding='UTF-8') as fp:
        for line in fp.readlines():
            line = line.strip()
            for c in line:
                if c not in dict_char:
                    dict_char[c] = 0
                    fo.write(c)
                    count = count + 1
                dict_char[c] = dict_char[c] + 1
                # print(c + ':' + str(dict_char[c]))


def file_copy(path, target_path, str):  # 将path目录下所有以str结尾的文件复制到targe_path
    if not os.path.exists(target_path):
        # 如果目标路径不存在原文件夹的话就创建
        os.makedirs(target_path)

    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(str):  # 若文件名结尾是以jpg结尾，则复制到新文件夹
                list1 = (os.path.join(root,name))  # list是jpg文件的全路径
                shutil.copy(list1, target_path)  # 将jpg文件复制到新文件夹


def selection_dir(label_filename):
    global k
    lf = os.listdir(label_filename)
    for file in lf:
        n = 0
        flag = False
        file_list = os.listdir(label_filename + '/' + file)
        for sub_file in file_list:
            with open(label_filename + '/' + file + '/' + sub_file, 'r', encoding='UTF-8') as f:
                content = f.read()
                print(content)
            with open(root + 'all.txt', 'r', encoding='UTF-8') as f3:
                for line in f3.readlines():
                    if content in line:
                        flag = True
                        break
                print(flag)
                break
            break
        if flag:
            # file_copy(label_filename + '/' + str(file), root + 'generate_label/' + str(k), 'txt')
            # file_copy(image_path + '/' + str(file), root + 'generate_image/' + str(k), 'jpg')
            k = k + 1
            print(k)


if __name__ == '__main__':
    # f = open(data_path + '/all.txt', 'w', encoding='UTF-8')
    # f1 = open(data_path + '/all.txt', 'a+', encoding='UTF-8')
    # for file in files:
    #     char_count(data_path + '/' + file, f1)

    # print("按字符出现次数由小到大排序：")
    # dict_now = dict(sorted(dict_char.items(), key=operator.itemgetter(1)))
    # for k, v in dict_now.items():
    #     print(k + ':' + str(v))
    # print("总共有:", count, "种字符")
    # selection_dir(label_path)

    for p in range(8109, 10000):
        print(p)
        i = 10
        for j in range(i):
            q = random.randint(1, 1126)
            moveFile(startimagefile + str(q) + '/', starttxtfile + str(q) + '/')
        image_compose(i, 'F:/研一上学期/工程实践准备/dataset/temp_image/', ['.jpg', '.JPG'],
                      'F:/研一上学期/工程实践准备/dataset/final_image/' + str(p + 1) + '.jpg')  # 调用函数
        txt_compose('F:/研一上学期/工程实践准备/dataset/temp_label/', p + 1)
        deletetxt_image(endttxtfile)
        deletetxt_image(endtimagefile)
    # for i in range(random.randint(5, 30)):
    #     for j in range(10):
    #         print(j)
    # 2066
