# PYTHON IMPORTS
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import zivid
import copy

# LOCAL IMPORTS
from src_cam.utility.io import _create_file_path
from src_cam.camera.convert import load_pointcloud


# Note to self: come up with a better way to specify plot data here

##################################
# IMPORT
##################################
def _import_img(folder, input_file):
    _ = zivid.Application()

    img_path = _create_file_path(folder, input_file).__str__()
    print(f"--Reading RGB image from file: {input_file}")

    img = cv.cvtColor(cv.imread(img_path), cv.COLOR_BGR2RGB)
    gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)

    img_data1 = {
        0: {
            "name": "original RGB",
            "img_file": img,
            "pos": (0),
        },
        1: {
            "name": "original gray",
            "img_file": gray,
            "pos": (1),
        },
    }

    return img, gray, img_data1


###################################
# DEPTH MASK (WHERE IS THERE NO DATA)
###################################
def _apply_depth_mask(img, gray, pointcloud):
    print("--apply depth mask")

    depth_map = pointcloud.copy_data("z")
    a = ~np.isnan(depth_map)  # where is there no depth data

    dims = np.shape(a)

    gray_mask = np.zeros((dims[0], dims[1], 1), np.uint8)  # changed from 1920-1944
    gray_mask[a] = 255  # make black
    color_mask = cv.cvtColor(gray_mask, cv.COLOR_GRAY2RGB)

    gray_plus_mask = cv.bitwise_and(gray, gray_mask)
    img_plus_mask = cv.bitwise_and(img, color_mask)

    fig_data = {
        0: {
            "name": "original gray",
            "img_file": gray,
            "pos": (1, 0),
        },
        1: {
            "name": "gray mask",
            "img_file": gray_mask,
            "pos": (1, 1),
        },
        2: {
            "name": "original gray + mask",
            "img_file": gray_plus_mask,
            "pos": (1, 2),
        },
        3: {
            "name": "original RGB",
            "img_file": img,
            "pos": (0, 0),
        },
        4: {
            "name": "RGB mask",
            "img_file": color_mask,
            "pos": (0, 1),
        },
        5: {
            "name": "original RGB + mask",
            "img_file": img_plus_mask,
            "pos": (0, 2),
        },
    }

    gray = gray_plus_mask
    img = img_plus_mask

    return img, gray, fig_data


####################################
# GLARE REMOVE
####################################
def _apply_glare_remove(img, gray):
    print("--apply glare removal")

    hsv_image = cv.cvtColor(img, cv.COLOR_RGB2HSV)
    h, s, v = cv.split(hsv_image)

    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    h = clahe.apply(h)
    s = clahe.apply(s)
    v = clahe.apply(v)

    hsv_image_unglared = cv.merge([h, s, v])
    img_unglared = cv.cvtColor(hsv_image_unglared, cv.COLOR_HSV2RGB)
    gray_unglared = cv.cvtColor(img_unglared, cv.COLOR_RGB2GRAY)

    img_data3 = {
        0: {
            "name": "original RGB + mask",
            "img_file": img,
            "pos": (0, 0),
        },
        1: {
            "name": "original gray + mask",
            "img_file": gray,
            "pos": (1, 0),
        },
        2: {
            "name": "1. original RGB + mask + unglare (w/ Clahe)",
            "img_file": img_unglared,
            "pos": (0, 1),
        },
        3: {
            "name": "2. turned gray",
            "img_file": gray_unglared,
            "pos": (1, 1),
        },
    }

    gray = gray_unglared
    img = img_unglared

    return gray, img_data3


##################################
# ADJUST IMAGE
##################################
def _apply_threshold(gray):
    print("--apply binary threshold:")

    # n = 7
    # gray = cv.medianBlur(gray, n)  # Blur

    # kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    # gray = cv.filter2D(gray, -1, kernel)  # sharpen kernel

    min_max = cv.minMaxLoc(gray)
    print("-- --max = ", min_max[1])

    delta = 50

    _, thresh1 = cv.threshold(gray, (min_max[1] - delta), 255, cv.THRESH_BINARY)  # binary threshold
    # ret, thresh1 = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)  # otsu threshold

    kernel = np.ones((5, 5), np.uint8)  # square image kernel used for erosion

    thresh = thresh1

    nlabels, labels, stats, centroids = cv.connectedComponentsWithStats(
        thresh, None, None, None, 8, cv.CV_32S
    )

    # get CC_STAT_AREA component as stats[label, COLUMN]
    areas = stats[1:, cv.CC_STAT_AREA]

    result = np.zeros((labels.shape), np.uint8)

    for i in range(0, nlabels - 1):
        if areas[i] >= 1000:  # keep
            result[labels == i + 1] = 255

    thresh = result
    erosion1 = cv.dilate(thresh, (3, 3), iterations=4)  # makes white area bigger
    erosion2 = cv.erode(erosion1, (3, 3), iterations=2)  # makes white area smaller

    thresh = erosion2
    opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)
    closing = cv.morphologyEx(
        opening, cv.MORPH_CLOSE, kernel
    )  # further remove small noises and holes in image
    closing = np.uint8(closing)

    img_data4 = {
        0: {
            "name": "masked gray, unglare, after sharpen + blur",
            "img_file": gray,
            "pos": (0, 0),
        },
        1: {
            "name": "1. threshold binary",
            "img_file": thresh1,
            "pos": (0, 1),
        },
        2: {
            "name": "2. threshold binary size reduce",
            "img_file": result,
            "pos": (0, 2),
        },
        3: {
            "name": "3. dilation (more white)",
            "img_file": erosion1,
            "pos": (1, 0),
        },
        4: {
            "name": "4. erosion (less white)",
            "img_file": erosion2,
            "pos": (1, 1),
        },
        5: {
            "name": "5. closing ",
            "img_file": closing,
            "pos": (1, 2),
        },
    }

    return closing, img_data4


