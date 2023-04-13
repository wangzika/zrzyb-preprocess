import geopandas as gpd
from shapely.geometry import Point, Polygon

# 创建四个角点
xmin, ymin, xmax, ymax = (560389, 4818439, 580979, 4837375)
bl = Point(xmin, ymin)
br = Point(xmax, ymin)
tr = Point(xmax, ymax)
tl = Point(xmin, ymax)

# 创建四个角点的多边形
bbox = Polygon([(bl.x, bl.y), (br.x, br.y), (tr.x, tr.y), (tl.x, tl.y)])

# 打开shp文件并将多边形添加到其中
gdf = gpd.read_file(r'C:\Users\xdh\Documents\ZRZYB\fengji\风机标注样本成果\res\光伏1.shp')
# gdf.loc[gdf.shape[0]] = bbox
gdf_bbox = gpd.GeoDataFrame(geometry=[bbox], crs=gdf.crs)
gdf = gdf.append(gdf_bbox, ignore_index=True)



# 保存修改后的shp文件
gdf.to_file(r'C:\Users\xdh\Documents\ZRZYB\fengji\风机标注样本成果\res\modified_shapefile.shp')
# shp_path = r'C:\Users\xdh\Documents\ZRZYB\fengji\风机标注样本成果\res\光伏2.shp'
# gdf = gpd.read_file(shp_path)
gdf.boundary.plot()
gdf.shape[0]
# gdf.bounds()
