# PYTHON IMPORTS
# from pathlib import Path
# import os
from time import process_time
import keyboard

# ZIVID IMPORTS
import zivid
import zivid.capture_assistant as capture_assistant
from zivid.capture_assistant import SuggestSettingsParameters as sgst_params

# LOCAL IMPORTS
from src_cam.utility.io import _create_file_path
from src_cam.utility.io import load_pointcloud
from src_cam.camera.convert import convert2png
from src_cam.camera.use import (
    _list_connected_cameras,
    camera_connect,
    camera_capture_settings,
    camera_capture_and_save,
    pc_downsample,
)

from src_cam.processing.checker_calc import checkboard_pose_calc
from sample_utils.save_load_matrix import load_and_assert_affine_matrix
from sample_utils.transformation_matrix import TransformationMatrix
from applications.basic.file_formats.convert_zdf import _convert_2_ply


def load_as_transformation_yaml(folder, input_file):
    file_name = _create_file_path(folder, input_file)

    matrix = load_and_assert_affine_matrix(file_name)

    trans = TransformationMatrix.from_matrix(matrix)

    trans = trans.inverse()

    return trans.as_matrix()


def main_transform(range):

    cam_nums = [1, 2]
    output_folder = "saved_output"

    file_names = {
        "pntcloud": "{:02d}_cam{}_3d.zdf",
        "pntcloud_trns_zdf": "{:02d}_cam{}_3d_TRNS.zdf",
        "pntcloud_trns_ply": "{:02d}_cam{}_3d_TRNS",
        "t_matrix": "{:02d}_cam{}_trans.yml",
    }

    for i in range:

        for cam_num in cam_nums:

            trans = load_as_transformation_yaml(
                folder=output_folder,
                input_file=file_names["t_matrix"].format(i, cam_num),
            )

            pc, frame = load_pointcloud(
                folder=output_folder, input_file=file_names["pntcloud"].format(i, cam_num)
            )

            pc.transform(trans)

            pointcloud_file_path = _create_file_path(
                output_folder, file_names["pntcloud_trns_zdf"].format(i, cam_num)
            )
            frame.save(pointcloud_file_path)

            pointcloud_file_path = _create_file_path(
                output_folder, file_names["pntcloud_trns_ply"].format(i, cam_num)
            )
            _convert_2_ply(frame, pointcloud_file_path)


def main_capture():

    idx = int(input("Please enter a an index to start at: "))

    cam_nums = [1, 2]
    output_folder = "saved_output"
    settings_folder = "input_settings"

    file_names = {
        "pntcloud": "{:02d}_cam{}_3d.zdf",
        "img": "{:02d}_cam{}_2d.png",
        "t_matrix": "{:02d}_cam{}_trans.yml",
    }

    while idx < 200:
        input("\nPress ENTER to start capture #{:02d}".format(idx))

        t_start = process_time()
        for cam_num in cam_nums:

            try:
                camera = camera_connect(cam_num)
            except RuntimeError:
                print("--camera connect error: camera already connected")
                print("--camera connect error: or ZIVID studio is open (close it!)")

            settings = camera_capture_settings(
                camera,
                folder=settings_folder,
                input_file="capture_settings_z{}.yml".format(cam_num),
            )

            with camera.capture(settings) as frame:

                pc = frame.point_cloud()

                pc_downsample(pc, downsample_factor=1, display=False)

                pointcloud_file_path = _create_file_path(
                    output_folder, file_names["pntcloud"].format(idx, cam_num)
                )

                frame.save(pointcloud_file_path)

                _ = convert2png(
                    pointcloud=pc,
                    folder=output_folder,
                    output_file=file_names["img"].format(idx, cam_num),
                )

                try:
                    checkboard_pose_calc(
                        pointcloud=pc,
                        folder=output_folder,
                        output_file=file_names["t_matrix"].format(idx, cam_num),
                        display=False,
                    )
                except RuntimeError:
                    print("\n NO CHECKERBOARD SEEN!!!")

        t_stop = process_time()
        t_elapsed = t_stop - t_start

        print("capture #{:02d} completed, elapsed time = {:.2f}s".format(idx, t_elapsed))

        idx += 1


if __name__ == "__main__":

    # _list_connected_cameras()
    # main_capture()

    main_transform(range(0, 3))
