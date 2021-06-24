# LOCAL IMPORTS
from src.camera.use import capture_image
from src.camera.convert import convert2depth, convert2png, load_pointcloud
from src.camera.intrinsics import build_cam_intrinsics

from src.processing.detect import find_features
from src.processing.calc_rectangles import calc_rectangles
from src.processing.calc_frames import calc_frames

from src.utility.io import file_name, dynamic_name
from src.utility.plots import plot_features, plot_ordered_features, plot_frames

from calibration_planes import make_yaml_frame

import os

################################
# 1. CAPTURE IMAGE
################################

def main(online = False):
	# capture with camera
	if online:
		name = dynamic_name(n=00, type = "online")
		capture_image(
			folder = "input",
			output_file = file_name(name, ".zdf"),
			setting_file = "detection_settings.yml",
		)
	else:
		# read in saved
		#name = "04_20_n00_online" #Multiple detected
		#name = "05_24_n00_online" 
		name = "06_22_n0_online"

	pc = load_pointcloud(
		folder = "input",
		input_file = file_name(name, ".zdf")
	)

	#########################################
	# 2. CONVERT AND FIND CORNERS/MIDPOINTS
	#########################################
	img_png = convert2png(
		pointcloud = pc,
		folder = "output",
		output_file = file_name(name, "_rgb.png"),
		)

	corners, midpoints = find_features(
		pointcloud = pc,
		folder = "output",
		input_file_image = file_name(name, "_rgb.png"),
		plot = True,
		)

	img_depth = convert2depth(
		pointcloud = pc,
		folder = "output",
		output_file = file_name(name, "_depth.png"),
		points = midpoints,
		)

	rectangles = calc_rectangles(corners, midpoints)
	#plot_features(img_png, img_depth, corners, midpoints)

	##########################################
	# 3. CALCULATE MEMBER FRAMES
	##########################################
	frames = calc_frames(pointcloud = pc, features = [rectangles, midpoints])

	make_yaml_frame("transformations","H1_cam_obj.yaml", frames)

	plot_frames(img_png,frames)
	plot_ordered_features(img_png, rectangles)

if __name__ == "__main__":
	main(online = True)