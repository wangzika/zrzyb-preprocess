# 根据列表中文件名将一个文件夹中文件复制到另一个文件夹
import shutil
import geopandas as gpd
import os 

# 读取shp文件
shp_path = r'C:\Users\xdh\Documents\自然资源部\风机标注样本成果\风机标注样本成果\风机标注样本.shp'
gdf = gpd.read_file(shp_path)

# 获取所有不同的imageName值
image_names = gdf['imageName'].unique()

#文件原始文件夹
source_dir=r''
#将文件复制到目标文件夹
target_dir=r''
# 根据imageName值切分shp文件
for filename in os.listdir(source_dir):
    for image_name in image_names:
        if image_name in filename:
            file_path=os.path.join(source_dir,filename)
            if not os.path.exists(os.path.join(target_dir,filename)):
                # 将文件复制到文件夹中
                shutil.copy(file_path,target_dir)
                print(file_path)
print("finish")
    
