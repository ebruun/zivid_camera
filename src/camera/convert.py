# PYTHON IMPORTS
import numpy as np
import cv2 as cv
import zivid

# ZIVID LOCAL IMPORTS

# LOCAL IMPORTS
from src.utility.io import create_file_path


def _point_cloud_to_cv_z(point_cloud, points):
	"""Get depth map from frame.

	Args:
			point_cloud: Zivid point cloud
			features: pixel locations where we want to get depths from

	Returns:
			Depth map (HxWx1 darray)

	"""
	depth_map = point_cloud.copy_data("z")

	d = []
	try:
			for point in points:
					x,y = point.ravel()
					d.append(depth_map[int(y),int(x)])
	except:
			d = [600] #default depth to use if no points given

	pad = 50 #min/max padding on min depth value

	a = depth_map < (np.nanmin(d) - pad)
	b = depth_map > (np.nanmax(d) + pad)
	c = np.isnan(depth_map)

	#Setting the depth map range based on min/max of the features
	depth_map_uint8 = (
			255 * (depth_map - (np.nanmin(d)-pad)) / (np.ptp(d) + 2*pad)
	).astype(np.uint8)

	depth_map_uint8[a] = 20 #cells closer than limit (dark)
	depth_map_uint8[b] = 240 #cells further than limit (light)
	depth_map_uint8[c] = 255 #cells without data (white)

	c_map = cv.COLORMAP_HOT
	depth_map_color_map = cv.applyColorMap(depth_map_uint8, c_map)

	return depth_map_color_map


def _point_cloud_to_cv_bgr(point_cloud):
	"""Get bgr image from frame.

	Args:
			point_cloud: Zivid point cloud

	Returns:
			BGR image (HxWx3 darray)

	"""
	rgba = point_cloud.copy_data("rgba")

	# Applying color map
	bgr = cv.cvtColor(rgba, cv.COLOR_RGBA2BGR)
	return bgr


def convert2png(pointcloud, output_file):
	print("\nCONVERTING TO BGR IMAGE")

	file_out_bgr = create_file_path("output",output_file)
	bgr = _point_cloud_to_cv_bgr(pointcloud)

	cv.imwrite(file_out_bgr, bgr)

	return bgr

def convert2depth(pointcloud, output_file, points = False):
	print("\nCONVERTING TO DEPTH IMAGE")

	file_out_depth = create_file_path("output",output_file)
	z_color_map = _point_cloud_to_cv_z(pointcloud, points)

	cv.imwrite(file_out_depth, z_color_map)

	return z_color_map

def load_pointcloud(input_file):
	print("\nREAD IN POINTCLOUD")

	app = zivid.Application()
	data_file_in = create_file_path("input",input_file) #ZDF file

	print(f"--Reading ZDF frame from file: {data_file_in}")
	frame = zivid.Frame(data_file_in)
	point_cloud = frame.point_cloud()

	return point_cloud  


if __name__ == "__main__":
		name = "04_20_n00_online.zdf"
		pc =  load_pointcloud(name)

		convert2png(pointcloud=pc, output_file = "_test_convert_rgb.png")
		convert2depth(pointcloud=pc, output_file = "_test_convert_depth.png")