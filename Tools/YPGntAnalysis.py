

# Frameworks
import os
import numpy as np
import struct
from PIL import Image


# Global Constants
Data_path = "F:/研一上学期/工程实践准备/dataset/Gnt1.0Test"
files = os.listdir(Data_path)
# 用于字符和文件夹名字映射的字典
dict1 = {}
# 全局变量，文件夹名字
N = 0


# 格式说明
"""
GNT文件格式如下: (数据按如下顺序小端存储)
    Sample size  - 4B - gnt文件存储的字符图像大小
    Tag code(GB) - 2B - gnt文件对应的字符的GBK编码
    Width        - 2B - gnt文件对应的字符的图像的宽度
    Height       - 2B - gnt文件对应的字符的图像的高度
    Bitmap - Width * Height bytes - gnt文件对应的字符的图像信息(bitmap格式)
"""

# NumPy说明
"""
NumPy部分函数使用如下:
    
    # 1.fromfile()函数: 用文本或二进制文件中的数据构造数组,返回值为numpy数组
    fromfile(file,dtype=float,count=-1,sep='')
    
    
"""

# 读取 gnt 格式的文件
def read_gnt_file(path):

    global N
    # gnt文件的头部信息长度: 4B + 2B + 2B + 2B
    header_size = 10
    try:
        # 二进制方式打开文件
        f = open(path, 'rb')       
    except IOError:
        print("Error: 没有找到文件或读取文件失败!")
        f.close()   
        return

    # 图片目录和标签目录
    dir_name, base_name = os.path.split(path)
    label_dir = dir_name + '_label'
    image_dir = dir_name + '_images'
    if not os.path.exists(label_dir):
        os.makedirs(label_dir)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # num用来记录每个gnt文件解析出来的图片名字
    num = 0
    while True:
        # 读取gnt文件的头部信息
        header = np.fromfile(f, dtype='uint8', count=header_size)
        if not header.size: break
        # 获取Sample size - 4B - 数据为小端存储
        sample_size = header[0] + (header[1] << 8) + (header[2] << 16) + (header[3] << 24)
        # 获取Tag code - 2B - 数据为小端存储
        tag_code = header[5] + (header[4] << 8)
        # 获取width - 2B - 数据为小端存储
        width = header[6] + (header[7] << 8)
        # 获取height - 2B - 数据为小端存储
        height = header[8] + (header[9] << 8)
        if header_size + width * height != sample_size:
            break
        # 获取对应的图片信息
        image = np.fromfile(f, dtype='uint8', count=width * height).reshape((height, width))
        # 获取对应的汉字, 编码为gb18030
        tagcode_unicode = struct.pack('>H', tag_code).decode('gbk', 'ignore')

        # 记录出现过的单字符
        label_all_path = label_dir + "_all.txt"

        flag = True
        with open(label_all_path, 'r', encoding='UTF-8') as foo:
            for line in foo.readlines():
                if tagcode_unicode in line:
                    flag = False
                    break

        fp = open(label_all_path, 'a+', encoding='UTF-8')
        print(flag)
        if flag == True:
            N = N + 1
            dict1[tagcode_unicode] = N
            fp.write(tagcode_unicode)

        label_dir_now = label_dir + '/' + str(dict1[tagcode_unicode])
        image_dir_now = image_dir + '/' + str(dict1[tagcode_unicode])

        if not os.path.exists(label_dir_now):
            os.makedirs(label_dir_now)
        if not os.path.exists(image_dir_now):
            os.makedirs(image_dir_now)

        print(tagcode_unicode)
        
        im = Image.fromarray(image)

        #保存信息
        label_file = os.path.join(label_dir_now, base_name.replace('.gnt', str(num) + '.txt'))
        with open(label_file, 'w',encoding='UTF-8') as f1:
            f1.write(tagcode_unicode)
        bitmap_file = os.path.join(image_dir_now, base_name.replace('.gnt', str(num) + '.jpg'))
        num = num + 1
        im.convert('RGB').save(bitmap_file)


# main 函数
def main():
    for file in files:
        read_gnt_file(Data_path + "/" + file)


# 程序入口
if __name__ == "__main__":
    main()


























