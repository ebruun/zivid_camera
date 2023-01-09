# PYTHON IMPORTS
from time import process_time

# LOCAL IMPORTS
from src_cam.utility.io import _create_file_path

from src_cam.camera.convert import convert2png

from src_cam.camera.use import (
    _list_connected_cameras,
    camera_connect,
    camera_capture_settings,
    pc_downsample,
)

from src_cam.processing.pcd_processing import pcd_stitch_and_crop, pcd_transform_and_save

from src_cam.processing.checker_calc import checkboard_pose_calc


def main_process(pcd_range, test_name, vis_on=False):

    folder_names = {
        "input_data": "saved_output_raw/{}",
        "input_settings": "input_settings",
        "output_data": "saved_output_processed/{}",
    }

    file_names = {
        "pntcloud": "{:02d}_ziv{}_3d.zdf",
        "pntcloud_trns_zdf": "{:02d}_ziv{}_3d_TRNS.zdf",
        "pntcloud_trns_ply": "{:02d}_ziv{}_3d_TRNS.ply",
        "pntcloud_processed_ply": "{}_step{:02d}_3d_PROCESSED.ply",
        "t_matrix": "{:02d}_ziv{}_trans.yml",
        "o3d_view": "o3d_view_settings.json",
    }

    pcd_stitch_and_crop(pcd_range, test_name, folder_names, file_names, vis_on)

    # pcd = o3d.io.read_point_cloud(
    #     _create_file_path(
    #         folder=folder_names["output_data"].format(test_name),
    #         filename=file_names["pntcloud_processed_ply"].format(test_name, 10),
    #     ).__str__()
    # )

    # o3d.visualization.draw_geometries([pcd])


def main_transform(pcd_range, test_name):

    folder_names = {
        "input_data": "saved_output_raw/{}",
        "output_data": "saved_output_processed/{}",
    }

    file_names = {
        "pntcloud": "{:02d}_ziv{}_3d.zdf",
        "pntcloud_trns_zdf": "{:02d}_ziv{}_3d_TRNS.zdf",
        "pntcloud_trns_ply": "{:02d}_ziv{}_3d_TRNS.ply",
        "t_matrix": "{:02d}_ziv{}_trans.yml",
    }

    pcd_transform_and_save(pcd_range, test_name, folder_names, file_names)


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

    test_name = "spec_N6_3"

    main_transform(range(0, 1), test_name)
    # main_process(range(0, 40), test_name, vis_on=False)
