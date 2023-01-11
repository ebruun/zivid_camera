# PYTHON IMPORTS
import open3d as o3d
import numpy as np


# LOCAL IMPORTS
from src_cam.utility.io import (
    _create_file_path,
    load_pointcloud,
    load_pointcloud_ply,
    load_as_transformation_yaml,
    save_pointcloud_ply,
)

from src_cam.utility.display import (
    visualize_pcd,
    visualize_pcd_interactive,
)


def _combine_pcd(i, test_name, folder_names, file_names, scale=1):
    """combine and scale two pointclouds as ply files"""
    point_data = []
    color_data = []

    for cam_num in [1, 2]:

        pcd = load_pointcloud_ply(
            folder_names["input_data"].format(test_name),
            file_names["pntcloud_trns_ply"].format(i, cam_num),
        )

        point_data.append(np.asarray(pcd.points))
        color_data.append(np.asarray(pcd.colors))

    points_combined = np.concatenate(point_data, axis=0)
    colors_combined = np.concatenate(color_data, axis=0)

    # Scale from mm --> m (if 1000)
    points_combined = points_combined * scale

    pcd_combined = o3d.geometry.PointCloud()
    pcd_combined.points = o3d.utility.Vector3dVector(points_combined)
    pcd_combined.colors = o3d.utility.Vector3dVector(colors_combined)

    return pcd_combined


def _rotate_pcd(pcd):
    """rotate full pointcloud so that +z is aligned with "up" in real world"""
    R = pcd.get_rotation_matrix_from_xyz((np.pi, 0, 0))
    pcd_rotated = pcd.rotate(R, center=(0, 0, 0))

    return pcd_rotated


def _crop_pcd(pcd, i):
    """crop pointcloud based on this specified box, make this generic one day"""

    box_corners = np.array(
        [
            [-0.005, -0.028, 0.229],
            [-0.005, -0.028, 0.235 + 0.003 * i],
            [-0.005, 0.175, 0.229],
            [-0.005, 0.175, 0.235 + 0.003 * i],
            [0.24, -0.028, 0.229],
            [0.24, -0.028, 0.235 + 0.003 * i],
            [0.24, 0.175, 0.229],
            [0.24, 0.175, 0.235 + 0.003 * i],
        ]
    )

    box_corners = o3d.utility.Vector3dVector(box_corners.astype("float64"))
    obb = o3d.geometry.OrientedBoundingBox.create_from_points(box_corners)

    pcd_cropped = pcd.crop(obb)

    # Get a nice looking bounding box to display around the newly cropped point cloud
    bounding_box = pcd_cropped.get_axis_aligned_bounding_box()
    bounding_box.color = (1, 0, 0)

    return pcd_cropped, bounding_box


def _color_mask_pcd(pcd, threshold=0.00):
    """select all points that are above a certain grayscale value, 0 = black, 1 = white"""

    # Get rid of black base
    grayscale_values = np.array(pcd.colors).dot(np.array([0.2989, 0.5870, 0.1140]))
    mask_indices = [i for i, x in enumerate(grayscale_values > threshold) if x]
    pcd_masked = pcd.select_by_index(mask_indices)

    return pcd_masked


def _outlier_remove_pcd(pcd, n, std):
    """remove outliers"""
    pcd_outlier, _ = pcd.remove_statistical_outlier(nb_neighbors=n, std_ratio=std)
    return pcd_outlier


def pcd_transform_and_save(pcd_range, test_name, folder_names, file_names):
    """Transform PCDs based on rotattion matrix from calibration plate"""

    for i in pcd_range:
        for cam_num in [1, 2]:

            trans = load_as_transformation_yaml(
                folder=folder_names["input_data"].format(test_name),
                input_file=file_names["t_matrix"].format(i, cam_num),
            )

            pc, frame = load_pointcloud(
                folder=folder_names["input_data"].format(test_name),
                input_file=file_names["pntcloud"].format(i, cam_num),
            )

            # Transform
            pc.transform(trans)

            # Save as ZDF
            pointcloud_file_path = _create_file_path(
                folder=folder_names["input_data"].format(test_name),
                filename=file_names["pntcloud_trns_zdf"].format(i, cam_num),
            )
            frame.save(pointcloud_file_path)

            # Save as PLY
            pointcloud_file_path = _create_file_path(
                folder=folder_names["input_data"].format(test_name),
                filename=file_names["pntcloud_trns_ply"].format(i, cam_num),
            )
            frame.save(pointcloud_file_path)


def pcd_process_and_save(pcd_range, test_name, folder_names, file_names, vis_on=False):
    """process the PCD in various ways: combine, rotate, crop, mask, outlier removal"""

    for i in pcd_range:
        pcd = _combine_pcd(i, test_name, folder_names, file_names, scale=0.001)
        print("pcd size after combine: {}".format(pcd))

        pcd = _rotate_pcd(pcd)

        pcd, crop_box = _crop_pcd(pcd, i)
        print("pcd size after cropping: {}".format(pcd))

        pcd = _color_mask_pcd(pcd, threshold=0.05)
        print("pcd size after color mask: {}".format(pcd))

        pcd = _outlier_remove_pcd(pcd, n=10, std=1.5)
        print("pcd size after outlier removal: {}".format(pcd))

        save_pointcloud_ply(
            pcd,
            folder_names["output_data"].format(test_name),
            file_names["pntcloud_processed_ply"].format(test_name, i),
        )

        if vis_on:
            visualize_pcd(
                viz_item_list=[pcd, crop_box],
                folder=folder_names["input_settings"],
                filename=file_names["o3d_view"],
                axis=True,
            )


def pcd_threshold_and_save(pcd_range, test_name, folder_names, file_names, vis_on=False):
    """Identify and isolate features of interest (white dots) in the PCDs"""

    for i in pcd_range:
        pcd = o3d.io.read_point_cloud(
            _create_file_path(
                folder=folder_names["output_data2"].format(test_name),
                filename=file_names["pntcloud_processed_ply"].format(test_name, i),
            ).__str__()
        )

        grayscale_values = np.array(pcd.colors).dot(np.array([0.2989, 0.5870, 0.1140]))

        mask_indices = [i for i, x in enumerate(grayscale_values > 0.55) if x]

        pcd_reduced = pcd.select_by_index(mask_indices)
        pcd_reduced.paint_uniform_color([1, 0, 0])

        pcd_leftover = pcd.select_by_index(mask_indices, invert=True)
        # pcd_leftover, ind = pcd_leftover.remove_statistical_outlier(nb_neighbors=10, std_ratio=0.2)

        # pcd_leftover.paint_uniform_color([0.5,0.5,0.5])

        print("original: {}\n reduced: {}".format(pcd, pcd_reduced))

        if vis_on:
            visualize_pcd(
                viz_item_list=[pcd_reduced, pcd_leftover],
                folder=folder_names["input_settings"],
                filename=file_names["o3d_view"],
            )
