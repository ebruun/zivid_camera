# PYTHON IMPORTS
from time import process_time
import open3d as o3d

# LOCAL IMPORTS
from src_cam.utility.io import _create_file_path, load_pointcloud, load_as_transformation_yaml

from src_cam.camera.convert import convert2png, convert2ply

from src_cam.camera.use import (
    _list_connected_cameras,
    camera_connect,
    camera_capture_settings,
    pc_downsample,
)

from src_cam.processing.pcd_processing import pcd_stitch_individual_rob

from src_cam.processing.checker_calc import checkboard_pose_calc


def main_process(pcd_range, test_name):

    cam_nums = [1, 2]

    folder_names = {
        "input_data": "saved_output_raw/{}}",
        "output_data": "saved_output_processed/{}}",
    }

    file_names = {
        "pntcloud": "{:02d}_ziv{}_3d.zdf",
        "pntcloud_trns_zdf": "{:02d}_ziv{}_3d_TRNS.zdf",
        "pntcloud_trns_ply": "{:02d}_ziv{}_3d_TRNS",
        "t_matrix": "{:02d}_ziv{}_trans.yml",
    }

    for i in pcd_range:

        # point_data = []
        # color_data = []

        for cam_num in cam_nums:

            _ = o3d.io.read_point_cloud(
                _create_file_path(
                    folder=folder_names["input_data"].format(test_name),
                    filename=file_names["pntcloud_trns_ply"].format(i, cam_num),
                ).__str__()
            )

        pcd_stitch_individual_rob(pcd_range)


def main_transform(range, test_name):

    cam_nums = [1, 2]

    folder_names = {
        "input_data": "saved_output_raw/{}",
        "output_data": "saved_output_processed/{}",
    }

    file_names = {
        "pntcloud": "{:02d}_ziv{}_3d.zdf",
        "pntcloud_trns_zdf": "{:02d}_ziv{}_3d_TRNS.zdf",
        "pntcloud_trns_ply": "{:02d}_ziv{}_3d_TRNS",
        "t_matrix": "{:02d}_ziv{}_trans.yml",
    }

    for i in range:

        for cam_num in cam_nums:

            trans = load_as_transformation_yaml(
                folder=folder_names["input_data"].format(test_name),
                input_file=file_names["t_matrix"].format(i, cam_num),
            )

            pc, frame = load_pointcloud(
                folder=folder_names["input_data"].format(test_name),
                input_file=file_names["pntcloud"].format(i, cam_num),
            )

            pc.transform(trans)

            pointcloud_file_path = _create_file_path(
                folder=folder_names["input_data"].format(test_name),
                filename=file_names["pntcloud_trns_zdf"].format(i, cam_num),
            )
            frame.save(pointcloud_file_path)

            pointcloud_file_path = _create_file_path(
                folder=folder_names["input_data"].format(test_name),
                filename=file_names["pntcloud_trns_ply"].format(i, cam_num),
            )
            convert2ply(frame, pointcloud_file_path)


def main_capture():

    idx = int(input("Please enter a an index to start at: "))

    cam_nums = [1, 2]
    output_folder = "saved_output"
    settings_folder = "input_settings"

    file_names = {
        "pntcloud": "{:02d}_ziv{}_3d.zdf",
        "pntcloud_reduced": "{:02d}_ziv{}_3d_reduced.zdf",
        "img": "{:02d}_ziv{}_2d.png",
        "t_matrix": "{:02d}_ziv{}_trans.yml",
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
                # input_file="capture_settings_z{}.yml".format(cam_num),
            )

            pointcloud_file_path1 = _create_file_path(
                output_folder, file_names["pntcloud"].format(idx, cam_num)
            )

            pointcloud_file_path2 = _create_file_path(
                output_folder, file_names["pntcloud_reduced"].format(idx, cam_num)
            )

            with camera.capture(settings) as frame:

                frame.save(pointcloud_file_path1)

                pc = frame.point_cloud()

                pc_downsample(pc, downsample_factor=4, display=False)
                frame.save(pointcloud_file_path2)

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
                    print("\nNO CHECKERBOARD SEEN!!!")

        t_stop = process_time()
        t_elapsed = t_stop - t_start

        print("\ncapture #{:02d} completed, elapsed time = {:.2f}s".format(idx, t_elapsed))

        idx += 1


if __name__ == "__main__":

    # _list_connected_cameras()
    # main_capture()

    test_name = "spec_N3_3"

    # main_transform(range(0, 1)test_name)
    main_process(range(0, 1), test_name)
