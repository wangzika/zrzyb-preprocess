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

size=input("请输入外扩切分范围(必须为整数默认为0)：")
# if data_type=="fengji":
#     dir=r"shp_tiff_save_dir"
# else data_type=="guangfu":
    
# else:
#     return
dir=r"C:\Users\wzb\Desktop\样例"
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
    print(layer)
    srs = layer.GetSpatialRef()
    #获得每个shp文件的边界
    shp_left, shp_right, shp_bottom, shp_top = layer.GetExtent()
    # 获得每个tiff文件边界
    tiff_path=os.path.join(dir, f'{os.path.splitext(shp_file)[0]}.tif')
    print("tiff_path:",tiff_path)
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

    # print(overlap)
    #计算像素坐标  
    pixel_size = transfrom[1]  # cgcs下像素大小2，wgs84是个小鼠
    print("像素大小：",pixel_size)
    xres = yres = pixel_size
    # xoff,yoff=overlap[0]
    # print("overlap[1] - overlap[0]:",overlap[1],overlap[0])
    xoff, yoff = overlap[0], overlap[3]
    cols = int(np.ceil((overlap[1] - overlap[0]) / pixel_size))
    rows = int(np.ceil((overlap[3] - overlap[2]) / pixel_size))
    print(cols,rows)
    # 将每个几何图形转换为图像中的像素坐标   print(feature.GetFieldAsString("wybm"))获取属性表
    from shapely.geometry import Polygon
    from shapely.ops import transform
    pixel_coords = []
    poly_list=[]
    boundingRect_list=[]
    for feature in layer:
        geom = feature.GetGeometryRef()
        #属性表
        name=feature.GetFieldAsString("wybm")
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
            #获取外界矩形  poly.bounds 
            # boundingRect_list=cv2.boundingRect(poly)

            #==============新加的代码
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


            #新建图片 image 全黑蒙版  img_result 用于保存目标区域图片
            image = np.zeros((int(poly.bounds[3]-poly.bounds[1]),int(poly.bounds[2]-poly.bounds[0]),3), dtype=np.uint8)
            img_result = np.zeros((int(poly.bounds[2]-poly.bounds[0]+float(size)), int(poly.bounds[3]-poly.bounds[1]+float(size)),3), dtype=np.uint8)
            img_result_b = np.zeros((int(poly.bounds[2]-poly.bounds[0]+float(size)), int(poly.bounds[3]-poly.bounds[1]+float(size)),3), dtype=np.uint8)

            # mask = np.zeros((rows, cols,3), dtype=np.uint8)
            Image.MAX_IMAGE_PIXELS=None

            # 读取tif文件并转换为numpy数组
            img = Image.open(tiff_path)
            img_arr = np.array(img)

            # 定义平移量
            dx = int(TIFF_Xtransform) # x轴平移量
            dy = int(TIFF_Ytransform) # y轴平移量

            # 创建一个更大的numpy数组，用于保存平移后的图像  波段为3
            new_img_arr = np.zeros((int(img_arr.shape[0] + dy), int(img_arr.shape[1] + dx),3), dtype=img_arr.dtype)
            new_img_arr_mask = np.zeros((int(img_arr.shape[0] + dy), int(img_arr.shape[1] + dx),3), dtype=img_arr.dtype)

            # 将原始图像平移并保存到新的numpy数组中
            new_img_arr[dy:, dx:] = img_arr


            #将目标区域图片放在新的图片int(poly.bounds[0]):int(poly.bounds[2])
            img_result_b=new_img_arr[int(poly.bounds[1]+dy-float(size)):int(poly.bounds[3]+dy+float(size)),int(poly.bounds[0]+dx-float(size)):int(poly.bounds[2]+dx+float(size))]
            # img_result_b=masked_image[int(poly.bounds[1]+dy-float(size)):int(poly.bounds[3]+dy+float(size)),int(poly.bounds[0]+dx-float(size)):int(poly.bounds[2]+dx+float(size))]
            cropped_image_b = Image.fromarray(img_result_b)
            cropped_image_b.save(f'C:/Users/wzb/Documents/GitHub/zrzyb-preprocess/res/{name}_b.png')

            # cv2.imshow("src",img_result)
            # cv2.waitKey(0)

            # new_img = Image.fromarray(img_result)
            # new_img.save("光伏1.png")
            pts = np.array(poly.exterior.coords[:-1], np.int32)
            cv2.fillPoly(new_img_arr_mask, [pts], color=(255, 255, 255))
            masked_image=cv2.bitwise_and(new_img_arr,new_img_arr_mask)

            #将目标区域图片放在新的图片int(poly.bounds[0]):int(poly.bounds[2])
            # img_result=masked_image[int(poly.bounds[1]+dy-float(size)):int(poly.bounds[3]+dy+float(size)),int(poly.bounds[0]+dx-float(size)):int(poly.bounds[2]+dx+float(size))]
            img_result=masked_image[int(poly.bounds[1]+dy):int(poly.bounds[3]+dy),int(poly.bounds[0]+dx):int(poly.bounds[2]+dx)]

            # cv2.imshow("src",img_result)
            # cv2.waitKey(0)
            # 切分图像为512x512的小图像
            # 创建裁剪后的图像
            cropped_image = Image.fromarray(img_result)
            cropped_image.save(f'C:/Users/wzb/Documents/GitHub/zrzyb-preprocess/res/{name}.png')
            
            #==============新加的代码

            pixel_coords.append(poly.exterior.coords[:-1])
    # print(pixel_coords.count)
    # 创建新的图像=============
