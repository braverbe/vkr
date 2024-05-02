import time

import cv2
import numpy as np

haar_cascade = cv2.CascadeClassifier('content/recogn_algoritm/haarcascade_frontalface_default.xml')


file_name = "content/images/img_2.jpg"
img = cv2.imread(file_name, 0)
gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
faces = haar_cascade.detectMultiScale(
    gray_img, scaleFactor=1.05, minNeighbors=1, minSize=(100, 100)
)
i = 0
user_image_maxx = 0
user_image_maxy = 0
user_image_maxw = 0
user_image_maxh = 0
user_image_maxi = 0
cropped_image = 0
for x, y, w, h in faces:
    if(user_image_maxh<h and user_image_maxw<w):
        user_image_maxh = h
        user_image_maxw = w
        user_image_maxi = i
        cropped_image = img[y : y + h, x : x + w]



target_file_name = 'stored-faces/img_' + str(time.time()) + '.jpg'
cv2.imwrite(
    target_file_name,
    cropped_image,
)