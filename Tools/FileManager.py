

# Frameworks
import os



# 获取当前目录路径
def get_Curr_Dir():
    return os.getcwd()


# 获取文件夹内的所有图片路径
def get_Images_In_Dir(dir_path, img_list):
    # 路径检查
    if (os.path.isdir(dir_path) == False):
        print("原文件夹不存在, 请输入正确的路径!!!")
        return
    # 获取原文件夹下的所有文件
    ori_files = os.listdir(dir_path)
    for file in ori_files:
        # 忽略 macOS 系统文件
        if file == ".DS_Store":
            continue
        # 拼接成绝对路径
        file_path = os.path.join(dir_path, file)
        # 处理文件
        if os.path.isfile(file_path):
            if os.path.splitext(file)[1] in [".png", ".jpg"]:
                img_list.append(file_path)
        # 处理文件夹, 递归
        if os.path.isdir(file_path):
            get_Images_In_Dir(file_path, img_list)


