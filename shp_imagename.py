import geopandas as gpd

# 读取shp文件
shp_path = r'C:\Users\xdh\Documents\自然资源部\风机标注样本成果\风机标注样本成果\风机标注样本.shp'
gdf = gpd.read_file(shp_path)

# 获取所有不同的imageName值
image_names = gdf['imageName'].unique()

# 根据imageName值切分shp文件
for image_name in image_names:
    split_gdf = gdf[gdf['imageName'] == image_name]
    split_gdf.to_file('C:/Users/xdh/Documents/自然资源部/风机标注样本成果/風機name_shp/output_file_{}.shp'.format(image_name), driver='ESRI Shapefile')
