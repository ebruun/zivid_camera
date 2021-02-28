"""Capture sample."""
# PYTHON IMPORTS
from pathlib import Path
import datetime
import zivid

# LOCAL IMPORTS
from utils import get_sample_data_path_edvard as get_sample_data_path
from utils import get_output_data_path_edvard as get_output_data_path

from zivid import capture_assistant





def _main():
    app = zivid.Application()
    camera = app.connect_camera()

    settings = zivid.Settings()
    settings.acquisitions.append(zivid.Settings.Acquisition())
    settings.acquisitions[0].aperture = 4
    settings.acquisitions[0].exposure_time = datetime.timedelta(microseconds=8333)
    settings.processing.filters.outlier.removal.enabled = True
    settings.processing.filters.outlier.removal.threshold = 5.0

    print("Capturing frame")
    with camera.capture(settings) as frame:
        data_file = Path() / get_output_data_path() / "output_frame.zdf"
        print(f"Saving frame to file: {data_file}")
        frame.save(data_file)

    print("Configuring 2D settings")
    settings_2d = zivid.Settings2D()
    settings_2d.acquisitions.append(zivid.Settings2D.Acquisition())
    settings_2d.acquisitions[0].exposure_time = datetime.timedelta(microseconds=30000)
    settings_2d.acquisitions[0].aperture = 11.31
    settings_2d.acquisitions[0].brightness = 1.80
    settings_2d.acquisitions[0].gain = 2.0
    settings_2d.processing.color.balance.red = 1.0
    settings_2d.processing.color.balance.green = 1.0
    settings_2d.processing.color.balance.blue = 1.0
    settings_2d.processing.color.gamma = 1.0

    print("Capturing 2D frame")
    with camera.capture(settings_2d) as frame_2d:
        image = frame_2d.image_rgba()

        data_file = Path() / get_output_data_path() / "output_frame.png"
        print(f"Saving frame to file: {data_file}")
        image.save(data_file)    

if __name__ == "__main__":
    _main()