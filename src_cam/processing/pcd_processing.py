# PYTHON IMPORTS
import open3d as o3d
import numpy as np


# LOCAL IMPORTS
from src_cam.utility.io import (
    _create_file_path,
    load_o3d_view_settings,
    load_pointcloud,
    load_as_transformation_yaml,
)

def test():
    print("import working")

def _visualize_pcd(viz_item_list, folder, filename):
    vis_settings = load_o3d_view_settings(folder, filename)

    # pcd.estimate_normals()

    o3d.visualization.draw_geometries(
        viz_item_list,
        left=10,
        top=50,
        width=1600,
        height=900,
        zoom=vis_settings["zoom"],
        front=vis_settings["front"],
        lookat=vis_settings["lookat"],
        up=vis_settings["up"],
    )


def _visualize_pcd_interactive(viz_item_list, folder, filename):
    print("")
    print("1) Please pick at least three correspondences using [shift + left click]")
    print("   Press [shift + right click] to undo point picking")
    print("2) Afther picking points, press q for close the window")

    pcd = viz_item_list[0]

    # vis_settings = load_o3d_view_settings(folder, filename)
    pcd.estimate_normals()

    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window()
    vis.add_geometry(pcd)

    # ctr = vis.get_view_control()
    # ctr.set_front(vis_settings["front"])
    # ctr.set_up(vis_settings["up"])
    # ctr.set_zoom(vis_settings["zoom"])
    # ctr.set_lookat(vis_settings["lookat"])

    vis.run()  # user picks points
    vis.destroy_window()
    print("")

    return vis.get_picked_points()


def pcd_segment(pcd_range, test_name, folder_names, file_names, vis_on=False):

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
            _visualize_pcd(
                viz_item_list=[pcd_reduced, pcd_leftover],
                folder=folder_names["input_settings"],
                filename=file_names["o3d_view"],
            )


def pcd_stitch_and_crop(pcd_range, test_name, folder_names, file_names, vis_on=False):

    for i in pcd_range:

        point_data = []
        color_data = []

        for cam_num in [1, 2]:

            pcd = o3d.io.read_point_cloud(
                _create_file_path(
                    folder=folder_names["input_data"].format(test_name),
                    filename=file_names["pntcloud_trns_ply"].format(i, cam_num),
                ).__str__()
            )

            point_data.append(np.asarray(pcd.points))
            color_data.append(np.asarray(pcd.colors))

        points_combined = np.concatenate(point_data, axis=0) / 1000  # mm -> m
        colors_combined = np.concatenate(color_data, axis=0)

        pcd_combined = o3d.geometry.PointCloud()
        pcd_combined.points = o3d.utility.Vector3dVector(points_combined)
        pcd_combined.colors = o3d.utility.Vector3dVector(colors_combined)

        # Rotate full pointcloud so that +z is aligned with "up" in real world
        R = pcd_combined.get_rotation_matrix_from_xyz((np.pi, 0, 0))
        pcd_combined = pcd_combined.rotate(R, center=(0, 0, 0))

        # cropping box
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

        pcd_combined_cropped = pcd_combined.crop(obb)

        # Get rid of black base
        grayscale_values = np.array(pcd_combined_cropped.colors).dot(
            np.array([0.2989, 0.5870, 0.1140])
        )
        mask_indices = [i for i, x in enumerate(grayscale_values > 0.05) if x]
        pcd_combined_cropped_masked = pcd_combined_cropped.select_by_index(mask_indices)

        # Remove Outliers
        (
            pcd_combined_cropped_masked_outlier,
            _,
        ) = pcd_combined_cropped_masked.remove_statistical_outlier(nb_neighbors=10, std_ratio=1.5)

        print(
            "original: {} \nafter crop: {} \nafter color mask: {} \nafter outlier1: {}".format(
                pcd,
                pcd_combined_cropped,
                pcd_combined_cropped_masked,
                pcd_combined_cropped_masked_outlier,
            )
        )

        pcd_save = pcd_combined_cropped_masked_outlier

        o3d.io.write_point_cloud(
            _create_file_path(
                folder=folder_names["output_data"].format(test_name),
                filename=file_names["pntcloud_processed_ply"].format(test_name, i),
            ).__str__(),
            pcd_save,
        )

        if vis_on:
            # Get a nice looking bounding box to display around the newly cropped point cloud
            bounding_box = pcd_combined_cropped.get_axis_aligned_bounding_box()
            bounding_box.color = (1, 0, 0)

            # Show coordinate axis
            mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
                size=0.2, origin=[0, 0, 0]
            )

            _visualize_pcd(
                viz_item_list=[pcd_save, bounding_box, mesh_frame],
                folder=folder_names["input_settings"],
                filename=file_names["o3d_view"],
            )


def pcd_transform_and_save(pcd_range, test_name, folder_names, file_names):

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
