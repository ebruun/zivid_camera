# PYTHON IMPORTS
import numpy as np
from cv2 import cv2
from matplotlib import pyplot as plt

import copy

import zivid

# LOCAL IMPORTS
from utils import create_file_path as create_file_path


def plot(imgs, dims):


    fig, axs = plt.subplots(dims[0],dims[1], figsize=(18, 8), facecolor='w', edgecolor='k')

    #gs = fig.add_gridspec(3,4)

    for item in imgs.items():
        i = item[1]

        axs[i["pos"]].imshow(i['img_file'],cmap="gray")
        axs[i["pos"]].set_title(i['name'])

            


##################################
# IMPORT
##################################
app = zivid.Application()

img_path = create_file_path("output","april20_image.png")
img_path = create_file_path("output","may24_image.png")

input_file = "lab_test_april20.zdf"
input_file = "_3D_frame_fromassistant_may24.zdf"

data_file_in = create_file_path("input",input_file) #ZDF file

img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)

img_data1 = {
    0: {
        "name": "original RGB",
        "img_file": img,
        "pos": (0),
    },
    1: {
        "name": "original gray",
        "img_file": gray,
        "pos":(1),
    },    
}



# cv2.namedWindow("img1", cv2.WINDOW_NORMAL)
# cv2.namedWindow("img2", cv2.WINDOW_NORMAL)
# cv2.namedWindow("img3", cv2.WINDOW_NORMAL)
# cv2.namedWindow("img4", cv2.WINDOW_NORMAL)
# cv2.namedWindow("img5", cv2.WINDOW_NORMAL)


###################################
# NO DEPTH MASK
###################################
print(f"Reading ZDF frame from file: {data_file_in}")
frame = zivid.Frame(data_file_in)
point_cloud = frame.point_cloud()

depth_map = point_cloud.copy_data("z")
a = ~np.isnan(depth_map) #where is there no depth data

mask = np.zeros((1200,1920,1), np.uint8)
mask[a] = (255) #make black
img_gray_mask = cv2.bitwise_and(gray, mask)

mask3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
img_mask = cv2.bitwise_and(img, mask3)

img_data2 = {
    0: {
        "name": "original gray",
        "img_file": gray,
        "pos": (1,0),
    },
    1: {
        "name": "original RGB",
        "img_file": img,
        "pos": (0,0),
    },
    2: {
        "name": "gray mask",
        "img_file": mask,
        "pos": (1,1),
    },    
    3: {
        "name": "original gray + mask",
        "img_file": img_gray_mask,
        "pos": (1,2),
    },  
    4: {
        "name": "RGB mask",
        "img_file": mask3,
        "pos": (0,1),
    },  
    5: {
        "name": "original RGB + mask",
        "img_file": img_mask,
        "pos": (0,2),
    },  
}



gray = img_gray_mask
img = img_mask

# ###################################
# # GLARE REMOVE
# ###################################

hsv_image = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
h, s, v = cv2.split(hsv_image)

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
h = clahe.apply(h)
s = clahe.apply(s)
v = clahe.apply(v)

hsv_image_unglared = cv2.merge([h, s, v])
img_unglared = cv2.cvtColor(hsv_image_unglared, cv2.COLOR_HSV2RGB)
gray_unglared = cv2.cvtColor(img_unglared,cv2.COLOR_RGB2GRAY)

img_data3 = {
    0: {
        "name": "original RGB + mask",
        "img_file": img,
        "pos": (0,0),
    },
    1: {
        "name": "original gray + mask",
        "img_file": gray,
        "pos": (1,0),
    },
    2: {
        "name": "1. original RGB + mask + unglare (w/ Clahe)",
        "img_file": img_unglared,
        "pos": (0,1),
    },    
    3: {
        "name": "2. turned gray",
        "img_file": gray_unglared,
        "pos": (1,1),
    },   

}

gray = gray_unglared

##################################
# ADJUST IMAGE
##################################
n = 7
gray = cv2.medianBlur(gray,n) #Blur

kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
gray = cv2.filter2D(gray, -1, kernel) #sharpen kernel

min_max = cv2.minMaxLoc(gray) 
delta = 50