#     image = np.zeros((rows, cols,3), dtype=np.uint8)

#     # 绘制几何图形
#     for coords in pixel_coords:
#         # boundingRect_list=cv2.boundingRect(coords)
#         pts = np.array(coords, np.int32)
#         cv2.fillPoly(image, [pts], color=(255, 255, 255))

#     # 将图像转换为二值图像
#     # thresh, binary_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY)
    
#     # img = cv2.imread(r'c:\Users\wzb\Desktop\样例\GF1D_PMS_E120.6_N30.8_20220503_1.tif')
    
   

#     # 创建一个全0的numpy数组存储tiff文件
#     # data = np.zeros((rows, cols), dtype=np.int32)

#     #判断shp左上角大还是tiff文件左上角大
#     if shp_left<tiff_left:
#         TIFF_Xtransform=(tiff_left-shp_left)/pixel_size
#     else:
#         TIFF_Xtransform=0
#     if shp_top>tiff_top:
#         TIFF_Ytransform=(shp_top-tiff_top)/pixel_size
#     else:
#         TIFF_Ytransform=0
#          #切分tiff文件
#     # import numpy as np

#     from PIL import Image


#     Image.MAX_IMAGE_PIXELS=None

#     # 读取tif文件并转换为numpy数组
#     img = Image.open(tiff_path)
#     img_arr = np.array(img)

#     # 定义平移量
#     dx = int(TIFF_Xtransform) # x轴平移量
#     dy = int(TIFF_Ytransform) # y轴平移量

#     # 创建一个更大的numpy数组，用于保存平移后的图像  波段为3
#     new_img_arr = np.zeros((int(img_arr.shape[0] + dy), int(img_arr.shape[1] + dx),3), dtype=img_arr.dtype)

#     # 将原始图像平移并保存到新的numpy数组中
#     new_img_arr[dy:, dx:] = img_arr
#     new_img = Image.fromarray(new_img_arr)
#     # new_img.save("光伏1.png")

#     masked_image=cv2.bitwise_and(new_img_arr,image)
#     cv2.imshow("src",masked_image)
#     cv2.waitKey(0)
#     # 切分图像为512x512的小图像
#    # 创建裁剪后的图像
#     cropped_image = Image.fromarray(masked_image)

#     # 保存结果图像  shp_file)[0]
#     # cropped_image.save('C:\Users\wzb\Documents\GitHub\zrzyb-preprocess\output_image.jpg')
#     cropped_image.save(f'C:/Users/wzb/Documents/GitHub/zrzyb-preprocess/{os.path.splitext(shp_file)[0]}.png')
    

    


