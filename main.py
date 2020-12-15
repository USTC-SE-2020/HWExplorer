# Frameworks
from GUI import YSGUIEntrance as YSGUI
from TextLineRecognizer.YSRecognizer import Recognizer


# main函数
def main():
    # 1.启动程序主窗口
    YSGUI.start_GUI_Window()
    # 2.初始化单例对象
    recognizer = Recognizer()


# 程序入口
if __name__ == '__main__':
    main()






















