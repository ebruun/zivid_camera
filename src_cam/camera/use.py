# PYTHON IMPORTS
import datetime
from time import process_time

# ZIVID IMPORTS
import zivid
import zivid.capture_assistant as capture_assistant
from zivid.capture_assistant import SuggestSettingsParameters as sgst_params
from sample_utils.display import display_pointcloud

# LOCAL IMPORTS
from src_cam.utility.io import _create_file_path
from src_cam.utility.io import load_pointcloud
from src_cam.camera.convert import convert2png


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
        virtual_camera_filepath = _create_file_path("ZividSampleData", "FileCameraZividOne.zfc")
        camera = app.create_file_camera(virtual_camera_filepath)
        print(f"--Connection failure, using virtual camera: {virtual_camera_filepath}")

    return camera


def camera_capture_settings(camera, folder=False, input_file=False):
    if camera.info.serial_number == "F1" or not input_file:  # virtual cam
        suggest_settings_parameters = sgst_params(
            max_capture_time=datetime.timedelta(milliseconds=1200),
            ambient_light_frequency=sgst_params.AmbientLightFrequency.none,
        )
        settings = capture_assistant.suggest_settings(camera, suggest_settings_parameters)
        print("--Using capture assistant")

    else:  # real camera w/ setting file
        settings_file_path = _create_file_path(folder, input_file)
        settings = zivid.Settings.load(settings_file_path)
        print(f"--Using specified settings file: {settings_file_path}")

    # print aquisition settings
    for i, acquisition in enumerate(settings.acquisitions):
        # print(f"--aquisition #{i+1}: {acquisition}")
        pass

    return settings


def pc_downsample(pc, downsample_factor=1, display=True):
    """
    downsample the pointcloud using Zivid API (happens on GPU, fast)
    """
    if display:
        xyz = pc.copy_data("xyz")
        rgba = pc.copy_data("rgba")

        print(f"Before downsampling: {pc.width * pc.height} point cloud")
        display_pointcloud(xyz, rgba[:, :, 0:3])

    if downsample_factor == 1:
        print("no downsampling")
    elif downsample_factor == 2:
        print("2x2 downsample")
        pc.downsample(zivid.PointCloud.Downsampling.by2x2)
    elif downsample_factor == 3:
        print("3x3 downsample")
        pc.downsample(zivid.PointCloud.Downsampling.by3x3)
    elif downsample_factor == 4:
        print("4x4 downsample")
        pc.downsample(zivid.PointCloud.Downsampling.by4x4)

    if display:
        xyz_donwsampled = pc.copy_data("xyz")
        rgba_downsampled = pc.copy_data("rgba")

        print(f"After downsampling: {pc.width * pc.height} point cloud")
        display_pointcloud(xyz_donwsampled, rgba_downsampled[:, :, 0:3])


def camera_capture_and_save(camera, settings, folder, output_file, downsample_factor=1):
    with camera.capture(settings) as frame:
        pc_downsample(frame.point_cloud(), downsample_factor)

        pointcloud_file_path = _create_file_path(folder, output_file)

        print(f"--Saving frame to file: {pointcloud_file_path}")
        frame.save(pointcloud_file_path)

        return frame.point_cloud(), frame


if __name__ == "__main__":
    _list_connected_cameras()

    rob_num = 2

    camera = camera_connect(rob_num)
    settings = camera_capture_settings(
        camera,
        folder="input_settings",
        input_file="capture_settings_z{}.yml".format(rob_num),
    )

    t1_start = process_time()
    pc, _ = camera_capture_and_save(
        camera, settings, folder="saved_pc", output_file="_delete" + ".zdf", downsample_factor=2
    )

    _ = convert2png(
        pointcloud=pc,
        folder="saved_output",
        output_file="_delete_rgb.png",
    )

    t1_stop = process_time()
    print("Elapsed time:", t1_stop - t1_start)
