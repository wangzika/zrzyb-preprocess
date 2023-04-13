from osgeo import gdal
import numpy as np

# 打开TIFF文件
tiff_path = r'C:\Users\cnu\Desktop\自然资源部\光伏2.tif'
tiff_ds = gdal.Open(tiff_path)

# 获取TIFF文件的宽度和高度
tiff_width = tiff_ds.RasterXSize
tiff_height = tiff_ds.RasterYSize

# 定义切分大小
tile_size = 512
i=0

# 循环遍历TIFF文件并切分成512x512大小的图像
for y in range(0, tiff_height, tile_size):
    for x in range(0, tiff_width, tile_size):
        # 获取每个切分块的左上角坐标
        x_min = x
        y_min = y
        x_max = min(x + tile_size, tiff_width)
        y_max = min(y + tile_size, tiff_height)

        # 读取切分块的数据  data = dataset.ReadAsArray(xoff=0, yoff=0, xsize=512, ysize=512)
        tile_data = tiff_ds.ReadAsArray(x_min, y_min, x_max - x_min, y_max - y_min)

        # 如果切分块大小不足512x512，则使用Numpy填充
        if tile_data.shape[1] < tile_size or tile_data.shape[2] < tile_size:
            padded_data = np.zeros((tile_data.shape[0], tile_size, tile_size), dtype=tile_data.dtype)
            padded_data[:, :tile_data.shape[1], :tile_data.shape[2]] = tile_data
            tile_data = padded_data

        # 定义输出文件名
        output_file = f"C:/Users/cnu/Desktop/自然资源部/res_guangfu1/tile_x{x_min}_y{y_min}.tif"

        # 创建输出TIFF文件
        driver = gdal.GetDriverByName("GTiff")
        # output_ds = driver.Create(output_file, tile_size, tile_size, tile_data.shape[0], gdal.GDT_Float32)
        output_ds = driver.Create(output_file, tile_size, tile_size, tile_data.shape[0],options= ["INTERLEAVE=PIXEL"])
        #获得图像的经纬度
        # if i==0:
        #     transform = tiff_ds.GetGeoTransform()
        # else:
        #     path=r"C:/Users/cnu/Desktop/自然资源部/res_guangfu1/tile_x{x_min}_y{y_min}.tif"
        #     tiff_ds_lit = gdal.Open(path)
        #     transform = tiff_ds_lit.GetGeoTransform()
        transform = tiff_ds.GetGeoTransform()

        # 计算左上角的经纬度
        x_origin = transform[0]
        y_origin = transform[3]
        pixel_width = transform[1]
        pixel_height = transform[5]
        ulx = x_origin
        uly = y_origin
        i=i+1

        # 计算右下角的经纬度
        lrx = ulx + (x * pixel_width)
        lry = uly - (y * -pixel_height)
        # 设置输出TIFF文件的地理元数据
        # output_ds.SetGeoTransform((x_min, tiff_ds.GetGeoTransform()[1], 0, y_min, 0, tiff_ds.GetGeoTransform()[5]))
        output_ds.SetGeoTransform((lrx, tiff_ds.GetGeoTransform()[1], 0, lry, 0, tiff_ds.GetGeoTransform()[5]))

        output_ds.SetProjection(tiff_ds.GetProjection())

        # 将切分块数据写入输出TIFF文件
        for i in range(tile_data.shape[0]):
            output_ds.GetRasterBand(i+1).WriteArray(tile_data[i, :, :])

        # 关闭输出TIFF文件
        output_ds = None
