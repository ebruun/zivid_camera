# PYTHON IMPORTS
import datetime
import zivid
import zivid.capture_assistant as capture_assistant
from zivid.capture_assistant import SuggestSettingsParameters as sgst_params


# LOCAL IMPORTS
from src_cam.utility.io import _create_file_path


def _list_connected_cameras():
    print("What cameras are connected?")
    app = zivid.Application()

    cameras = app.cameras()
    for camera in cameras:
        print(f"Camera Info:  {camera}")


def camera_connect(rob_num):
    """connect to camera, assume rob1 = zivid1, rob2 = zivid2"""

    camera_ids = {
        1: "19010186",  # zivid 1
        2: "2147EFB1",  # zivid 2
    }

    print("\nCONNECTING TO CAMERA:", camera_ids[rob_num])
    app = zivid.Application()

    try:
        camera = app.connect_camera(camera_ids[rob_num])
        print("--Connection success")
    except RuntimeError:
        virtual_camera_filepath = _create_file_path("ZividSampleData2", "FileCameraZividOne.zfc")
        camera = app.create_file_camera(virtual_camera_filepath)
        print(f"--Connection failure, using virtual camera: {virtual_camera_filepath}")

    return camera


def camera_capture_settings(camera, setting_file=False):
    if camera.info.serial_number == "F1" or not setting_file:  # virtual cam
        suggest_settings_parameters = sgst_params(
            max_capture_time=datetime.timedelta(milliseconds=1200),
            ambient_light_frequency=sgst_params.AmbientLightFrequency.none,
        )
        settings = capture_assistant.suggest_settings(camera, suggest_settings_parameters)
        print("--Using capture assistant")

    else:  # real camera w/ setting file
        settings_file_path = _create_file_path("input", setting_file)
        settings = zivid.Settings.load(settings_file_path)
        print(f"--Using specified settings file: {settings_file_path}")

    for i, acquisition in enumerate(settings.acquisitions):
        print(f"--aquisition #{i+1}: {acquisition}")

    return settings


def camera_capture_and_save(camera, settings, folder, filename):
    with camera.capture(settings) as frame:
        file_out = _create_file_path(folder, filename)
        frame.save(file_out)
        print(f"--Saving frame to file: {file_out}")


if __name__ == "__main__":
    _list_connected_cameras()

    rob_num = 1

    camera = camera_connect(rob_num)
    settings = camera_capture_settings(camera, "capture_settings_z{}.yml".format(rob_num))
    camera_capture_and_save(camera, settings, "input", "_delete.zdf")
