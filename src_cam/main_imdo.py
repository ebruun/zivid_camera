# PYTHON IMPORTS
from pathlib import Path
import os
from time import process_time

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


def main_transform():

    cam_nums = [1, 2]

    for i in range(1):
        for cam_num in cam_nums:

            trans = load_as_transformation_yaml(
                folder="saved_output",
                input_file="{:02d}_cam{}_trans.yml".format(i, cam_num),
            )

            pc, frame = load_pointcloud(
                folder="saved_output", input_file="{:02d}_cam{}_3d.zdf".format(i, cam_num)
            )

            pc.transform(trans)

            folder = "saved_output"
            output_file = "{:02d}_cam{}_3d_TRNS.zdf".format(i, cam_num)
            pointcloud_file_path = _create_file_path(folder, output_file)
            frame.save(pointcloud_file_path)

            folder = "saved_output"
            output_file = "{:02d}_cam{}_3d_TRNS".format(i, cam_num)
            pointcloud_file_path = _create_file_path(folder, output_file)
            _convert_2_ply(frame, pointcloud_file_path)


def main_capture():
    for i in range(1):
        cam_nums = [1, 2]

        for cam_num in cam_nums:

            try:
                camera = camera_connect(cam_num)
            except RuntimeError:
                print("--camera connect error: camera already connected")
                print("--camera connect error: or ZIVID studio is open (close it!)")

            folder = "saved_output"
            output_file = "{:02d}_cam{}_3d.zdf".format(i, cam_num)
            pointcloud_file_path = _create_file_path(folder, output_file)

            settings = camera_capture_settings(
                camera,
                folder="input_settings",
                input_file="capture_settings_z{}.yml".format(cam_num),
            )

            with camera.capture(settings) as frame:

                pc = frame.point_cloud()

                pc_downsample(pc, downsample_factor=4, display=False)

                frame.save(pointcloud_file_path)

                _ = convert2png(
                    pointcloud=pc,
                    folder="saved_output",
                    output_file="{:02d}_cam{}_2d.png".format(i, cam_num),
                )

                try:
                    checkboard_pose_calc(
                        pointcloud=pc,
                        folder="saved_output",
                        output_file="{:02d}_cam{}_trans.yml".format(i, cam_num),
                        display=True,
                    )
                except RuntimeError:

                    print("\n NO CHECKERBOARD SEEN!!!")


if __name__ == "__main__":

    # _list_connected_cameras()
    # main_capture()

    main_transform()
