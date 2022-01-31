# PYTHON IMPORTS
import pathlib
import numpy as np
import cv2 as cv
from datetime import datetime

# COMPAS IMPORTS
from compas.geometry import Transformation


def _create_file_path_robot(folder, filename):
    """create output data path.

    Returns:
        path: Output data path

    """
    path = pathlib.PurePath(
        pathlib.Path.cwd().parent,  # up to root folder
        folder,
        filename,
    )

    # print("created path...", path)
    return path


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


def create_dynamic_filename(n=00):
    str2 = datetime.now().strftime("%m_%d_n")
    return str2 + str(n)


def save_frames_as_matrix_yaml(folder, name, frames):
    file_name = _create_file_path_robot(folder, name).__str__()
    s = cv.FileStorage(file_name, cv.FileStorage_WRITE)

    for i, f in enumerate(frames):
        T = Transformation.from_frame(f)
        PoseState = np.array(T)
        s.write("PoseState{}".format(i), PoseState)

    s.release()


if __name__ == "__main__":
    _create_file_path_robot("zerowaste_robot/transformations", "H1_cam_obj2.yaml")
    _create_file_path("transformations", "H1_cam_obj2.yaml")
