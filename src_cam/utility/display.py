# PYTHON IMPORTS
import numpy as np
import open3d as o3d
from typing import Optional

# LOCAL IMPORTS
from src_cam.utility.io import (
    load_o3d_view_settings,
)


def display_pointcloud(
    xyz: np.ndarray, rgb: np.ndarray, normals: Optional[np.ndarray] = None
) -> None:
    """Display point cloud provided from 'xyz' with colors from 'rgb'.
    Args:
        rgb: RGB image
        xyz: A numpy array of X, Y and Z point cloud coordinates
        normals: Ordered array of normal vectors, mapped to xyz
    """
    xyz = np.nan_to_num(xyz).reshape(-1, 3)
    if normals is not None:
        normals = np.nan_to_num(normals).reshape(-1, 3)
    rgb = rgb.reshape(-1, 3)

    point_cloud_open3d = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(xyz))
    point_cloud_open3d.colors = o3d.utility.Vector3dVector(rgb / 255)
    if normals is not None:
        point_cloud_open3d.normals = o3d.utility.Vector3dVector(normals)
        print("Open 3D controls:")
        print("  n: for normals")
        print("  9: for point cloud colored by normals")
        print("  h: for all controls")

    visualizer = o3d.visualization.Visualizer()  # pylint: disable=no-member
    visualizer.create_window()
    visualizer.add_geometry(point_cloud_open3d)

    if normals is None:
        visualizer.get_render_option().background_color = (0, 0, 0)
    visualizer.get_render_option().point_size = 1
    visualizer.get_render_option().show_coordinate_frame = True
    visualizer.get_view_control().set_front([0, 0, -1])
    visualizer.get_view_control().set_up([0, -1, 0])

    visualizer.run()
    visualizer.destroy_window()


def visualize_pcd(viz_item_list, folder, filename, box=False, axis=False):
    vis_settings = load_o3d_view_settings(folder, filename)

    # pcd.estimate_normals()

    if axis:
        # Show coordinate axis
        mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2, origin=[0, 0, 0])
        viz_item_list.append(mesh_frame)

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


def visualize_pcd_interactive(viz_item_list, folder, filename):
    print("")
    print("1) Please pick at least three correspondences using [shift + left click]")
    print("   Press [shift + right click] to undo point picking")
    print("2) Afther picking points, press q for close the window")

    pcd = viz_item_list[0]

    vis_settings = load_o3d_view_settings(folder, filename)
    pcd.estimate_normals()

    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window()
    vis.add_geometry(pcd)

    ctr = vis.get_view_control()
    ctr.set_front(vis_settings["front"])
    ctr.set_up(vis_settings["up"])
    ctr.set_zoom(vis_settings["zoom"])
    ctr.set_lookat(vis_settings["lookat"])

    vis.run()  # user picks points
    vis.destroy_window()
    print("")

    return vis.get_picked_points()
