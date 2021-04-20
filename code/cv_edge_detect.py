# PYTHON IMPORTS
import numpy as np
from cv2 import cv2
from matplotlib import pyplot as plt
from pathlib import Path

# LOCAL IMPORTS
from utils import create_file_path as create_file_path


#img_path = create_file_path("output","emulated_output_frame.png")
#img_path = create_file_path("output","april6_image.png")
img_path = create_file_path("output","april20_image.png")

img = cv2.imread(img_path)


gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

n = 7
gray = cv2.medianBlur(gray,n) #Blur

kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
gray = cv2.filter2D(gray, -1, kernel) #sharpen kernel

# fig = plt.figure(figsize=(16, 6))
# gs = fig.add_gridspec(1,3)

# plt.subplot(gs[0, 0]),
# plt.imshow(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB))
# plt.title('GRAY'), plt.xticks([]), plt.yticks([])

# plt.subplot(gs[0, 1]),
# plt.imshow(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB))
# plt.title('GRAY BLUR'), plt.xticks([]), plt.yticks([])

# plt.subplot(gs[0, 2]),
# plt.imshow(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB))
# plt.title('GRAY SHARP'), plt.xticks([]), plt.yticks([])

# plt.show()

#gray = np.float32(gray)



ret,thresh1 = cv2.threshold(gray,220,235,cv2.THRESH_BINARY) #binary threshold
ret,thresh2 = cv2.threshold(gray,220,235,cv2.THRESH_BINARY_INV) #inverse threshold

thresh = thresh2

kernel = np.ones((10,10),np.uint8) #square image kernel used for erosion
#erosion = cv2.erode(thresh, kernel,iterations = 1) #refines all edges in the binary image

erosion = thresh

opening = cv2.morphologyEx(erosion, cv2.MORPH_OPEN, kernel)
closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel) #this is for further removing small noises and holes in the image

closing = np.uint8(closing)
contours, hierarchy = cv2.findContours(closing,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #find contours with simple approximation

#NEED LOGIC TO CHOOSE CONTOURS
areas = [] #list to hold all areas

for contour in contours:
  ar = cv2.contourArea(contour)
  areas.append(ar)

# HARDCODED THE ONES TO CHOOSE
cv2.drawContours(img, contours[:], -1, (0, 255, 0), 7)
  
 

##################################
fig = plt.figure(figsize=(16, 6))

edges = cv2.Canny(closing,100,200,5)

corners = cv2.goodFeaturesToTrack(closing,12,0.1,40)

for corner in corners:
    x,y = corner.ravel()
    cv2.circle(img,(x,y),5,(0,0,255),-1)


# cv2.imshow('canny', edges)
# cv2.imshow('image', img)
# cv2.waitKey()

plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

plt.show()


##################################
fig = plt.figure(figsize=(16, 6))

gs = fig.add_gridspec(3,4)

plt.subplot(gs[1:3, 1:3]),
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title('Original Image'), plt.xticks([]), plt.yticks([])

plt.subplot(gs[0, 0]),
plt.imshow(gray,"gray")
plt.title('Gray Image'), plt.xticks([]), plt.yticks([])

plt.subplot(gs[0, 1]),
plt.imshow(thresh1,"gray")
plt.title('Threshold'), plt.xticks([]), plt.yticks([])

plt.subplot(gs[0, 2]),
plt.imshow(thresh,"gray")
plt.title('Flipped Threshold'), plt.xticks([]), plt.yticks([])

plt.subplot(gs[0, 3]),
plt.imshow(closing, "gray")
plt.title('Eroded'), plt.xticks([]), plt.yticks([])

plt.show()
