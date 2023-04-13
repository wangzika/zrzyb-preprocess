from osgeo import ogr, gdal
from shapely.geometry import Polygon
from shapely.ops import transform
import numpy as np
import cv2


tiff_path = r'C:\Users\xdh\Documents\ZRZYB\光伏2.tif'
tiff_ds = gdal.Open(tiff_path)
transform = tiff_ds.GetGeoTransform()
# 打开shp文件
shp = ogr.Open(r'C:\Users\xdh\Documents\ZRZYB\res\output_file_G47E002022-DOM-202004.shp')
layer = shp.GetLayer()

# 获取空间参考和边界框信息
srs = layer.GetSpatialRef()
xmin, xmax, ymin, ymax = layer.GetExtent()

# 将边界框信息转换为像素坐标
pixel_size = transform[1]  # 像素大小
xres = yres = pixel_size
xoff, yoff = xmin, ymax
cols = int(np.ceil((xmax - xmin) / pixel_size))
rows = int(np.ceil((ymax - ymin) / pixel_size))

# 定义转换函数
def shp_to_pixel_coord(x, y):
    """将shp文件中的坐标转换为像素坐标"""
    x_pix = int((x - xoff) / xres)
    y_pix = int((yoff - y) / yres)
    return x_pix, y_pix

# 将每个几何图形转换为图像中的像素坐标
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

# 设置块大小
block_size = 512

# 切分
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
        cv2.imwrite(f'block_{i}_{j}.png', block)
       
