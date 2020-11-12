#此函数用来从指定文件夹中 随机获取其中一张图片以及标签 存放到指定文件夹中
import os, random, shutil

#需要传入源图片以及标签路径参数 （其中 具体文件夹编号需要用变量存储
startimagefile ='F:/研一上学期/工程实践准备/dataset/test_image/' #源图片文件夹路径
starttxtfile = 'F:/研一上学期/工程实践准备/dataset/test_label/'  #源图片标签路径

#目的图片以及标签路径可以指定
endtimagefile = 'F:/研一上学期/工程实践准备/dataset/temp_image/'    #目的文件夹路径
endttxtfile= 'F:/研一上学期/工程实践准备/dataset/temp_label/'  #目的图片标签路径

def moveFile(startimagefile, starttxtfile):
        imagepath = os.listdir(startimagefile)    #取图片的原始路径
        sample = random.sample(imagepath, 1)  #随机选取1个样本图片
        for name in sample:
                shutil.copy(startimagefile + name, endtimagefile+name)
                #print(startimagefile + name)
                shutil.copy(starttxtfile + str(name).replace('.jpg', '.txt'), endttxtfile + str(name).replace('.jpg', '.txt'))
                #print(starttxtfile + str(name).replace('.jpg', '.txt'))

        return