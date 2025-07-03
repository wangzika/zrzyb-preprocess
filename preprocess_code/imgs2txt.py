# 将二值图转为txt文本文件：具体将目标框保留中心点，以及长和宽。
import os
import cv2

# 定義文件夾路徑和輸出txt文件夾路徑
input_folder_path = r'C:\Users\xdh\Documents\ZRZYB\fengji\fengji_bina_png'
output_folder_path = r'C:\Users\xdh\Documents\ZRZYB\fengji\fengji_bina_png'

# 確定輸出txt文件夾存在
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# 遍歷文件夾中的所有文件
for filename in os.listdir(input_folder_path):
    # 確定文件是圖像文件
    if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
        # 讀取圖像文件
        img = cv2.imread(os.path.join(input_folder_path, filename), cv2.IMREAD_GRAYSCALE)
        # 將二值圖反轉，使前景為白色，背景為黑色
        # img = cv2.bitwise_not(img)
        # 找到前景的輪廓
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 遍歷輪廓
        rectangles=[]
        print(contours)
        for contour in contours:
            # 獲取輪廓的外接矩形
            x, y, w, h = cv2.boundingRect(contour)
            print(x, y, w, h)
            # 計算矩形的中心點座標
            center_x = x + w / 2
            center_y = y + h / 2
            rectangles.append((w, h, (x+w/2, y+h/2))) #Each row is class x_center y_center width height format
            # 將矩形的長寬和中心點座標寫入txt文件
            # with open(os.path.join(output_folder_path, os.path.splitext(filename)[0] + '.txt'), 'w') as f:
            #     f.write(f"{0} {w} {h} {center_x} {center_y}\n")
        print(contours)
        for contour in contours:
            with open(os.path.join(output_folder_path, os.path.splitext(filename)[0] + '.txt'), 'w') as f:
                for rectangle in rectangles:
                    # f.write('0'+' '+str(+rectangle[0]) + ',' + str(rectangle[1]) + ',' + str(rectangle[2][0]) + ',' + str(rectangle[2][1]) + '\n')
                    f.write('0'+' '+str(+rectangle[2][0]/512) + ' ' + str(rectangle[2][1]/512) + ' ' + str(rectangle[0]/512) + ' ' + str(rectangle[1]/512) + '\n')

            
