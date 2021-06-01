import numpy as np
import cv2 as cv
import glob

# LOCAL IMPORTS
from src.utility.io import create_file_path

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = 30*np.zeros((6*7,3), np.float32)
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


#############################################

#############################################

 #Input images
img1 = cv.imread(create_file_path("img_calibration","left04.jpg"))
ret1, corners1 = cv.findChessboardCorners(img1, (7,6))

img2 = cv.imread(create_file_path("img_calibration","left02.jpg"))
ret2, corners2 = cv.findChessboardCorners(img2, (7,6))

cv.drawChessboardCorners(img1, (7,6), corners1, ret1)
cv.imshow('img', img1)
cv.waitKey(0)

if ret1 and ret2:
    print("found both")

obj_pnt = np.zeros((6*7,3), np.float32)
obj_pnt[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
obj_pnt_planar = np.delete(obj_pnt,obj=2, axis=1)

ret, rvec1, tvec1 = cv.solvePnP(obj_pnt,corners1, mtx, dist)
print(rvec1, tvec1)

R,_ = cv.Rodrigues(rvec1)

print(R)


# #img_pnt = cv.undistortPoints(corners1, mtx, dist)
# img_pnt = corners1

# H,_ = cv.findHomography(obj_pnt_planar, img_pnt)

# print(H)
# norm = np.linalg.norm(H[:,0])

# H /= norm
# print(H, norm)


# c1 = H[:,0]
# c2 = H[:,1]
# c3 = np.cross(c1,c2)
# tvec = H[:,2]

# print(c1,c2,c3,tvec)

# R =np.array([c1,c2,c3])
# R = np.squeeze(R.T)

# print(R)

# W, U, Vt = cv.SVDecomp(R)

# R = U*Vt

# def draw_axis(img, R, t, K):
#     # unit is mm
#     rotV, _ = cv.Rodrigues(R)
#     points = np.float32([[10, 0, 0], [0, 10, 0], [0, 0, 10], [0, 0, 0]]).reshape(-1, 3)
#     axisPoints, _ = cv.projectPoints(points, rotV, t, K, (0, 0, 0, 0))

    
#     axisPoints = abs(axisPoints.astype(int))
#     axisPoints = axisPoints.astype(int)
#     print(axisPoints)
#     img = cv.line(img, tuple(axisPoints[3].ravel()), tuple(axisPoints[0].ravel()), (0,0,255), 3)
#     img = cv.line(img, tuple(axisPoints[3].ravel()), tuple(axisPoints[1].ravel()), (0,255,0), 3)
#     img = cv.line(img, tuple(axisPoints[3].ravel()), tuple(axisPoints[2].ravel()), (255,0,0), 3)
#     return img

# im = draw_axis(img1,R,R.dot(tvec),mtx)

# cv.imshow('img', im)
# cv.waitKey(0)

# print(R)

