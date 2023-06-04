# PYTHON IMPORTS

# LOCAL IMPORTS
from src_cam.camera.use import (
    _list_connected_cameras,
    camera_capture_and_save_IMDO,
)

from src_cam.processing.pcd_processing import (
    pcd_transform_and_save,
    pcd_process_and_save,
    pcd_process_corners_and_save,
    pcd_threshold_and_save,
)


def main_capture(test_name, folder_names, file_names):
    """camera --> data1_raw"""
    _list_connected_cameras()
    idx = int(input("Please enter a an index to start at: "))
    camera_capture_and_save_IMDO(idx, test_name, folder_names, file_names)
    pass


def main_transform_pcd(pcd_range, cameras, test_name, folder_names, reduced_flag, file_names):
    """data1_raw --> data1_raw (TRNS)
    make sure to set whether using the ORIGINAL or REDUCED file
    """
    pcd_transform_and_save(pcd_range, cameras, test_name, folder_names, reduced_flag, file_names)


def main_process_pcd(
    pcd_range, cameras, test_name, folder_names, file_names, scale=0.001, vis_on=False
):
    """data1_raw (TRNS) --> data2_processed
    scale from mm --> m
    """
    pcd_process_and_save(pcd_range, cameras, test_name, folder_names, file_names, scale, vis_on)


def main_process_pcd2(pcd_range, test_name, folder_names, file_names, vis_on=False):
    """data2_processed --> data2_processed (overwrite)
    CHECK THE DELETE VOLUMES FIRST
    """
    pcd_process_corners_and_save(pcd_range, test_name, folder_names, file_names, vis_on)


def main_locate_pnts_pcd(pcd_range, test_name, folder_names, file_names, vis_on=False):
    """data3_processed_clean --> data4_found_points"""
    pcd_threshold_and_save(pcd_range, test_name, folder_names, file_names, vis_on)


if __name__ == "__main__":
    folder_names = {
        "input_settings": "input_settings",
        "data1_raw": "data1_raw/{}",
        "data2_processed": "data2_processed/{}",
        "data3_processed_clean": "data3_processed_clean/{}",
        "data4_found_points": "data4_found_points/{}",
    }

    file_names = {
        "pntcloud": "{:02d}_ziv{}_3d.zdf",  # original
        "pntcloud_reduced": "{:02d}_ziv{}_3d_REDUCED .zdf",  # original_reduced (NEED THE SPACE IN NAME)
        "pntcloud_trns_zdf": "{:02d}_ziv{}_3d_TRNS.zdf",  # after main_transform_pcd
        "pntcloud_trns_ply": "{:02d}_ziv{}_3d_TRNS.ply",  # after main_transform_pcd
        "pntcloud_processed_ply": "{}_step{:02d}_3d_PROCESSED.ply",  # after main_transform_pcd and 2
        "pntcloud_saved_pnts": "{}_step{:02d}_3d_POINTS.ply",  # after main_locate_pnts_pcd
        "img": "{:02d}_ziv{}_3d_REDUCED.png",
        "t_matrix": "{:02d}_ziv{}_trans.yml",
        "o3d_view": "o3d_view_settings.json",
        "capture_settings": "capture_settings_calibration.yml",
    }

    cameras = [1, 2]
    reduced_flag = False

    test_name = "spec_N4_EB_3"

    # main_capture(test_name, folder_names, file_names)
    # main_transform_pcd(range(0, 1), cameras, test_name, folder_names, reduced_flag, file_names)
    # main_process_pcd(range(0, 1), cameras, test_name, folder_names, file_names, scale=0.001, vis_on=True)

    ### CHECK THE DELETE VOLUMES FIRST###
    # main_process_pcd2(range(0, 1), test_name, folder_names, file_names, vis_on=True)

    # main_locate_pnts_pcd(range(0, 1), test_name, folder_names, file_names, vis_on=True)
