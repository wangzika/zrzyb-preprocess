import os
from shapely.geometry import box
import fiona

# Set the directory containing the TIFF files
directory = r"C:\Users\xdh\.cursor-tutor"

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.txt'):
        # Split the filename by "_" and slice the resulting list to get the desired values
        values = os.path.splitext(filename)[0].split("_")[1:4]
        print(os.path.splitext(filename[0]))
        print(values) # Output: ['95.0872278213501', '36.41386270523071', '2.1457672119140625e-05']
        x_min=float(values[0])
        y_max=float(values[1])
        pixel=float(values[2])
        txt_path=os.path.join(directory,filename)
        shp_outpath=os.path.join(directory,os.path.splitext(filename)[0]+'.shp')
        with open(txt_path, 'r') as file:
            # Create a new shapefile for writing
            with fiona.open(shp_outpath, 'w', 'ESRI Shapefile', schema={'geometry': 'Polygon'}) as output:
                # Loop through each line in the file
                for line in file:
                    # Split the line into a list of values
                    values = line.split()
                    # Extract the relevant values for the rectangle
                    center_x = float(values[1])*512
                    center_y = float(values[2])*512
                    width = float(values[3])*512
                    length = float(values[4])*512
                    # Calculate the coordinates of the rectangle
                    #计算出元素行列号
                    rect_xmin = center_x-width/2
                    rect_ymin = center_y-length/2
                    rect_xmax = center_x + width/2
                    rect_ymax = center_y + length/2
                    geo_xmin=x_min+rect_xmin*pixel
                    geo_xmax=x_min+rect_xmax*pixel
                    geo_ymax=y_max-rect_ymin*pixel
                    geo_ymin=y_max-rect_ymax*pixel
                    # Convert the coordinates to a shapely box object
                    rect = box(geo_xmin, geo_ymin, geo_xmax, geo_ymax)
                    # Write the shapely object to the shapefile
                    output.write({'geometry': {'type': 'Polygon', 'coordinates': [list(rect.exterior.coords)]}, 'properties': {}})
                    print('finish:',shp_outpath)
                