# LOCAL IMPORTS
from src.camera.use import capture_image
from src.camera.convert import convert2depth, convert2png, load_pointcloud
from src.camera.intrinsics import build_cam_intrinsics

from src.processing.detect import find_features
from src.processing.calc_rectangles import calc_rectangles
from src.processing.calc_frames import calc_frames

from src.utility.io import file_name, dynamic_name
from src.utility.plots import plot_features, plot_ordered_features, plot_frames

################################
# 1. CAPTURE IMAGE
################################

#name = dynamic_name(n=00, type = "online")
#capture_image(output_file = file_name(name, ".zdf"))

name = "04_20_n00_online"
#name = "05_24_n00_online"

pc = load_pointcloud(file_name(name, ".zdf"))

#########################################
# 2. CONVERT AND FIND CORNERS/MIDPOINTS
#########################################
img_png = convert2png(
	pointcloud = pc,
	output_file = file_name(name, "_rgb.png"),
	)

corners, midpoints = find_features(
	pointcloud = pc,
	input_file_image = file_name(name, "_rgb.png"),
	plot = False,
	)

img_depth = convert2depth(
	pointcloud = pc,
	output_file = file_name(name, "_depth.png"),
	points = midpoints,
	)

rectangles = calc_rectangles(corners, midpoints)
plot_features(img_png, img_depth, corners, midpoints)

##########################################
# 3. CALCULATE MEMBER FRAMES
##########################################
frames = calc_frames(pointcloud = pc, features = [rectangles, midpoints])
plot_frames(img_png,frames)
plot_ordered_features(img_png, rectangles)

