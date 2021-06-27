# PYTHON IMPORTS
import datetime
import zivid
from pathlib import Path

# ZIVID IMPORTS
from sample_utils.settings_from_file import get_settings_from_yaml

# LOCAL IMPORTS 
from src.utility.io import create_file_path


def capture_image(folder, output_file, setting_file = False):
    print("CAPTURING IMAGE")
    app = zivid.Application()

    ##############################
    # 1. CONNECT
    ##############################
    try:
        print("TRYING TO CONNECT TO CAMERA...")
        camera = app.connect_camera()
        print(f"--Connected to real camera")
        real_camera = True
    except:
        folder_zivid_data = "ZividSampleData2"
        file_camera = "FileCameraZividOne.zfc"

        camera_file_path =  create_file_path(folder_zivid_data,file_camera)
        camera = app.create_file_camera(Path() / camera_file_path)
        print(f"--Connected to virtual camera using file: {camera_file_path}")
        real_camera = False
        

    ##############################
    # 2. CAPTURE SETTINGS
    ##############################
    if setting_file and real_camera:
        settings_file_path = create_file_path(folder,setting_file)

        settings = get_settings_from_yaml(Path() / settings_file_path)

        print(f"--Configuring settings from file: {settings_file_path}")
    else:
        suggest_settings_parameters = zivid.capture_assistant.SuggestSettingsParameters(
            max_capture_time=datetime.timedelta(milliseconds=1200),
            ambient_light_frequency=zivid.capture_assistant.SuggestSettingsParameters.AmbientLightFrequency.none,
        )
        settings = zivid.capture_assistant.suggest_settings(camera, suggest_settings_parameters)
        print(f"--Running Capture Assistant with parameters: {suggest_settings_parameters}")

    ##############################
    # 3. CAPTURE FRAME
    ##############################
    print("--Capturing 3D frame...")
    with camera.capture(settings) as frame:
        file_out = Path() / create_file_path(folder,output_file)
        frame.save(file_out)
        print(f"--Saving frame to file: {file_out}")


if __name__ == "__main__":
    #capture_image(folder = "input", output_file = "_test_output.zdf")
    capture_image(folder = "input", output_file = "_test_output.zdf", setting_file = "capture_settings.yml")