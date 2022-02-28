# PYTHON IMPORTS
import pathlib
import zivid
from datetime import datetime


# def _create_file_path_robot(folder, filename):
#     """create output data path.

#     Returns:
#         path: Output data path

#     """
#     path = pathlib.PurePath(
#         pathlib.Path.cwd().parent,  # up to root folder
#         folder,
#         filename,
#     )

#     # print("created path...", path)
#     return path


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


def load_pointcloud(folder, input_file):
    print("\nREAD IN POINTCLOUD")

    _ = zivid.Application()
    data_file_in = _create_file_path(folder, input_file)  # ZDF file

    print(f"--Reading ZDF frame from file: {data_file_in}")
    frame = zivid.Frame(data_file_in.__str__())
    point_cloud = frame.point_cloud()

    return point_cloud, frame


if __name__ == "__main__":
    # _create_file_path_robot("zerowaste_robot/transformations", "H1_cam_obj2.yaml")
    _create_file_path("transformations", "H1_cam_obj2.yaml")
