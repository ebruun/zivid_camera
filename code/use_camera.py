"""Capture sample."""
# PYTHON IMPORTS
import datetime
import zivid
from pathlib import Path

# ZIVID IMPORTS
from sample_utils.settings_from_file import get_settings_from_yaml

# LOCAL IMPORTS
from utils import create_file_path as create_file_path


def _main(output_file, setting_file = False):
    app = zivid.Application()
    camera = app.connect_camera()

    if setting_file:
        settings_file_path = Path() / create_file_path("input",setting_file)

        print(f"Configuring settings from file: {settings_file_path}")
        settings = get_settings_from_yaml(settings_file_path)
    else:
        suggest_settings_parameters = zivid.capture_assistant.SuggestSettingsParameters(
            max_capture_time=datetime.timedelta(milliseconds=1200),
            ambient_light_frequency=zivid.capture_assistant.SuggestSettingsParameters.AmbientLightFrequency.none,
        )

        print(f"Running Capture Assistant with parameters: {suggest_settings_parameters}")
        settings = zivid.capture_assistant.suggest_settings(camera, suggest_settings_parameters)

    print("Capturing 3D frame")
    with camera.capture(settings) as frame:
        file_out = create_file_path("input",output_file)
        print(f"Saving frame to file: {file_out}")

        frame.save(file_out)


if __name__ == "__main__":
    #_main(output_file = "_3D_frame_fromfile.zdf", setting_file = "capture_settings.yml")
    _main(output_file = "_3D_frame_fromassistant.zdf")