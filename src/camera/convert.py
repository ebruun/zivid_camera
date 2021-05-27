# PYTHON IMPORTS
import numpy as np
from cv2 import cv2
from matplotlib import pyplot as plt
import zivid

# ZIVID LOCAL IMPORTS

# LOCAL IMPORTS
from src.utility.io import create_file_path


def _point_cloud_to_cv_z(point_cloud, features):
    """Get depth map from frame.

    Args:
        point_cloud: Zivid point cloud
        features: pixel locations where we want to get depths from

    Returns:
        Depth map (HxWx1 darray)

    """
    depth_map = point_cloud.copy_data("z")

    try:
        depths = []
        for point in features:
            x,y = point.ravel()
            depths.append(depth_map[int(y),int(x)])
    except:
        depths = [600]

    # Setting the depth map based on min/max of the features
    pad = 100
    depth_map_uint8 = (
        255 * (depth_map - (np.nanmin(depths)-pad)) / ((pad+np.nanmax(depths)) - (np.nanmin(depths)-pad))
    ).astype(np.uint8)

    depth_map_uint8 = 255 - depth_map_uint8 #Flipping so that closest = lighter color

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

    ##################################
    plt.subplot(121),
    plt.imshow(bgr,cmap = 'gray')
    plt.title('Original Image'),
    plt.xticks([]), plt.yticks([])

def convert2depth(input_file, output_file, feature_points=False):
    print("\nCONVERT TO DEPTH IMAGE")
    app = zivid.Application()

    data_file_in = create_file_path("input",input_file) #ZDF file
    file_out_depth = create_file_path("output",output_file)

    print(f"--Reading ZDF frame from file: {data_file_in}")
    frame = zivid.Frame(data_file_in)
    point_cloud = frame.point_cloud()

    print("--Converting to Depth map in OpenCV format")
    z_color_map = _point_cloud_to_cv_z(point_cloud,feature_points)

    # # Add a white/black square on the depth map to show where the feature point is
    # for point in feature_points:
    #     x,y = point.ravel()

    #     x = int(x)
    #     y = int(y)

    #     z_color_map[(y-5):(y+5),(x-5):(x+5)] = [255,255,255]
    #     z_color_map[(y-2):(y+2),(x-2):(x+2)] = [0,0,0]

    cv2.imwrite(file_out_depth, z_color_map)

    ##################################
    z_color_map = cv2.cvtColor(z_color_map, cv2.COLOR_BGR2RGB)

    plt.subplot(122),
    plt.imshow(z_color_map,cmap = 'gray')
    plt.title('Depth Image'),
    plt.xticks([]), plt.yticks([])
    plt.show()


if __name__ == "__main__":   
    convert2png(input_file = "_3D_frame_fromassistant.zdf",output_file = "_test_convert_rgb.png")
    convert2depth(input_file = "_3D_frame_fromassistant.zdf",output_file = "_test_convert_depth.png")