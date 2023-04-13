import geopandas as gpd
from osgeo import gdal,ogr,osr
# from osgeo.gdal import 
import numpy as np
import math
import os

# 读取shp文件为GeoDataFrame对象
shp_file = gpd.read_file(r"C:\Users\xdh\Documents\ZRZYB\fengji\风机标注样本成果\风机标注样本.shp")

# 读取tiff文件为numpy数组
tiff_file = gdal.Open(r"C:\Users\xdh\Documents\ZRZYB\风机.tif")
tiff_array = tiff_file.ReadAsArray()

# 定义目标坐标系（CGCS2000_GK_CM_87E）
target_srs = osr.SpatialReference()
target_srs.ImportFromEPSG(4525)

# 将shp文件投影变换为目标坐标系
shp_file = shp_file.to_crs(target_srs.ExportToWkt())

# 将tiff文件投影变换为目标坐标系
tiff_transform = tiff_file.GetGeoTransform()
tiff_srs = tiff_file.GetProjectionRef()
tiff_proj = osr.SpatialReference(wkt=tiff_srs)
tiff_proj.AutoIdentifyEPSG()
tiff_proj_epsg = tiff_proj.GetAuthorityCode(None)
tiff_transform = gdal.Warp("", tiff_file, format="VRT", srcSRS=tiff_srs, dstSRS="EPSG:" + tiff_proj_epsg, outputBounds=[-180, -90, 180, 90], xRes=0.01, yRes=0.01, resampleAlg=gdal.GRA_Bilinear).GetGeoTransform()
tiff_array = gdal.Warp("", tiff_file, format="VRT", srcSRS=tiff_srs, dstSRS="EPSG:" + tiff_proj_epsg, outputBounds=[-180, -90, 180, 90], xRes=0.01, yRes=0.01, resampleAlg=gdal.GRA_Bilinear).ReadAsArray()

# 计算shp文件和tiff文件的空间范围交集
shp_bounds = shp_file.total_bounds
tiff_bounds = (tiff_transform[0], tiff_transform[3] + tiff_array.shape[0] * tiff_transform[5], tiff_transform[0] + tiff_array.shape[1] * tiff_transform[1], tiff_transform[3])
intersection = (max(shp_bounds[0], tiff_bounds[0]), max(shp_bounds[1], tiff_bounds[1]), min(shp_bounds[2], tiff_bounds[2]), min(shp_bounds[3],tiff_bounds[3]))

#将交集区域切分为512*512的区域
x_min, y_min, x_max, y_max = intersection
x_size = math.ceil((x_max - x_min) / 512)
y_size = math.ceil((y_max - y_min) / 512)
splits = [(int(x_min + i * 512), int(y_min + j * 512), int(min(x_min + (i + 1) * 512, x_max)), int(min(y_min + (j + 1) * 512, y_max))) for i in range(x_size) for j in range(y_size)]

#将每个切分区域转换为tiff文件中对应的像素坐标，并将其保存为一张512*512的png图片
for i, split in enumerate(splits):
    x_offset = int((split[0] - tiff_transform[0]) / tiff_transform[1])
    y_offset = int((split[3] - tiff_transform[3]) / tiff_transform[5])
    x_size = int((split[2] - split[0]) / tiff_transform[1])
    y_size = int((split[1] - split[3]) / tiff_transform[5])
    split_array = tiff_array[y_offset:y_offset+y_size, x_offset:x_offset+x_size]
    split_array[split_array<0] = 0 # 将无效值替换为0
    png_array = np.zeros((512, 512), dtype=np.uint8)
    png_array[:split_array.shape[0], :split_array.shape[1]] = split_array
    png_file = f"split_{i}.png"
    os.makedirs(r"C:\Users\xdh\Desktop\preprocess_code\dst_shp\output_folder", exist_ok=True)
    png_path = os.path.join("output_folder", png_file)
    Image.fromarray(png_array).save(png_path)
    print("image")

print("All done!")