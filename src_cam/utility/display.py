import numpy as np
import open3d as o3d

from typing import Optional


def display_pointcloud(xyz: np.ndarray, rgb: np.ndarray, normals: Optional[np.ndarray] = None) -> None:
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