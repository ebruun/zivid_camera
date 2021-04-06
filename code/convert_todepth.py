# PYTHON IMPORTS
import os
import numpy as np
from pathlib import Path

from cv2 import cv2
from matplotlib import pyplot as plt
import zivid

# ZIVID LOCAL IMPORTS
import applications.advanced.create_depth_map as create_depth_map

# LOCAL IMPORTS
from utils import create_file_path as create_file_path


def _point_cloud_to_cv_z(point_cloud):
    """Get depth map from frame.

    Args:
        point_cloud: Zivid point cloud

    Returns:
        Depth map (HxWx1 darray)

    """
    depth_map = point_cloud.copy_data("z")

    depth_map_uint8 = (
        (depth_map - np.nanmin(depth_map)) / (np.nanmax(depth_map) - np.nanmin(depth_map)) * 255
    ).astype(np.uint8)

    depth_map_color_map = cv2.applyColorMap(depth_map_uint8, cv2.COLORMAP_VIRIDIS)

    # Setting nans to black
    depth_map_color_map[np.isnan(depth_map)[:, :]] = 0

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
    bgr = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGR)
    return bgr


app = zivid.Application()

data_file = create_file_path("input","lab_test_april6_notape.zdf")
print(f"Reading ZDF frame from file: {data_file}")

frame = zivid.Frame(data_file)
point_cloud = frame.point_cloud()

print("Converting to BGR image in OpenCV format")
bgr = _point_cloud_to_cv_bgr(point_cloud)
file_out = create_file_path("output","april6_image.png")
cv2.imwrite(file_out, bgr)

print("Converting to Depth map in OpenCV format")
z_color_map = _point_cloud_to_cv_z(point_cloud)

z_color_map[525:575,825:875] = [255,255,255]
z_color_map[475:525,325:375] = [255,255,255]

file_out = create_file_path("output","april6_depth.png")
cv2.imwrite(file_out, z_color_map)

plt.subplot(121),plt.imshow(bgr,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(z_color_map,cmap = 'gray')
plt.title('Depth Image'), plt.xticks([]), plt.yticks([])
plt.show()

    