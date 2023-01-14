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


def _combine_pcd(pcds, scale=1):
    """combine and scale two pointclouds as ply files"""
    point_data = []
    color_data = []

    for pcd in pcds:
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


def _multi_points_delete(pcd, crop_volumes):
    """delete points in a specified volume"""

    points_delete = []
    bounding_boxes = []

    for crop_volume in crop_volumes:
        pcd_delete = crop_volume.crop_point_cloud(pcd)
        points_delete.append(np.asarray(pcd_delete.points))

        bounding_box = pcd_delete.get_oriented_bounding_box()
        bounding_box.color = (0, 0, 1)

        bounding_boxes.append(bounding_box)

    points_delete = np.concatenate(points_delete, axis=0)

    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)

    A, B = _view1D(points, points_delete)
    row_indices_duplicate = np.isin(A, B)  # boolean array

    points_remaining = points[~row_indices_duplicate]
    colors_remaining = colors[~row_indices_duplicate]

    pcd_remaining = o3d.geometry.PointCloud()
    pcd_remaining.points = o3d.utility.Vector3dVector(points_remaining)
    pcd_remaining.colors = o3d.utility.Vector3dVector(colors_remaining)

    return pcd_remaining, bounding_boxes


def _multi_color_change(pcd, crop_volumes):
    """change color of points in a specified volume"""

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
                folder=folder_names["data1_raw"].format(test_name),
                input_file=file_names["t_matrix"].format(i, cam_num),
            )

            pc, frame = load_pointcloud(
                folder=folder_names["data1_raw"].format(test_name),
                input_file=file_names["pntcloud"].format(i, cam_num),
            )

            # Transform
            pc.transform(trans)

            # Save as ZDF
            pointcloud_file_path = _create_file_path(
                folder=folder_names["data1_raw"].format(test_name),
                filename=file_names["pntcloud_trns_zdf"].format(i, cam_num),
            )
            frame.save(pointcloud_file_path)

            # Save as PLY
            pointcloud_file_path = _create_file_path(
                folder=folder_names["data1_raw"].format(test_name),
                filename=file_names["pntcloud_trns_ply"].format(i, cam_num),
            )
            frame.save(pointcloud_file_path)


