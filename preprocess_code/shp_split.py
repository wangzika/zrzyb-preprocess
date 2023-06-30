import geopandas as gpd
import pyproj
from osgeo import gdal,ogr

# 打开SHP文件
gdf = gpd.read_file('C:/Users/xdh/Documents/ZRZYB/fengji/风机标注样本成果/风机标注样本.shp')

# 定义SHP文件的坐标系（WGS84）

# 定义TIFF文件的投影坐标系（CGCS2000_GK_CM_87E）
# target_crs = pyproj.CRS('CGCS2000_GK_CM_87E')

# 将SHP文件的坐标系转换为投影坐标系
# gdf = gdf.to_crs(target_crs)

# 打开TIFF文件
# dataset = gdal.Open('C:/Users/xdh/Documents/ZRZYB/光伏2.tif')

# 获取TIFF文件的边界范围
# left, width, _, top, _, height = dataset.GetGeoTransform()
# right = left + (width * dataset.RasterXSize)
# bottom = top + (height * dataset.RasterYSize)

import os

# 获取所有TIFF文件的文件名
# import os
#所有tiff文件的路径
folder_path = "C:/Users/xdh/Documents/ZRZYB"  # 文件夹路径
files = os.listdir(folder_path)  # 获取文件夹中所有文件的文件名
tiff_files = [f for f in files if f.endswith(".tiff") or f.endswith(".tif")]  # 获取所有以tiff结尾的文件名
print(tiff_files)  # 输出所有以tiff结尾的文件名
#保存标准图幅大小shp文件的文件夹
save_dir=folder_path

# 循环处理每个TIFF文件
for tiff_file in tiff_files:
    # 拼接TIFF文件的完整路径
    tiff_path = os.path.join(folder_path, tiff_file)
    
    # 打开TIFF文件
    dataset = gdal.Open(tiff_path)
    # 获取tiff文件的投影坐标系
    wkt_projection=dataset.GetProjection()
    print(wkt_projection)
    proj=pyproj.proj(wkt_projection)#这个好像没用
    print('-------------------')

    #定义shp文件坐标系wgs84
    source_crs = pyproj.CRS('EPSG:4326')

    # 定义tiff文件投影坐标系
    target_crs=pyproj.CRS(wkt_projection)

    # 将SHP文件的坐标系转换为投影坐标系
    gdf=gdf.to_crs(target_crs)
    # 获取TIFF文件的边界范围
    left, width, _, top, _, height = dataset.GetGeoTransform()
    right = left + (width * dataset.RasterXSize)
    bottom = top + (height * dataset.RasterYSize)
    print(left,right,bottom,top)
    # 筛选出在TIFF文件边界范围内的要素
    gdf_selected = gdf.cx[left:right, bottom:top]
    if gdf_selected.empty:
        os.remove(tiff_path)
        print(tiff_file,":is delated!")
        continue
    print(gdf_selected)
    print('========================')
    
    # 将筛选后的要素保存为新的SHP文件，并以TIFF文件名字命名
    output_path = os.path.join(save_dir, f'{os.path.splitext(tiff_file)[0]}.shp')
    gdf_selected.to_file(output_path)




    



