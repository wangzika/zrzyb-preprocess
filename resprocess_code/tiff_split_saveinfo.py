# Import necessary libraries
import os
from PIL import Image
from osgeo import gdal
import cv2
import numpy as np


# Set the input and output directories
input_dir = r"C:\Users\xdh\Desktop\preprocess_code"
output_dir = r"C:\Users\xdh\Desktop\preprocess_code\dist_tiff"

# Set the desired size of each sub-image
sub_image_size = 512

# Loop through each TIFF image in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.tif'):
        # Open the image using PIL
        image = Image.open(os.path.join(input_dir, filename))
        dataset = gdal.Open(os.path.join(input_dir, filename))
        geotransform = dataset.GetGeoTransform()
        print("------------------------",os.path.join(input_dir,filename))
        print(geotransform)
        # Calculate the coordinates of the four corners of the image
        # ulx = geotransform[0]
        # uly = geotransform[3]
        # Get the dimensions of the image
        cols=dataset.RasterXSize
        rows=dataset.RasterYSize
        
        # Calculate the number of sub-images in each dimension
        num_tiles_cols =int(np.ceil(cols/sub_image_size))
        num_tiles_rows =int(np.ceil(rows/sub_image_size))

        # 创建一个大的数组容纳图像，如果边界不够则填充
        # 1。计算填充的边界
        pad_cols=num_tiles_cols*sub_image_size-cols
        pad_rows=num_tiles_rows*sub_image_size-rows

        img_arr=np.array(image)

        new_img_arr=np.zeros((int(row+pad_rows),int(cols+pad_cols),3),dtype=img_arr.dtype)

        # 将原始图像平移并保存在新的数组
        new_img_arr[0:rows,0:cols,]=img_arr
        print('rows:',rows,'\t','cols:',cols)        
        # Loop through each sub-image
        for i in range(0,rows,sub_image_size):
            num=0
            for j in range(0,cols,sub_image_size):
                print('i:',i,'\t','j:',j,'\t','num:',num)
                # Calculate the coordinates of the sub-image
                x_left=dataset.GetGeoTransform()[0]+j*dataset.GetGeoTransform()[1]
                y_top=dataset.GetGeoTransform()[3]+j*dataset.GetGeoTransform()[5]
                print((x_left,y_top,geotransform[1]))
                # Crop the sub-image using PIL
                # sub_image = image.crop((left, upper, right, lower))
                block=new_img_arr[i:i+sub_image_size,j:j+sub_image_size]

                #保存块
                tile_img=Image.fromarray(block)
                
                # Save the sub-image as a TIFF file
                sub_image_filename = os.path.splitext(filename)[0] + '_{}_{}_{}.tiff'.format(x_left,y_top,geotransform[1])
                tile_img.save(os.path.join(output_dir, sub_image_filename))
                num=num+1