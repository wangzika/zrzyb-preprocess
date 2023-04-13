import os
import shutil

# 指定文件夹路径
folder_path = r'C:\Users\xdh\Desktop\preprocess_code\object_detection'

# 指定目标文件夹路径
target_folder_path = r'C:\Users\xdh\Desktop'

# 获取指定文件夹里所有test名称的文件
for filename in os.listdir(folder_path):
    if 'shp_ds' in filename:
        # 构造文件路径
        file_path = os.path.join(folder_path, filename)
            # 判断文件是否已经存在于目标文件夹中
        if not os.path.exists(os.path.join(target_folder_path, filename)):
            # 将文件移动到指定文件夹
            shutil.copy(file_path, target_folder_path)
print("finsh")