import cv2
import os

directory = './images'

# 遍历目录
for root, dirs, files in os.walk(directory):
    for file in files:
        image = cv2.imread(f'./images/{file}')
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(f'./image/{file}', rotated_image)
