import cv2
from osgeo import gdal, ogr, osr
import os

def raster2shp(mask_path, image_path, strVectorFile):

    img0 = cv2.imread(mask_path)
    img1 = cv2.cvtColor(img0, cv2.COLOR_BGR2GRAY)
    ret, img2 = cv2.threshold(img1, 200, 255, cv2.THRESH_BINARY)
    _, contours, hierarchy = cv2.findContours(img2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    inimg = gdal.Open(image_path)
    prj = osr.SpatialReference()
    prj.ImportFromWkt(inimg.GetProjection())
    Geoimg = inimg.GetGeoTransform()

    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")

    ogr.RegisterAll()
    strDriverName = "ESRI Shapefile"
    oDriver = ogr.GetDriverByName(strDriverName)
    if oDriver == None:
        print("驱动不可用！")

    oDS = oDriver.CreateDataSource(strVectorFile)
    if oDS == None:
        print("创建文件失败！")

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    papszLCO = []
    oLayer = oDS.CreateLayer("TestPolygon", srs, ogr.wkbPolygon, papszLCO)
    if oLayer == None:
        print("图层创建失败！")
    oFieldID = ogr.FieldDefn("FieldID", ogr.OFTInteger)
    oLayer.CreateField(oFieldID, 1)

    oDefn = oLayer.GetLayerDefn()
    gardens = ogr.Geometry(ogr.wkbMultiPolygon)
    i = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  # 面积大于n才保存

            box1 = ogr.Geometry(ogr.wkbLinearRing)
            i += 1
            for point in contour:
                #将像素坐标转地理坐标
                x_col = Geoimg[0] + Geoimg[1] * (float(point[0, 0])) + (float(point[0, 1])) * Geoimg[2]
                y_row = Geoimg[3] + Geoimg[4] * (float(point[0, 0])) + (float(point[0, 1])) * Geoimg[5]
                box1.AddPoint(y_row, x_col)
            oFeatureTriangle = ogr.Feature(oDefn)
            oFeatureTriangle.SetField(0, i)
            garden1 = ogr.Geometry(ogr.wkbPolygon)
            garden1.AddGeometry(box1)
            gardens.AddGeometry(garden1)
    gardens.CloseRings()
    geomTriangle = ogr.CreateGeometryFromWkt(str(gardens))
    oFeatureTriangle.SetGeometry(geomTriangle)
    oLayer.CreateFeature(oFeatureTriangle)
    oDS.Destroy()

    xpixel = Geoimg[1]
    ypixel = Geoimg[5]
    return xpixel,ypixel

def shp2area(strShpFile,xpixel,ypixel):
    dataSource = ogr.Open(strShpFile, 1)
    layer = dataSource.GetLayer()
    new_field = ogr.FieldDefn("Area", ogr.OFTReal)
    new_field.SetWidth(32)
    new_field.SetPrecision(2)
    layer.CreateField(new_field)
    for feature in layer:
        geom = feature.GetGeometryRef()
        area = geom.GetArea()
        # 矢量面积
        feature.SetField("Area", abs(area/xpixel/ypixel))
        layer.SetFeature(feature)

image_path = ""# 原始有地理坐标的图片
mask_path = ""# 分割结果图
strShpFile = ""# 分割结果图转矢量文件
strVectorFile = ""# 分割结果图转为包含每个矢量的面积的矢量文件

xpixel, ypixel = raster2shp(mask_path, image_path, strVectorFile)
strTemp = "ogr2ogr -f \"ESRI Shapefile\" -explodecollections " + strShpFile + strVectorFile
os.system(strTemp)
shp2area(strShpFile, xpixel, ypixel)



