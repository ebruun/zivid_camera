# PYTHON IMPORTS
import numpy as np
from cv2 import cv2
from matplotlib import pyplot as plt

# LOCAL IMPORTS
from utils import create_file_path as create_file_path


##################################
# IMPORT
##################################
#img_path = create_file_path("output","emulated_output_frame.png")
img_path = create_file_path("output","april20_image.png")
img = cv2.imread(img_path)

gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)



##################################
# ADJUST IMAGE
##################################
n = 7
gray = cv2.medianBlur(gray,n) #Blur

kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
gray = cv2.filter2D(gray, -1, kernel) #sharpen kernel

ret,thresh1 = cv2.threshold(gray,220,235,cv2.THRESH_BINARY) #binary threshold
ret,thresh2 = cv2.threshold(gray,220,235,cv2.THRESH_BINARY_INV) #inverse threshold

thresh = thresh2

kernel = np.ones((10,10),np.uint8) #square image kernel used for erosion

#erosion = cv2.erode(thresh, kernel,iterations = 1) #refines all edges in the binary image
erosion = thresh

opening = cv2.morphologyEx(erosion, cv2.MORPH_OPEN, kernel)
closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel) #this is for further removing small noises and holes in the image
closing = np.uint8(closing)


##################################
# FIND FEATURES
##################################
edges = cv2.Canny(closing,100,200,5)
corners = cv2.goodFeaturesToTrack(closing,12,0.1,40)

contours, hierarchy = cv2.findContours(closing,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #find contours with simple approximation
max_contour_area = 2300000 #(1920x1200 pixels)
contours = [c  for c in contours if cv2.contourArea(c)<max_contour_area]



##################################
# PLOT
##################################
fig = plt.figure(figsize=(16, 6))

cv2.drawContours(img, contours, -1, (0, 255, 0), 7)

for corner in corners:
    x,y = corner.ravel()
    cv2.circle(img,(x,y),5,(0,0,255),-1)

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
plt.title('Binary Threshold'), plt.xticks([]), plt.yticks([])

plt.subplot(gs[0, 2]),
plt.imshow(thresh,"gray")
plt.title('Inverse Threshold'), plt.xticks([]), plt.yticks([])

plt.subplot(gs[0, 3]),
plt.imshow(closing, "gray")
plt.title('Eroded'), plt.xticks([]), plt.yticks([])

plt.show()
