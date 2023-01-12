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


def _make_crop_volumes(polygons):
    crop_polygons = []
    for polygon in polygons:

        # Convert the corners array to have type float64
        bounding_polygon = polygon.astype("float64")

        # Create a SelectionPolygonVolume
        vol = o3d.visualization.SelectionPolygonVolume()

        # You need to specify what axis to orient the polygon to.
        # I choose the "Z" axis. I made the max value the maximum Z of
        # the polygon vertices and the min value the minimum Y of the
        # polygon vertices.
        vol.orthogonal_axis = "Z"
        vol.axis_max = 0.300
        vol.axis_min = np.min(bounding_polygon[:, 2])

        # Set all the Z values to 0 (they aren't needed since we specified what they
        # should be using just vol.axis_max and vol.axis_min).
        bounding_polygon[:, 2] = 0

        # Convert the np.array to a Vector3dVector
        vol.bounding_polygon = o3d.utility.Vector3dVector(bounding_polygon)

        crop_polygons.append(vol)

    return crop_polygons


# https://stackoverflow.com/a/45313353/ @Divakar
def _view1D(a, b):  # a, b are arrays
    a = np.ascontiguousarray(a)
    b = np.ascontiguousarray(b)
    void_dt = np.dtype((np.void, a.dtype.itemsize * a.shape[1]))
    return a.view(void_dt).ravel(), b.view(void_dt).ravel()


def _multi_color_change(pcd, crop_volumes):
    """use a different method to crop based on irregular 2d polygon"""

    points_crop = []
    bounding_boxes = []

    for crop_volume in crop_volumes:
        pcd_cropped = crop_volume.crop_point_cloud(pcd)
        points_crop.append(np.asarray(pcd_cropped.points))

        bounding_box = pcd_cropped.get_oriented_bounding_box()
        bounding_box.color = (0, 1, 0)

        bounding_boxes.append(bounding_box)

    points_crop = np.concatenate(points_crop, axis=0)

    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)

    A, B = _view1D(points, points_crop)
    row_indices_duplicate = np.isin(A, B)

    colors[row_indices_duplicate] = (0, 0, 0)

    pcd_modified = o3d.geometry.PointCloud()
    pcd_modified.points = o3d.utility.Vector3dVector(points)
    pcd_modified.colors = o3d.utility.Vector3dVector(colors)

    return pcd_modified, bounding_boxes


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


###########################


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
            folder_names["output_data1"].format(test_name),
            file_names["pntcloud_processed_ply"].format(test_name, i),
        )

        if vis_on:
            visualize_pcd(
                viz_item_list=[pcd, crop_box],
                folder=folder_names["input_settings"],
                filename=file_names["o3d_view"],
                axis=True,
            )


def pcd_process_corners_and_save(pcd_range, test_name, folder_names, file_names, vis_on=False):
    for i in pcd_range:

        print(
            "processing corners: {}".format(
                file_names["pntcloud_processed_ply"].format(test_name, i)
            )
        )

        pcd = load_pointcloud_ply(
            folder=folder_names["output_data1"].format(test_name),
            filename=file_names["pntcloud_processed_ply"].format(test_name, i),
        )

        # if vis_on:
        #     pnts = visualize_pcd_interactive(
        #         viz_item_list=[pcd],
        #         folder=folder_names["input_settings"],
        #         filename=file_names["o3d_view"],
        #         # axis=True,
        #     )

        if test_name == "spec_N6_3":
            polygons = np.array(
                [
                    [
                        [-0.005, 0.050, 0.220],
                        [-0.005, 0.100, 0.220],
                        [0.015, 0.100, 0.220],
                        [0.015, 0.050, 0.220],
                    ],
                    [
                        [0.21, 0.050, 0.220],
                        [0.21, 0.100, 0.220],
                        [0.29, 0.050, 0.220],
                        [0.29, 0.100, 0.220],
                    ],
                    [
                        [0.15, -0.018, 0.220],
                        [0.175, -0.0036, 0.220],
                        [0.185, -0.028, 0.220],
                        [0.16, -0.036, 0.220],
                    ],
                    [
                        [0.053, -0.0053, 0.220],
                        [0.074, -0.018, 0.220],
                        [0.074, -0.026, 0.220],
                        [0.021, -0.051, 0.220],
                    ],
                    [
                        [0.053, 0.15, 0.220],
                        [0.074, 0.16, 0.220],
                        [0.082, 0.19, 0.220],
                        [0.031, 0.19, 0.220],
                    ],
                    [
                        [0.15, 0.162, 0.225],
                        [0.17, 0.152, 0.225],
                        [0.19, 0.19, 0.225],
                        [0.14, 0.20, 0.225],
                    ],
                ]
            )

        crop_volumes = _make_crop_volumes(polygons)
        pcd_modified, bounding_boxes = _multi_color_change(pcd, crop_volumes)

        # save_pointcloud_ply(
        #     pcd,
        #     folder_names["output_data1"].format(test_name),
        #     file_names["pntcloud_processed_ply"].format(test_name, i),
        # )

        if vis_on:
            visualize_pcd(
                viz_item_list=bounding_boxes + [pcd_modified],
                folder=folder_names["input_settings"],
                filename=file_names["o3d_view"],
                axis=True,
            )


def pcd_threshold_and_save(pcd_range, test_name, folder_names, file_names, vis_on=False):
    """Identify and isolate features of interest (white dots) in the PCDs"""

    for i in pcd_range:

        print(
            "Finding points on: {}".format(
                file_names["pntcloud_processed_ply"].format(test_name, i)
            )
        )

        pcd = load_pointcloud_ply(
            folder=folder_names["output_data2"].format(test_name),
            filename=file_names["pntcloud_processed_ply"].format(test_name, i),
        )

        grayscale_values = np.array(pcd.colors).dot(np.array([0.2989, 0.5870, 0.1140]))

        mask_indices = [i for i, x in enumerate(grayscale_values > 0.70) if x]

        pcd_reduced = pcd.select_by_index(mask_indices)
        pcd_reduced.paint_uniform_color([1, 0, 0])

        pcd_leftover = pcd.select_by_index(mask_indices, invert=True)
        # pcd_leftover, ind = pcd_leftover.remove_statistical_outlier(nb_neighbors=10, std_ratio=0.2)

        # pcd_leftover.paint_uniform_color([0.5,0.5,0.5])

        print("original: {}\n reduced: {}".format(pcd, pcd_reduced))

        save_pointcloud_ply(
            pcd_reduced,
            folder_names["output_data3"].format(test_name),
            file_names["pntcloud_saved_pnts"].format(test_name, i),
        )

        if vis_on:
            visualize_pcd(
                viz_item_list=[pcd_leftover, pcd_reduced],
                folder=folder_names["input_settings"],
                filename=file_names["o3d_view"],
            )
