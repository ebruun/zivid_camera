import copy
from src.camera.use import capture_image
from src.camera.convert import convert2depth, convert2png

from src.processing.detect import find_features
from src.processing.calc import calc_rectangles

from src.utility.io import file_name, dynamic_name
from src.utility.plots import plot_features, plot_ordered_features

import numpy as np
from cv2 import cv2

################################
# 1. CAPTURE IMAGE
################################

#name = dynamic_name(n=00, type = "online")
#capture_image(output_file = file_name(name, ".zdf"))

#name = "04_20_n00_online"
name = "05_24_n00_online"

################################
# 2. CONVERT AND FIND CORNERS
################################

img_png = convert2png(
  input_file = file_name(name, ".zdf"),
  output_file = file_name(name, "_rgb.png"),
  )

corners, midpoints = find_features(
  input_file_zdf = file_name(name, ".zdf"), 
  input_file_image = file_name(name, "_rgb.png"),
  plot = False,
  )

img_depth = convert2depth(
  input_file = file_name(name, ".zdf"),
  output_file = file_name(name, "_depth.png"),
  points = midpoints,
  )

#plot_features(img_png, img_depth, corners, midpoints)

################################
# 3. CALCULATE VECTORS AND PLANE
################################

print(corners,midpoints)

rectangles = calc_rectangles(corners, midpoints)

plot_ordered_features(img_png, rectangles)

target = np.array([[
  [1000, 600],
  [975, 600],
  [1000, 530],
  [975, 530],
]])


img_cp = copy.deepcopy(img_png)
plot_ordered_features(img_cp, target)

H,_ = cv2.findHomography(rectangles[0], target)
print(H)

img1_warp = cv2.warpPerspective(img_png, H, (img_png.shape[1], img_png.shape[0]))

cv2.circle(img1_warp,(1000,600),10,(255,0,0),-1)

cv2.imshow('yo',img1_warp)
cv2.waitKey(0)