ret,thresh1 = cv2.threshold(gray,(min_max[1] - delta), 255,cv2.THRESH_BINARY) #binary threshold
#ret,thresh2 = cv2.threshold(gray, (min_max[1] - delta), 255,cv2.THRESH_BINARY_INV) #inverse threshold (may24)

kernel = np.ones((5,5),np.uint8) #square image kernel used for erosion

thresh = thresh1

nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh, None, None, None, 8, cv2.CV_32S)

#get CC_STAT_AREA component as stats[label, COLUMN] 
areas = stats[1:,cv2.CC_STAT_AREA]

result = np.zeros((labels.shape), np.uint8)

for i in range(0, nlabels - 1):
    if areas[i] >= 1000:   #keep
        result[labels == i + 1] = 255

thresh = result
erosion1 = cv2.dilate(thresh, (3,3),iterations = 4) #makes white area bigger
erosion2 = cv2.erode(erosion1, (3,3),iterations = 2) #makes white area smaller

thresh = erosion2
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel) #this is for further removing small noises and holes in the image
closing = np.uint8(closing)


img_data4 = {
    0: {
        "name": "masked gray, unglare, after sharpen + blur",
        "img_file": gray,
        "pos": (0,0),
    },
    1: {
        "name": "1. threshold binary",
        "img_file": thresh1,
        "pos": (0,1),
    },
    2: {
        "name": "2. threshold binary size reduce",
        "img_file": result,
        "pos": (0,2),
    },    
    3: {
        "name": "3. dilation (more white)",
        "img_file": erosion1,
        "pos": (1,0),
    },   
    4: {
        "name": "4. erosion (less white)",
        "img_file": erosion2,
        "pos": (1,1),
    },   
    5: {
        "name": "5. closing ",
        "img_file": closing,
        "pos": (1,2),
    },   

}





##################################
# FIND FEATURES
##################################
contours, hierarchy = cv2.findContours(closing,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #find contours with simple approximation

min_area = 5000
max_area = 25000
n_approx_max = 8 #how many corners should approx shape have
max_contour_area = 2300000 # max contour area for 1920x1200 pixels

contours = [c  for c in contours if cv2.contourArea(c) < max_contour_area]

#make a mask of only the final rectangles
results = np.zeros((1200,1920,3), np.uint8)
results[:, :] = (255,255,255) #all white

num_labels = 0
contour_save = []
for c in contours:
    area = cv2.contourArea(c)
    epsilon = 0.01*cv2.arcLength(c,True)
    approx = cv2.approxPolyDP(c,epsilon,True)

    str = "contour area: {:.0f}, # contours: {:.0f}, # approx corner: {:.0f}".format(area, len(c), len(approx))
    print(str)

    if area > min_area and area < max_area and len(approx) < n_approx_max:
            num_labels += 1
            cv2.drawContours(results, [c], -1, (0, 0, 0), thickness=cv2.FILLED)
            contour_save.append(c)

results = cv2.cvtColor(results,cv2.COLOR_RGB2GRAY)
edges = cv2.Canny(results,100,200,5)
corners = cv2.goodFeaturesToTrack(results,num_labels*4,0.1,40)


##################################
# PLOT
##################################

#plot(img_data1,dims=[1,2])
#plot(img_data2,dims=[2,3])
#plot(img_data3, dims=[2,2])
plot(img_data4, dims=[2,3])



fig = plt.figure(figsize=(12, 6))

img_copy = copy.deepcopy(img)
fig = plt.figure(figsize=(12, 6))
cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 7)
cv2.drawContours(img, contour_save, -1, (0, 255, 0), 7)

for corner in corners:
    x,y = corner.ravel()
    cv2.circle(img,(x,y),5,(0,0,255),-1)

plt.subplot(221),
plt.imshow(img_copy,cmap = 'gray')
plt.title('Masked RGB + ALL contours'), plt.xticks([]), plt.yticks([])

plt.subplot(223),
plt.imshow(results, cmap = 'gray')
plt.title('Found Box'), plt.xticks([]), plt.yticks([])

plt.subplot(224),
plt.imshow(edges,cmap = 'gray')
plt.title('Edges of rectangles'), plt.xticks([]), plt.yticks([])

plt.subplot(222),plt.imshow(img,cmap = 'gray')
plt.title('Masked RGB + selected contours/corners'), plt.xticks([]), plt.yticks([])

plt.show()
plt.pause(1)
