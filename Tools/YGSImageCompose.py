import PIL.Image as Image

import os

# IMAGE_COLUMN=24 #待拼接图片个数
#
# IMAGES_PATH = 'E:\\picture\\test2\\'  # 图片所在文件夹
#
# IMAGES_FORMAT = ['.jpg', '.JPG']  # 图片格式
#
# IMAGE_SAVE_PATH = 'E:\\picture\\test2\\final.jpg'  # 合成后的图片存放地址


# 定义图像拼接函数
def image_compose(IMAGE_COLUMN,IMAGES_PATH,IMAGES_FORMAT,IMAGE_SAVE_PATH):#传入参数为 待拼接的图片个数  图片所在文件夹地址 图片格式 合成后的图片存放地址
    # 获取图片集地址下的所有图片名称
    image_names = [name for name in os.listdir(IMAGES_PATH) for item in IMAGES_FORMAT if
                   os.path.splitext(name)[1] == item]
    #循环遍历图片，计算出所有图片的总宽度以及总高度（求平均高度）
    sumw = 0
    sumh = 0
    for x in range(0, IMAGE_COLUMN):
        im=Image.open(IMAGES_PATH + image_names[x]) #读取文件
        sumw=sumw+im.size[0] #sumw存放所有图片的总宽度
        sumh=sumh+im.size[1] #sumh存放所有图片的总高度
    IMAGE_SIZE_H = int(sumh/IMAGE_COLUMN) #计算平均高度
    to_image = Image.new('RGB', (sumw, IMAGE_SIZE_H))  # 创建一个新图
    # 循环遍历，把每张图片按顺序粘贴到对应位置上
    tempx= 0
    tempy=0
    for x in range(0, IMAGE_COLUMN):
        im=Image.open(IMAGES_PATH + image_names[x])
        from_image = Image.open(IMAGES_PATH + image_names[x]).resize((im.size[0], IMAGE_SIZE_H), Image.ANTIALIAS)  #用于下一步传参数
        to_image.paste(from_image, (tempx, tempy)) #由于高度固定 则纵坐标tempy始终为0
        # im.paste(image, position)---粘贴image到im的position（左上角）位置。
        tempx = tempx + im.size[0] #tempx 表示横坐标 初始为0 每复制一张图片 那么下一张图片的起点复制位置 需要加前面已经复制好的图片的宽度

    return to_image.save(IMAGE_SAVE_PATH)  # 保存新图