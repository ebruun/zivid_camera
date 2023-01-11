# PYTHON IMPORTS
import pathlib
import open3d as o3d
from datetime import datetime

# COMPAS IMPORTS
from compas_fab.utilities import read_data_from_json

# ZIVID IMPORTS
import zivid
from sample_utils.save_load_matrix import load_and_assert_affine_matrix
from sample_utils.transformation_matrix import TransformationMatrix


def _create_file_path(folder, filename):
    """create output data path.

    Returns:
        path: Output data path

    """
    path = pathlib.PurePath(
        pathlib.Path.cwd(),
        folder,
        filename,
    )

    # print("created path...", path)
    return path


def file_name(file_name, type):
    return file_name + type


def create_dynamic_filename(rob_num, n=00):
    str2 = datetime.now().strftime("%m_%d_n")
    return "R{}_".format(rob_num) + str2 + str(n)


def load_as_transformation_yaml(folder, input_file):
    file_name = _create_file_path(folder, input_file)

    matrix = load_and_assert_affine_matrix(file_name)

    trans = TransformationMatrix.from_matrix(matrix)

    trans = trans.inverse()

    return trans.as_matrix()


def load_pointcloud(folder, input_file):
    print("\nREAD IN POINTCLOUD")

    _ = zivid.Application()
    data_file_in = _create_file_path(folder, input_file)  # ZDF file

    print(f"--Reading ZDF frame from file: {data_file_in}")
    frame = zivid.Frame(data_file_in.__str__())
    point_cloud = frame.point_cloud()

    return point_cloud, frame


def load_pointcloud_ply(folder, filename):

    pcd = o3d.io.read_point_cloud(
        _create_file_path(
            folder=folder,
            filename=filename,
        ).__str__()
    )
    return pcd


def save_pointcloud_ply(pcd, folder, filename):

    o3d.io.write_point_cloud(
        _create_file_path(
            folder=folder,
            filename=filename,
        ).__str__(),
        pcd,
    )


def load_o3d_view_settings(folder, name):
    file_path = _create_file_path(folder, name)
    data = read_data_from_json(file_path)

    return data["trajectory"][0]


if __name__ == "__main__":
    # _create_file_path_robot("zerowaste_robot/transformations", "H1_cam_obj2.yaml")
    _create_file_path("transformations", "H1_cam_obj2.yaml")
