import cv2 as cv
import numpy as np

from compas.geometry import Transformation

# LOCAL IMPORTS
from src_cam.camera.intrinsics import build_cam_intrinsics

def _draw_axis(img, r, t, K):
		# unit is mm
		rotV, _ = cv.Rodrigues(r) #3x1 --> 3x3

		points = np.float32([[100, 0, 0], [0, 100, 0], [0, 0, 100], [0, 0, 0]]).reshape(-1, 3)
		axisPoints, _ = cv.projectPoints(points, rotV, t, K, (0, 0, 0, 0))

		axisPoints = axisPoints.astype(int)

		img = cv.line(img, tuple(axisPoints[3].ravel()), tuple(axisPoints[0].ravel()), (0,0,255), 3)
		img = cv.line(img, tuple(axisPoints[3].ravel()), tuple(axisPoints[1].ravel()), (0,255,0), 3)
		img = cv.line(img, tuple(axisPoints[3].ravel()), tuple(axisPoints[2].ravel()), (255,0,0), 3)
		return img

def _member_transforms(F):
	print("--transformations")

	T = Transformation.from_frame(F)

	r_mat = np.squeeze(T)[0:3,0:3]
	rvec,_ = cv.Rodrigues(r_mat)
	tvec = np.squeeze(T)[0:3,3].reshape(3,1)

	return rvec, tvec


def plot_frames(img,frames):
	mtx, dist = build_cam_intrinsics("intrinsics.yml")

	h, w = img.shape[:2]
	newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

	img_corrected = cv.undistort(img, mtx, dist, None, newcameramtx)

	
	for frame in frames:
		rvec,tvec = _member_transforms(frame)

		_draw_axis(img,rvec,tvec,mtx) #draw on original
		_draw_axis(img_corrected,rvec,tvec,newcameramtx) #draw on distortion corrected

	h1 = np.concatenate((img, img), axis = 1)
	h2 = np.concatenate((img_corrected, img_corrected), axis = 1)
	v1 = np.concatenate((h1, h2), axis = 0)

	im = cv.resize(v1, (1320, 800))
	cv.imshow('img', im)
	cv.waitKey(0)