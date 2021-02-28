"""
This example is based on "capture_from_file.py" code provided in zivid-python-samples repo


"""

#Add a comment to this file

# PYTHON IMPORTS
from pathlib import Path
import datetime
import zivid

#ZIVID IMPORTS
import applications.basic.file_formats.convert_zdf as convert

# LOCAL IMPORTS
from utils import get_sample_data_path_edvard as get_sample_data_path
from utils import get_output_data_path_edvard as get_output_data_path

def _main():
    app = zivid.Application()

    # The file_camera file is in Zivid Sample Data. See instructions in README.md
    file_camera = Path() / get_sample_data_path() / "FileCameraZividOne.zfc"

    print(f"Creating virtual camera using file: {file_camera}")
    camera = app.create_file_camera(file_camera)

    print("Configuring settings")
    settings = zivid.Settings()
    settings.acquisitions.append(zivid.Settings.Acquisition())
    settings.processing.filters.smoothing.gaussian.enabled = True
    settings.processing.filters.smoothing.gaussian.sigma = 1.5
    settings.processing.filters.reflection.removal.enabled = True
    settings.processing.color.balance.red = 1.0
    settings.processing.color.balance.green = 1.0
    settings.processing.color.balance.blue = 1.0

    print("Capturing frame")
    with camera.capture(settings) as frame:
        data_file = Path() / get_output_data_path() / "emulated_output_frame.zdf"
        print(f"Saving frame to file: {data_file}")
        frame.save(data_file)


    print("Configuring 2D settings")
    settings_2d = zivid.Settings2D()
    settings_2d.acquisitions.append(zivid.Settings2D.Acquisition())
    settings_2d.acquisitions[0].exposure_time = datetime.timedelta(microseconds=30000)
    settings_2d.acquisitions[0].aperture = 11.31
    settings_2d.acquisitions[0].brightness = 1.00
    settings_2d.acquisitions[0].gain = 2.0
    settings_2d.processing.color.balance.red = 1.0
    settings_2d.processing.color.balance.green = 1.0
    settings_2d.processing.color.balance.blue = 1.0
    settings_2d.processing.color.gamma = 1.0

    print("Capturing 2D frame")
    with camera.capture(settings_2d) as frame_2d:
        image = frame_2d.image_rgba()

        data_file = Path() / get_output_data_path() / "emulated_output_frame.png"
        print(f"Saving frame to file: {data_file}")
        image.save(data_file)        
        

    
if __name__ == "__main__":
    _main()

#Johns first comment in code

