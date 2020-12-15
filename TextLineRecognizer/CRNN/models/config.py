import json

# 图片大小
OUTPUT_SHAPE = (32,320,3)

#项目路径
WORK_PATH = '/Users/soyou/Documents/EProjects/HWExplorer/'

#测试文件目录
TEST_PATH = WORK_PATH + 'dataset/test/'

#字符映射表
TABLE_PATH = WORK_PATH + "TextLineRecognizer/CRNN/dataset/table.txt"
JSON_PATH = WORK_PATH + "TextLineRecognizer/CRNN/dataset/char.json"
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    chardic = json.load(f)
with open(TABLE_PATH, 'w', encoding='utf-8') as fw:
    for char in chardic:
        fw.write(char+'\n')

#字符数
NUM_CLASSES = len(chardic) + 3


#数据集参数
BATCH_SIZE = 256
BUFFER_SIZE = 10000


#模型保存与否
is_save_model = False

#保存模型版本号
version = 1

#模型保存地址
export_path = WORK_PATH + 'TextLineRecognizer/CRNN/output/crnn/{0}'.format(str(version))