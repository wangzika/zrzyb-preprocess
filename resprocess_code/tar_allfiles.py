import os
import tarfile

# 获取当前目录
current_dir = os.getcwd()

# 遍历当前目录下的所有文件
for file_name in os.listdir(current_dir):
    # 判断文件是否以tar结尾
    if file_name.endswith('.tar'):
        # 打开tar文件
        tar = tarfile.open(file_name)
        # 解压tar文件
        tar.extractall()
        # 关闭tar文件
        tar.close()
