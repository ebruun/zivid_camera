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

data_file_in = create_file_path("input","lab_test_april6.zdf")
#data_file_in = create_file_path("input","MiscObjects.zdf")
file_out_bgr = create_file_path("output","april6_image.png")
file_out_depth = create_file_path("output","april6_depth.png")


print(f"Reading ZDF frame from file: {data_file_in}")

frame = zivid.Frame(data_file_in)
point_cloud = frame.point_cloud()


print("Converting to BGR image in OpenCV format")
bgr = _point_cloud_to_cv_bgr(point_cloud)
cv2.imwrite(file_out_bgr, bgr)

print("Converting to Depth map in OpenCV format")
z_color_map = _point_cloud_to_cv_z(point_cloud)

z_color_map[290:310,805:825] = [255,255,255] #del
z_color_map[290:310,1455:1475] = [255,255,255] #del

z_color_map[657:677,1055:1075] = [255,255,255]
z_color_map[578:598,1725:1745] = [255,255,255]
z_color_map[511:531,891:911] = [255,255,255]
z_color_map[386:406,1730:1750] = [255,255,255]
z_color_map[878:898,460:480] = [255,255,255]
z_color_map[873:893,533:553] = [255,255,255]
z_color_map[690:710,990:1010] = [255,255,255]
z_color_map[675:695,532:552] = [255,255,255]
z_color_map[675:695,455:475] = [255,255,255]
z_color_map[478:498,957:977] = [255,255,255]
z_color_map[385:405,1664:1684] = [255,255,255]
z_color_map[576:596,1662:1682] = [255,255,255]


cv2.imwrite(file_out_depth, z_color_map)

plt.subplot(121),plt.imshow(bgr,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(z_color_map,cmap = 'gray')
plt.title('Depth Image'), plt.xticks([]), plt.yticks([])
plt.show()

    