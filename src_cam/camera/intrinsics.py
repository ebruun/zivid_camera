# PYTHON IMPORTS
import yaml
import numpy as np

# LOCAL IMPORTS
from src_cam.utility.io import create_file_path


# Build camera intrinsics from the hard-coded values saved in "input folder"
# see the following convo on github https://github.com/zivid/zivid-python/issues/42#issuecomment-1020424432
def build_cam_intrinsics(file_name):

    with open(create_file_path("input", file_name), 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    c = data['CameraIntrinsics']['CameraMatrix']

    mtx = np.array([
        [c['FX'], 0, c['CX']],
        [0, c['FY'], c['CY']],
        [0, 0, 1],
    ])

    d = data['CameraIntrinsics']['Distortion']

    dist = np.array([d['K1'], d['K2'], d['P1'], d['P2'], d['K3']])

    return mtx, dist


if __name__ == "__main__":
    f = "intrinsics_zivid1.yml"
    mtx, dist = build_cam_intrinsics(f)

    print("mtx", mtx)