def pcd_process_and_save(pcd_range, test_name, folder_names, file_names, vis_on=False):
    """process the PCD in various ways: combine, rotate, crop, mask, outlier removal"""

    for i in pcd_range:

        print("\nprocessing: {}".format(file_names["pntcloud_processed_ply"].format(test_name, i)))

        pcds = []
        for cam_num in [1, 2]:

            loaded_pcd = load_pointcloud_ply(
                folder_names["data1_raw"].format(test_name),
                file_names["pntcloud_trns_ply"].format(i, cam_num),
            )

            pcds.append(loaded_pcd)

        pcd = _combine_pcd(pcds, scale=0.001)
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
            folder_names["data2_processed"].format(test_name),
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
            folder=folder_names["data2_processed"].format(test_name),
            filename=file_names["pntcloud_processed_ply"].format(test_name, i),
        )

        if vis_on:
            pnts = visualize_pcd_interactive(
                viz_item_list=[pcd],
                folder=folder_names["input_settings"],
                filename=file_names["o3d_view"],
                # axis=True,
            )
            print(np.asarray(pcd.points)[pnts])

        if test_name == "spec_N6_3":
            color_polygons = np.array(
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

        elif test_name == "spec_N5_3":
            color_polygons = np.array(
                [
                    [
                        [0.13, -0.015, 0.220],  # corners
                        [0.15, -0.0087, 0.220],
                        [0.16, -0.051, 0.220],
                        [0.13, -0.056, 0.220],
                    ],
                    [
                        [0.035, 0.031, 0.220],
                        [0.047, 0.014, 0.220],
                        [-0.035, -0.03, 0.220],
                        [-0.027, 0.015, 0.220],
                    ],
                    [
                        [0.048, 0.13, 0.220],
                        [0.035, 0.12, 0.220],
                        [-0.020, 0.05, 0.220],
                        [0.017, 0.17, 0.220],
                    ],
                    [
                        [0.155, 0.155, 0.220],
                        [0.13, 0.16, 0.220],
                        [0.14, 0.19, 0.220],
                        [0.17, 0.17, 0.220],
                    ],
                    [
                        [0.2, 0.062, 0.220],
                        [0.2, 0.087, 0.220],
                        [0.22, 0.084, 0.220],
                        [0.22, 0.065, 0.220],
                    ],
                    [
                        [0.043, 0.02, 0.210],  # sides
                        [0.14, -0.012, 0.210],
                        [0.13, -0.023, 0.210],
                        [0.042, 0.011, 0.210],
                    ],
                    [
                        [0.14, -0.0084, 0.210],
                        [0.2, 0.07, 0.210],
                        [0.21, 0.064, 0.210],
                        [0.15, -0.016, 0.210],
                    ],
                    [
                        [0.039, 0.12, 0.210],
                        [0.039, 0.026, 0.210],
                        [0.027, 0.023, 0.210],
                        [0.027, 0.13, 0.210],
                    ],
                    [
                        [0.14, 0.16, 0.210],
                        [0.045, 0.13, 0.210],
                        [0.038, 0.14, 0.210],
                        [0.14, 0.17, 0.210],
                    ],
                    [
                        [0.2, 0.078, 0.210],
                        [0.14, 0.16, 0.210],
                        [0.15, 0.17, 0.210],
                        [0.21, 0.083, 0.210],
                    ],
                ]
            )

            delete_polygons = [
                np.array(
                    [
                        [0.1529166, -0.01611024, 0.20],
                        [0.19471136, -0.02285242, 0.20],
                        [0.21088745, -0.01519365, 0.20],
                        [0.22872858, 0.04915744, 0.20],
                        [0.21668607, 0.06462979, 0.20],
                        [0.20088504, 0.06146107, 0.20],
                        [0.15061945, -0.00818526, 0.20],
                    ]
                ),
                np.array(
                    [
                        [0.04558737, 0.01368767, 0.20],
                        [0.03764117, -0.0148172, 0.20],
                        [0.05197833, -0.02188771, 0.20],
                        [0.06824371, -0.02205147, 0.20],
                        [0.13191617, -0.02314828, 0.20],
                        [0.128108, -0.0132541, 0.20],
                    ]
                ),
                np.array(
                    [
                        [0.03529871, 0.11781342, 0.2],
                        [0.02415088, 0.12590814, 0.2],
                        [0.02184369, 0.04133041, 0.2],
                        [0.02177271, 0.02243735, 0.2],
                        [0.03464105, 0.03030618, 0.2],
                    ]
                ),
                np.array(
                    [
                        [0.04610632, 0.1369007, 0.2],
                        [0.04788623, 0.13487723, 0.2],
                        [0.12851248, 0.15966498, 0.2],
                        [0.13201035, 0.16809216, 0.2],
                        [0.06820551, 0.17120758, 0.2],
                        [0.05513959, 0.17119415, 0.2],
                        [0.03204877, 0.16839441, 0.2],
                        [0.02287036, 0.15415363, 0.2],
                    ]
                ),
                np.array(
                    [
                        [0.15061722, 0.15597513, 0.2],
                        [0.20150677, 0.0846152, 0.2],
                        [0.20988593, 0.08422189, 0.2],
                        [0.21821747, 0.08422278, 0.2],
                        [0.20388962, 0.15890372, 0.2],
                        [0.20131342, 0.16644717, 0.2],
                        [0.16270276, 0.16677191, 0.2],
                    ]
                ),
            ]

        color_volumes = _make_crop_volumes(color_polygons)
        delete_volumes = _make_crop_volumes(delete_polygons)

        pcd_modified1, bounding_boxes1 = _multi_color_change(pcd, color_volumes)
        pcd_modified2, bounding_boxes2 = _multi_points_delete(pcd_modified1, delete_volumes)

        save_pointcloud_ply(
            pcd_modified2,
            folder_names["data2_processed"].format(test_name),
            file_names["pntcloud_processed_ply"].format(test_name, i),
        )

        if vis_on:
            visualize_pcd(
                viz_item_list=bounding_boxes1 + bounding_boxes2 + [pcd_modified2],
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
            folder=folder_names["data3_processed_clean"].format(test_name),
            filename=file_names["pntcloud_processed_ply"].format(test_name, i),
        )

        grayscale_values = np.array(pcd.colors).dot(np.array([0.2989, 0.5870, 0.1140]))

        mask_indices = [i for i, x in enumerate(grayscale_values > 0.52) if x]

        pcd_reduced = pcd.select_by_index(mask_indices)
        pcd_reduced.paint_uniform_color([1, 0, 0])

        pcd_leftover = pcd.select_by_index(mask_indices, invert=True)

        print("original: {}\n reduced: {}".format(pcd, pcd_reduced))

        save_pointcloud_ply(
            pcd_reduced,
            folder_names["data4_found_points"].format(test_name),
            file_names["pntcloud_saved_pnts"].format(test_name, i),
        )

        if vis_on:
            visualize_pcd(
                viz_item_list=[pcd_leftover, pcd_reduced],
                folder=folder_names["input_settings"],
                filename=file_names["o3d_view"],
            )
