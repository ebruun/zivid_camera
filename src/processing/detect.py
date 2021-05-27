# PYTHON IMPORTS
import numpy as np
from cv2 import cv2
from matplotlib import pyplot as plt
import zivid

# LOCAL IMPORTS
from src.utility.io import create_file_path
from src.utility.plots import plot_flex, plot_summary



##################################
# IMPORT
##################################
def _import_img(input_file):
    print("\nIMPORT IMAGE")
    app = zivid.Application()

    img_path = create_file_path("output",input_file)

    print(f"--Reading image from file: {input_file}")
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

    return img,gray,img_data1


###################################
# DEPTH MASK (WHERE NO DATA)
###################################
def _apply_depth_mask(img, gray, input_file):
    print("\nAPPLY DEPTH MASK")
    data_file_in = create_file_path("input",input_file) #ZDF file

    print(f"--Reading depth data from ZDF file: {data_file_in}")
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

    return img,gray,img_data2


####################################
# GLARE REMOVE
####################################
def _apply_glare_remove(img,gray):
    print("\nAPPLY GLARE REMOVE")

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
    img = img_unglared

    return gray, img_data3



##################################
# ADJUST IMAGE
##################################
def _apply_threshold(gray):
    print("\nAPPLY BINARY THRESHOLD")

    n = 7
    gray = cv2.medianBlur(gray,n) #Blur

    kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
    gray = cv2.filter2D(gray, -1, kernel) #sharpen kernel

    min_max = cv2.minMaxLoc(gray) 
    delta = 50

    _,thresh1 = cv2.threshold(gray,(min_max[1] - delta), 255,cv2.THRESH_BINARY) #binary threshold
    
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

    return closing, img_data4


##################################
# FIND FEATURES
##################################
def _find_contours(closing):
    print("\nFIND FEATURES")

    contours, hierarchy = cv2.findContours(closing,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #find contours with simple approximation

    min_area = 5000
    max_area = 25000
    n_approx_max = 8 #how many corners should approx shape have
    max_contour_area = 2300000 # max contour area for 1920x1200 pixels

    contours = [c  for c in contours if cv2.contourArea(c) < max_contour_area]

    #make a mask of only the final rectangles
    found_shapes = np.zeros((1200,1920,3), np.uint8)
    found_shapes[:, :] = (255,255,255) #all white

    num_labels = 0
    contours_save = []
    for c in contours:
        area = cv2.contourArea(c)
        epsilon = 0.01*cv2.arcLength(c,True)
        approx = cv2.approxPolyDP(c,epsilon,True)

        str = "--contour area: {:.0f}, # contours: {:.0f}, # approx corner: {:.0f}".format(area, len(c), len(approx))
        print(str)

        if area > min_area and area < max_area and len(approx) < n_approx_max:
                num_labels += 1
                cv2.drawContours(found_shapes, [c], -1, (0, 0, 0), thickness=cv2.FILLED)
                contours_save.append(c)

    found_shapes = cv2.cvtColor(found_shapes,cv2.COLOR_RGB2GRAY)

    edges = cv2.Canny(found_shapes,100,200,5)
    corners = cv2.goodFeaturesToTrack(found_shapes,num_labels*4,0.1,40)

    return contours, contours_save, found_shapes, edges, corners


def find_features(input_file_zdf, input_file_image, plot = False):
    img, gray, data1 = _import_img(input_file = input_file_image)
    img, gray, data2 = _apply_depth_mask(img, gray, input_file = input_file_zdf)
    gray, data3 = _apply_glare_remove(img,gray)
    closing, data4 = _apply_threshold(gray)

    contours, contours_save, found_shapes, edges, corners = _find_contours(closing)

    if plot:
        plot_flex(data1,dims=[1,2])
        plot_flex(data2,dims=[2,3])
        plot_flex(data3, dims=[2,2])
        plot_flex(data4, dims=[2,3])

        plot_summary(img, contours, contours_save, corners, found_shapes, edges)

    return corners


if __name__ == "__main__":
    find_features("may24_image.png","_3D_frame_fromassistant.zdf", plot = True)





