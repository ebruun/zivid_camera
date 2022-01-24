# PYTHON IMPORTS
from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import copy
from compas.geometry import Transformation

# LOCAL IMPORTS
from src.camera.intrinsics import build_cam_intrinsics


def plot_flex(imgs, dims):

	fig, axs = plt.subplots(dims[0],dims[1], figsize=(18, 8), facecolor='w', edgecolor='k')

	for item in imgs.items():
		i = item[1]

		axs[i["pos"]].imshow(i['img_file'],cmap="gray")
		axs[i["pos"]].set_title(i['name'])

def plot_summary(img, contours, contours_save, midpoint_save, hull, corners_rect, corners_saved):
	
	img2 = copy.deepcopy(img)
	img3 = copy.deepcopy(img)
	img4 = copy.deepcopy(img)

	cv.drawContours(img, contours, -1, (255, 0, 0), 5)
	cv.drawContours(img2, contours_save, -1, (255, 0, 0), 7)

	for i,_ in enumerate(midpoint_save):
		cv.drawContours(img2, [corners_rect[4*i:4*i+4]], -1, (0, 0, 255), 3)

	for corner in hull:
		x,y = corner.ravel()
		cv.circle(img3,(int(x),int(y)),8,(255,0,0),-1)

	for corner in corners_rect:
		x,y = corner.ravel()
		cv.circle(img3,(int(x),int(y)),8,(0,0,255),-1)

	for corner in corners_saved:
		x,y = corner.ravel()
		cv.circle(img3,(int(x),int(y)),5,(0,255,0),-1) 
		cv.circle(img4,(int(x),int(y)),8,(0,255,0),-1) 

	for midpoint in midpoint_save:
		x,y = midpoint.ravel()
		cv.circle(img4,(int(x),int(y)),10,(255,0,0),-1)        

	fig = plt.figure(figsize=(12, 6))

	plt.subplot(221),
	plt.imshow(img,cmap = 'gray')
	plt.title('ALL contours'), plt.xticks([]), plt.yticks([])

	plt.subplot(222),
	plt.imshow(img2,cmap = 'gray')
	plt.title('SELECTED contours & rect approx'), plt.xticks([]), plt.yticks([])

	plt.subplot(223),
	plt.imshow(img3, cmap = 'gray')
	plt.title('corners: Hull, Rect, Saved'), plt.xticks([]), plt.yticks([])

	plt.subplot(224),
	plt.imshow(img4, cmap = 'gray')
	plt.title('saved corners + midpoint'), plt.xticks([]), plt.yticks([])


def plot_features(img_png, img_depth, points, midpoints):
	fig = plt.figure(figsize=(12, 6))

	plt.subplot(121),
	plt.imshow(img_png,cmap = 'gray')
	plt.title('Original Image'),
	plt.xticks([]), plt.yticks([])

	# Add a white/black square on the depth map to show where the feature point is
	for point in points:
		x,y = point.ravel()

		x = int(x)
		y = int(y)

		img_depth[(y-5):(y+5),(x-5):(x+5)] = [255,255,255]
		img_depth[(y-2):(y+2),(x-2):(x+2)] = [0,0,0]

	for point in midpoints:
		x,y = point.ravel()

		x = int(x)
		y = int(y)

		img_depth[(y-5):(y+5),(x-5):(x+5)] = [255,255,255]
		img_depth[(y-2):(y+2),(x-2):(x+2)] = [255,0,0]

	img_depth = cv.cvtColor(img_depth, cv.COLOR_BGR2RGB)

	plt.subplot(122),
	plt.imshow(img_depth,cmap = 'gray')
	plt.title('Depth Image'),
	plt.xticks([]), plt.yticks([])
	plt.show()


def plot_ordered_features(img_png, rectangles):

	img_png = cv.cvtColor(img_png, cv.COLOR_BGR2RGB)

	for rectangle in rectangles:
		for i,point in enumerate(rectangle):
			x,y = point.ravel()
			cv.circle(img_png,(int(x),int(y)),10,(255,0,0),-1)
			cv.putText(
				img = img_png,
				text = str(i),
				org = (x+10,y-10),
				fontFace= cv.FONT_HERSHEY_COMPLEX,
				fontScale = 1.5,
				thickness = 4,
				color = (0, 0, 255),
				)

	fig = plt.figure(figsize=(12, 6))
	
	plt.subplot(111),
	plt.imshow(img_png,cmap = 'gray')
	plt.title('Original Image'),
	plt.xticks([]), plt.yticks([])
	plt.show()

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
	T = Transformation.from_frame(F)

	r_mat = np.squeeze(T)[0:3,0:3]
	rvec,_ = cv.Rodrigues(r_mat)
	tvec = np.squeeze(T)[0:3,3].reshape(3,1)

	return rvec, tvec


def plot_frames(img,frames):
	print("\n--plot frames")
	mtx, dist = build_cam_intrinsics("intrinsics.yml")

	h, w = img.shape[:2]
	newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

	img_corrected = cv.undistort(img, mtx, dist, None, newcameramtx)

	img1 = copy.deepcopy(img)
	img2 = copy.deepcopy(img_corrected)
	
	for frame in frames:
		rvec,tvec = _member_transforms(frame)

		_draw_axis(img,rvec,tvec,mtx) #draw on original
		_draw_axis(img_corrected,rvec,tvec,newcameramtx) #draw on distortion corrected

	h1 = np.concatenate((img1, img), axis = 1)
	h2 = np.concatenate((img2, img_corrected), axis = 1)
	v1 = np.concatenate((h1, h2), axis = 0)

	im = cv.resize(v1, (1320, 800))
	cv.imshow('img', im)
	cv.waitKey(100)