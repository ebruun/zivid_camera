# PYTHON IMPORTS
import numpy as np
import cv2 as cv

# LOCAL IMPORTS
from src_cam.utility.io import _create_file_path

from src_cam.utility.io import (
    load_pointcloud,
)


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
            x, y = point.ravel()
            d.append(depth_map[int(y), int(x)])
    except TypeError:
        d = [600]  # default depth to use if no points given

    pad = 50  # min/max padding on min depth value

    a = depth_map < (np.nanmin(d) - pad)
    b = depth_map > (np.nanmax(d) + pad)
    c = np.isnan(depth_map)

    # Setting the depth map range based on min/max of the features
    depth_map_uint8 = (255 * (depth_map - (np.nanmin(d) - pad)) / (np.ptp(d) + 2 * pad)).astype(
        np.uint8
    )

    depth_map_uint8[a] = 20  # cells closer than limit (dark)
    depth_map_uint8[b] = 240  # cells further than limit (light)
    depth_map_uint8[c] = 255  # cells without data (white)

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


def convert2png(pointcloud, folder, output_file):
    print("\nCONVERTING TO BGR IMAGE")

    file_out_bgr = _create_file_path(folder, output_file).__str__()
    bgr = _point_cloud_to_cv_bgr(pointcloud)

    cv.imwrite(file_out_bgr, bgr)

    return bgr


def convert2depth(pointcloud, folder, output_file, points=False):
    print("\nCONVERTING TO DEPTH IMAGE")

    file_out_depth = _create_file_path(folder, output_file).__str__()
    z_color_map = _point_cloud_to_cv_z(pointcloud, points)

    cv.imwrite(file_out_depth, z_color_map)

    return z_color_map


if __name__ == "__main__":
    pc = load_pointcloud(
        folder="input",
        input_file="_test_output.zdf",
    )

    convert2png(
        pointcloud=pc,
        folder="output",
        output_file="_test_convert_rgb.png",
    )

    convert2depth(
        pointcloud=pc,
        folder="output",
        output_file="_test_convert_depth.png",
    )
