# PYTHON IMPORTS
import datetime
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
    camera_capture_and_save
)



_list_connected_cameras()

cam_num = 1

camera = camera_connect(cam_num)

settings = camera_capture_settings(
    camera,
    folder="input_settings",
    input_file="capture_settings_z{}.yml".format(cam_num),
)

pc, _ = camera_capture_and_save(
    camera, settings, folder="saved_pc", output_file="_delete" + ".zdf", downsample_factor=2,
)

_ = convert2png(
    pointcloud=pc,
    folder="saved_output",
    output_file="_delete_rgb.png",
)