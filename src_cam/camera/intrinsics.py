# PYTHON IMPORTS
import yaml
import numpy as np
from zivid.experimental.calibration import intrinsics

# LOCAL IMPORTS
from src_cam.utility.io import _create_file_path
from src_cam.camera.use import camera_connect


# read in and print intrinsics for a camera
# these values are saved in yaml files already
# write func to extract and save one day...
# https://github.com/zivid/zivid-python/pull/163
def _print_camera_intrinsics(camera):
    a = intrinsics(camera)
    print(a)


# Build camera intrinsics from the hard-coded values saved in "input folder"
# see the following convo on github https://github.com/zivid/zivid-python/issues/42#issuecomment-1020424432
def build_cam_intrinsics(file_name):

    with open(_create_file_path("input", file_name), "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    c = data["CameraIntrinsics"]["CameraMatrix"]

    mtx = np.array(
        [
            [c["FX"], 0, c["CX"]],
            [0, c["FY"], c["CY"]],
            [0, 0, 1],
        ]
    )

    d = data["CameraIntrinsics"]["Distortion"]

    dist = np.array([d["K1"], d["K2"], d["P1"], d["P2"], d["K3"]])  # diff format

    return mtx, dist


if __name__ == "__main__":

    rob_num = 2
    camera = camera_connect(rob_num)

    _print_camera_intrinsics(camera)

    f = "intrinsics_z{}.yml".format(rob_num)

    mtx, dist = build_cam_intrinsics(f)

    print("mtx", mtx)
    print("dist", dist)
