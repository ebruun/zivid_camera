# PYTHON IMPORTS
import numpy as np
from cv2 import cv2
from matplotlib import pyplot as plt
import zivid

# ZIVID LOCAL IMPORTS

# LOCAL IMPORTS
from utils import create_file_path as create_file_path


def _point_cloud_to_cv_z(point_cloud, features):
    """Get depth map from frame.

    Args:
        point_cloud: Zivid point cloud
        features: pixel locations where we want to get depths from

    Returns:
        Depth map (HxWx1 darray)

    """
    depth_map = point_cloud.copy_data("z")

    depths = [600]
    for point in features:
        x,y = point.ravel()
        depths.append(depth_map[y,x])

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


def _main(input_file, output_bgr, output_depth):
    app = zivid.Application()

    data_file_in = create_file_path("input",input_file) #ZDF file
    file_out_bgr = create_file_path("output",output_bgr)
    file_out_depth = create_file_path("output",output_depth)

    print(f"Reading ZDF frame from file: {data_file_in}")
    frame = zivid.Frame(data_file_in)
    point_cloud = frame.point_cloud()

    print("Converting to BGR image in OpenCV format")
    bgr = _point_cloud_to_cv_bgr(point_cloud)
    cv2.imwrite(file_out_bgr, bgr)

    print("Converting to Depth map in OpenCV format")
    feature_points = np.array([
        [1065,667],
        [1735,588],
        [901,521],
        [1740,396],
        [470,887],
        [543,883],
        [1000,700],
        [542,685],
        [465,685], 
        [967,488],
        [1674,395],
        [1672,586],
        ])

    z_color_map = _point_cloud_to_cv_z(point_cloud,feature_points)

    # Add a white/black square on the depth map to show where the feature point is
    for point in feature_points:
        x,y = point.ravel()
        z_color_map[(y-5):(y+5),(x-5):(x+5)] = [255,255,255]
        z_color_map[(y-2):(y+2),(x-2):(x+2)] = [0,0,0]

    cv2.imwrite(file_out_depth, z_color_map)

    ##################################

    plt.subplot(121),plt.imshow(bgr,cmap = 'gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(z_color_map)
    plt.title('Depth Image'), plt.xticks([]), plt.yticks([])
    plt.show()


if __name__ == "__main__":
    _main(
        input_file = "_3D_frame_fromassistant_may24.zdf",
        output_bgr = "may24_image.png",
        output_depth = "may24_depth.png",
        )    