##################################
# FIND FEATURES
##################################
def _find_contours(closing):
    print("--find contours and features")

    # find contours with simple approximation
    contours, hierarchy = cv.findContours(closing, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    min_area = 10000
    max_area = 40000
    n_approx_max = 6  # how many corners should approx shape have
    max_contour_area = 2300000  # max contour area for 1920x1200 pixels

    contours = [c for c in contours if cv.contourArea(c) < max_contour_area]

    # make a mask of only the final rectangles
    # found_shapes = np.zeros((1200,1920,3), np.uint8)
    # found_shapes[:, :] = (255,255,255) #all white

    num_labels = 0
    contours_save = []
    p_mid_save = []
    for c in contours:
        area = cv.contourArea(c)
        epsilon = 0.01 * cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, epsilon, True)

        str = "-- --contour area: {:.0f}, # contours: {:.0f}, # approx corner: {:.0f}".format(
            area, len(c), len(approx)
        )
        print(str)

        if area > min_area and area < max_area and len(approx) < n_approx_max:
            str = (
                "-- -- --contour area: {:.0f}, # contours: {:.0f}, # approx corner: {:.0f}".format(
                    area, len(c), len(approx)
                )
            )
            print(str)
            num_labels += 1
            # cv.drawContours(found_shapes, [c], -1, (0, 0, 0), thickness=cv.FILLED)
            contours_save.append(c)

            m = cv.moments(c)
            p_mid_save.append([int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])])

    def closest_node(node, nodes):
        dist_2 = np.sum((nodes - node) ** 2, axis=1)
        return np.argmin(dist_2)

    c_hull_save = np.empty((0, 2), int)
    c_box_save = np.empty((0, 2), int)
    c_save = np.empty((0, 2), int)
    for contour in contours_save:
        rect = cv.minAreaRect(contour)
        box = cv.boxPoints(rect)
        box = np.int0(box)

        hull = cv.convexHull(contour)
        hull = np.squeeze(hull)

        c_idx = []
        for c in box:
            c_idx.append(closest_node(c, hull))

        c_hull_save = np.append(c_hull_save, hull, axis=0)
        c_box_save = np.append(c_box_save, box, axis=0)
        c_save = np.append(c_save, hull[c_idx], axis=0)

    # edges = cv.Canny(found_shapes,0,255)
    # corners = cv.goodFeaturesToTrack(found_shapes,num_labels*4,0.5,40)
    # corners = np.squeeze(corners).astype('int32')

    p_mid_save = np.asarray(p_mid_save).astype("int32")

    return contours, contours_save, p_mid_save, c_hull_save, c_box_save, c_save


def find_features(pointcloud, folder, input_file_image, plot=False):
    print("\nFIND FEATURES IN IMAGE")
    img, gray, data1 = _import_img(folder=folder, input_file=input_file_image)
    img, gray, data2 = _apply_depth_mask(img, gray, pointcloud=pointcloud)
    # gray, data3 = _apply_glare_remove(img, gray)
    closing, data4 = _apply_threshold(gray)

    contours, contours_save, p_mid, c_hull, c_box, c = _find_contours(closing)

    plot_data = []
    if plot:
        plot_data = [
            [data1, [1, 2], "Step1: import image"],
            [data2, [2, 3], "Step2: depth mask"],
            [data4, [2, 3], "Step3: thresholding"],
            [img, contours, contours_save, p_mid, c_hull, c_box, c, "Found Features"],
        ]

    return c, p_mid, plot_data


if __name__ == "__main__":
    pc = load_pointcloud(folder="input", input_file="02_27_n0.zdf")

    find_features(
        pointcloud=pc,
        folder="output",
        input_file_image="02_27_n0_rgb.png",
        plot=True,
    )
