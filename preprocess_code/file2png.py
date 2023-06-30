#前提条件shp，tiff文件在一个文件夹下
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

# 定义转换函数
def shp_to_pixel_coord(x, y):
    """将shp文件中的坐标转换为像素坐标"""
    x_pix = int((x - xoff) / xres)
    y_pix = int((yoff - y) / yres)
    return x_pix, y_pix

for shp_file in shp_files:
    #获得每个shp文件的路径
    shp_path = os.path.join(dir, shp_file)
    # gdf_f = gpd.read_file(shp_path)
    shp = ogr.Open(shp_path)
    layer = shp.GetLayer()
    srs = layer.GetSpatialRef()
    #获得每个shp文件的边界
    shp_left, shp_bottom, shp_right, shp_top = layer.GetExtent()
    # 获得每个tiff文件边界
    tiff_path=os.path.join(dir, f'{os.path.splitext(shp_file)[0]}.tiff')
    dataset = gdal.Open(tiff_path)
    transfrom=dataset.GetGeoTransform()
    
    # 获取TIFF文件的边界范围
    tiff_left, width, _, tiff_top, _, height = dataset.GetGeoTransform()
    tiff_right = tiff_left + (width * dataset.RasterXSize)
    tiff_bottom = tiff_top + (height * dataset.RasterYSize)
    # tiff_left, tiff_right, tiff_bottom, tiff_top=left,right,bottom,top
    #最大外界矩形
    overlap = (
    min(shp_left, tiff_left),
    max(shp_right, tiff_right),
    min(shp_bottom, tiff_bottom),
    max(shp_top, tiff_top),)


    #计算像素坐标  
    pixel_size = transfrom[1]  # cgcs下像素大小2，wgs84是个小鼠
    print("像素大小：",pixel_size)
    xres = yres = pixel_size
    # xoff,yoff=overlap[0]
    xoff, yoff = overlap[0], overlap[3]
    cols = int(np.ceil((overlap[1] - overlap[0]) / pixel_size))
    rows = int(np.ceil((overlap[3] - overlap[2]) / pixel_size))
    
    # 将每个几何图形转换为图像中的像素坐标
    from shapely.geometry import Polygon
    from shapely.ops import transform
    pixel_coords = []
    poly_list=[]
    for feature in layer:
        geom = feature.GetGeometryRef()
        if geom is None:
            continue
        if geom.GetGeometryType() == ogr.wkbPolygon:
            # 转换为Shapely的Polygon对象
            exterior_ring = geom.GetGeometryRef(0)
            # for pt in exterior_ring.GetPoints():
            #     poly=Polygon(pt[0], pt[1])
            # poly = Polygon([(pt[0], pt[1]) for pt in exterior_ring.GetPoints()])
            poly = Polygon([(pt[0], pt[1]) for pt in exterior_ring.GetPoints()])
            # 转换为像素坐标
            # for i in poly:
            #     polys=shp_to_pixel_coord(i[0],i[1])
            #     poly_list.append(polys)
            poly = transform(shp_to_pixel_coord, poly)
            pixel_coords.append(poly.exterior.coords[:-1])

    # 创建新的图像
    image = np.zeros((rows, cols), dtype=np.uint8)

    # 绘制几何图形
    for coords in pixel_coords:
        pts = np.array(coords, np.int32)
        cv2.fillPoly(image, [pts], color=(255, 255, 255))

    # 将图像转换为二值图像
    thresh, binary_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY)

    # 切分shp文件
    block_size=512
    for i in range(0, rows, block_size):
        for j in range(0, cols, block_size):
            # 提取块
            block = binary_image[i:i+block_size, j:j+block_size]
            # 忽略空白块
            if block.sum() == 0:
                continue
            # 调整块大小
            block = cv2.resize(block, (block_size, block_size), interpolation=cv2.INTER_NEAREST)
            # 保存块
            label=[i,j]
            labels.append(label)
            if data_type=="fengji":
                cv2.imwrite(f'C:/Users/xdh/Desktop/dataset/fengji/labels/img_binary/{os.path.splitext(shp_file)[0]_{i}_{j}.png}', block)
            else:
                cv2.imwrite(f'')

    print('shp save done in shp_512')
    # 创建一个全0的numpy数组存储tiff文件
    data = np.zeros((rows, cols), dtype=np.int32)

    #判断shp左上角大还是tiff文件左上角大
    if shp_left<tiff_left:
        TIFF_Xtransform=(tiff_left-shp_left)/pixel_size
    else:
        TIFF_Xtransform=0
    if shp_top>tiff_top:
        TIFF_Ytransform=(shp_top-tiff_top)/pixel_size
    else:
        TIFF_Ytransform=0


    #切分tiff文件
    # import numpy as np
    from PIL import Image

    # 读取tif文件并转换为numpy数组
    img = Image.open(tiff_path)
    img_arr = np.array(img)

    # 定义平移量
    dx = int(TIFF_Xtransform) # x轴平移量
    dy = int(TIFF_Ytransform) # y轴平移量

    # 创建一个更大的numpy数组，用于保存平移后的图像  波段为3
    new_img_arr = np.zeros((int(img_arr.shape[0] + dy), int(img_arr.shape[1] + dx),3), dtype=img_arr.dtype)

    # 将原始图像平移并保存到新的numpy数组中
    new_img_arr[dy:, dx:] = img_arr
    new_img = Image.fromarray(new_img_arr)
    # new_img.save("光伏1.png")

    # 切分图像为512x512的小图像
    block_size = 512

    for lab in labels:#忽略空白块
        for i in range(0,rows,block_size):
            if i!=lab[0]:#忽略空白块
                continue
            for j in range(0,rows,block_size):
                if j!=lab[1]:#忽略空白块
                    continue
                #提取块
                block=new_img_arr[i:i+block_size,j:j+block_size]
                try:
                    #调整块大小
                    block=cv2.resize(block,(block_size,block_size),interpolation=cv2.INTER_NEAREST)
                    #保存块
                    tile_img=Image.fromarray(block)
                    if data_type=="fengji":
                        tile_img.save(f'C:/Users/xdh/Desktop/dataset/fengji/images/train/{os.path.splitext(shp_file)[0]_{i}_{j}.png}')
                    else:
                        tile_img.save(f'C:/Users/xdh/Desktop/dataset/guangfu/images/train/{os.path.splitext(shp_file)[0]_{i}_{j}.png}')
                except:
                    if data_type=='fengji':
                        print(f'C:/Users/xdh/Desktop/dataset/fengji/images/train/{os.path.splitext(shp_file)[0]_{i}_{j}.png}')
                        os.remove(f'C:/Users/xdh/Desktop/dataset/fengji/labels/img_binary/{os.path.splitext(shp_file)[0]_{i}_{j}.png}')
                        continue
                    else:
                        print(f'C:/Users/xdh/Desktop/dataset/guangfu/images/train/{os.path.splitext(shp_file)[0]_{i}_{j}.png}')
                        os.remove(f'C:/Users/xdh/Desktop/dataset/guangfu/labels/img_binary/{os.path.splitext(shp_file)[0]_{i}_{j}.png}')
                        continue

    print('tiff_saved')
    print("===================finish===================")

    



