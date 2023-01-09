# PYTHON IMPORTS
import open3d as o3d
import numpy as np


# LOCAL IMPORTS
from src_cam.utility.io  import (
    _create_file_path,
    load_o3d_view_settings,
)




def _visualize_pcd(pcd, folder, filename):
    vis_settings = load_o3d_view_settings(folder, filename)

    pcd.estimate_normals()

    o3d.visualization.draw_geometries(
        [pcd],
        left=10,
        top=50,
        width=1600,
        height=900,
        zoom=vis_settings["zoom"],
        front=vis_settings["front"],
        lookat=vis_settings["lookat"],
        up=vis_settings["up"],
    )


def pcd_stitch_individual_rob(rob_nums, pc_range, folders, filenames, pcd_vars, vis_on=False):
    """
    combine pointclouds from all captures with a single robot
    """

    print("START POINTCLOUD STITCH\n")
    for i in pc_range:
    
        point_data = []
        color_data = []

        for rob_num in rob_nums:
            pcd = o3d.io.read_point_cloud(
                _create_file_path(
                    folder=folders[2].format(rob_num), filename=filenames[1].format(i)
                ).__str__()
            )

            # reduce individual files (otherwise too slow when all together)
            pcd = pcd.voxel_down_sample(voxel_size=pcd_vars["voxels"])
            pcd, _ = pcd.remove_statistical_outlier(
                nb_neighbors=pcd_vars["neighbors"], std_ratio=pcd_vars["std_dev"]
            )

            point_data.append(np.asarray(pcd.points))
            color_data.append(np.asarray(pcd.colors))

        points_combined = np.concatenate(point_data, axis=0) / 1000  # mm -> m
        colors_combined = np.concatenate(color_data, axis=0)

        pcd_combined = o3d.geometry.PointCloud()
        pcd_combined.points = o3d.utility.Vector3dVector(points_combined)
        pcd_combined.colors = o3d.utility.Vector3dVector(colors_combined)

        # reduce when all together
        pcd_combined = pcd_combined.voxel_down_sample(voxel_size=pcd_vars["voxels"])
        # pcd_combined, _ = pcd_combined.remove_statistical_outlier(
        #     nb_neighbors=pcd_vars["neighbors"], std_ratio=pcd_vars["std_dev"]
        # )
        # pcd_combined, _ = pcd_combined.remove_radius_outlier(
        #     nb_points=pcd_vars["radius_pnts"], radius=pcd_vars["radius"]
        # )

        if vis_on:
            _visualize_pcd(
                pcd_combined,
                folders[2].format(rob_num),
                filenames[6].format(rob_num),
            )

        o3d.io.write_point_cloud(
            _create_file_path(
                folder=folders[2].format(rob_num), filename=filenames[5].format(rob_num)
            ).__str__(),
            pcd_combined,
        )