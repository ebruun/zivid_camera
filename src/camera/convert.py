# PYTHON IMPORTS
import numpy as np
from cv2 import cv2
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
        d = [600]

    pad = 50

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

    c_map = cv2.COLORMAP_HOT
    depth_map_color_map = cv2.applyColorMap(depth_map_uint8, c_map)

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


def convert2png(input_file, output_file):
    print("\nCONVERT TO BGR PNG")
    app = zivid.Application()

    data_file_in = create_file_path("input",input_file) #ZDF file
    file_out_bgr = create_file_path("output",output_file)

    print(f"--Reading ZDF frame from file: {data_file_in}")
    frame = zivid.Frame(data_file_in)
    point_cloud = frame.point_cloud()

    print("--Converting to BGR image in OpenCV format")
    bgr = _point_cloud_to_cv_bgr(point_cloud)

    cv2.imwrite(file_out_bgr, bgr)

    return bgr

def convert2depth(input_file, output_file, points):
    print("\nCONVERT TO DEPTH IMAGE")
    app = zivid.Application()

    data_file_in = create_file_path("input",input_file) #ZDF file
    file_out_depth = create_file_path("output",output_file)

    print(f"--Reading ZDF frame from file: {data_file_in}")
    frame = zivid.Frame(data_file_in)
    point_cloud = frame.point_cloud()

    print("--Converting to Depth map in OpenCV format")
    z_color_map = _point_cloud_to_cv_z(point_cloud, points)

    cv2.imwrite(file_out_depth, z_color_map)

    return z_color_map


if __name__ == "__main__":   
    convert2png(input_file = "04_20_n00_online_depth.zdf",output_file = "_test_convert_rgb.png")
    convert2depth(input_file = "04_20_n00_online_depth.zdf",output_file = "_test_convert_depth.png")