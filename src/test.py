import numpy as np
import cv2 as cv
import glob
import copy

from numpy.lib.function_base import copy

# LOCAL IMPORTS
from src.utility.io import create_file_path

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Frame

from compas.geometry import Transformation

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

data_file_in = create_file_path("img_calibration","*.jpg") #Input images

images = glob.glob(data_file_in)

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7,6), None)
    print("found:", ret)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)

        #Draw and display the corners
        # cv.drawChessboardCorners(img, (7,6), corners2, ret)
        # cv.imshow('img', img)
        # cv.waitKey(0)
        print("done")


ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)



#############################
i = 2

a,_ = cv.Rodrigues(rvecs[i])
b = tvecs[i]

H = np.insert(a,3,np.squeeze(b),axis=1)
H = np.insert(H,3,[0,0,0,1],axis=0)

T = Transformation.from_matrix(H.tolist())
F = Frame.from_transformation(T)

print("trans matrix", T)
print("frame", F)

img1 = cv.imread(images[i])

h,  w = img1.shape[:2]
newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

img1_nodistort = cv.undistort(img1, mtx, dist, None, newcameramtx)

def draw_axis(img, r, t, K):
    # unit is mm
    rotV, _ = cv.Rodrigues(r)
    print(rotV)
    points = np.float32([[10, 0, 0], [0, 10, 0], [0, 0, 10], [0, 0, 0]]).reshape(-1, 3)
    axisPoints, _ = cv.projectPoints(points, rotV, t, K, (0, 0, 0, 0))

    axisPoints = axisPoints.astype(int)

    img = cv.line(img, tuple(axisPoints[3].ravel()), tuple(axisPoints[0].ravel()), (0,0,255), 3)
    img = cv.line(img, tuple(axisPoints[3].ravel()), tuple(axisPoints[1].ravel()), (0,255,0), 3)
    img = cv.line(img, tuple(axisPoints[3].ravel()), tuple(axisPoints[2].ravel()), (255,0,0), 3)
    return img

img1_axis = draw_axis(copy(img1),rvecs[i],tvecs[i],mtx)
img1_nodistort_axis = draw_axis(copy(img1_nodistort),rvecs[i],tvecs[i],newcameramtx)


h1 = np.concatenate((img1, img1_axis), axis = 1)
h2 = np.concatenate((img1_nodistort, img1_nodistort_axis), axis = 1)
v1 = np.concatenate((h1, h2), axis = 0)

cv.imshow('img', v1)
cv.waitKey(0)
