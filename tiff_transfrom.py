# from PIL import Image

# # 打开TIFF影像
# img = Image.open('光伏1.tif')

# # 确定平移距离，这里以向右平移50像素为例
# dx = 50
# dy = 1110

# # 应用平移操作
# img = img.transform(img.size, Image.AFFINE, (1, 0, dx, 0, 1, dy))

# # 保存结果
# img.save('shifted_image.tif')


#--------------
import numpy as np
from PIL import Image

# 读取tif文件并转换为numpy数组
img = Image.open('光伏1.tif')
img_arr = np.array(img)

# 定义平移量
dx = 100 # x轴平移量
dy = 500 # y轴平移量

# 创建一个更大的numpy数组，用于保存平移后的图像
new_img_arr = np.zeros((img_arr.shape[0] + dy, img_arr.shape[1] + dx,4), dtype=img_arr.dtype)

# 将原始图像平移并保存到新的numpy数组中
new_img_arr[dy:, dx:] = img_arr
new_img = Image.fromarray(new_img_arr)
new_img.save("光伏1.png")

# 切分图像为512x512的小图像
tile_size = 512
print(new_img_arr.shape)
rows, cols,bands = new_img_arr.shape
num_tiles_row = rows // tile_size
num_tiles_col = cols // tile_size

for r in range(num_tiles_row):
    for c in range(num_tiles_col):
        tile = new_img_arr[r*tile_size:(r+1)*tile_size, c*tile_size:(c+1)*tile_size]
        # 保存图像
        tile_img = Image.fromarray(tile)
        tile_img.save(f"dist_tiff/tile_{r}_{c}.tif")
