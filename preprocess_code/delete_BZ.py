#删除shp文件中特定的字段
import os
import geopandas as gpd
import pyproj
from osgeo import gdal,ogr
import numpy as np
import cv2

def end_allfile(dir,end_string):
    folder_path = dir  # 文件夹路径
    files = os.listdir(folder_path)  # 获取文件夹中所有文件的文件名
    f_files = [f for f in files if f.endswith(end_string) or f.endswith(end_string)]  # 获取所有以tiff结尾的文件名
    print(f_files)  # 输出所有以tiff结尾的文件名
    return f_files

data_type=input("请输入切分类型：fengji or guangfu")
if data_type=="fengji":
    dir=r"shp_tiff_save_dir"
else data_type=="guangfu":
    dir=r""
else:
    return

shp_files=end_allfile(dir,"shp")
tiff_files=end_allfile(dir,"tiff")

for shp_file in shp_files:
    #获得每个shp文件的路径
    shp_path=os.path.join(dir,shp_file)
    shp_ds=ogr.Open(shp_path,1)
    shp_layer=shp_ds.GetLayer(0)

    query="BZ='???-??'"

    shp_layer.SetAttributeFilter(query)

    for feature in shp_layer:
        shp_layer.DeleteFeature(feature.GetFID())

    shp_ds.SyncToDisk()