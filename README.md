# zerowaste

## Zivid Code

Working for SDK V2.2.0

Zivid provides example code from the following repos:
(in samples folder)
(in source folder)

| Repo      | Folder |
| ----------- | ----------- |
| https://github.com/zivid/zivid-python      | Samples       |
| https://github.com/zivid/zivid-python-samples   | Source        |

Note that at the time of writing (Feb, 2021), the code in zivid-python-samples repo is just a more comprehensive set of code than what is provided in the samples folder in zivid-python repo. So can probably ignore the samples folder provided in the zivid-python repo, but check this to make sure...

**DO NOT MAKE CHANGES TO ZIVID BASE CODE SAMPLES**

The code in this repo extends the functionality of the sample code provided by Zivid. Some functions we use will rely on their code base, which we will keep updated as new versions are released. The idea is to keep their code as a "template" for our own implementation. If we need to make any changes to their provided code, make a copy, reference where it came from (so can update easier), and save our own version in this repo.

**DO NOT MAKE CHANGES TO ZIVID BASE CODE SAMPLES**

To use the provided Zivid code modules as imports to new code, ensure the source code location is added to the PYTHONPATH environment variable. This will ensure that python module imports work.

Suggest the following steps:
1. Clone the https://github.com/zivid/zivid-python-samples repo
2. Add the source code folder to the PYTHONPATH
    * Read section 3.6 in the following link: https://docs.python.org/3/using/windows.html
    * in command line: echo %PYTHONPATH% (will be empty if the variable is not set)
    * to add temporarily to current shell: set PYTHONPATH=%PYTHONPATH%;C:\new\path\to\source\code
    * to add permanently: go through System Properties, Environment Variables, Edit or Add New (need to restart shell to see changes)
    * downside of permanent method is that all versions on python will refer to this folder, so make sure this won't cause any issues
3. Test that this works, should now be able to import any of the modules in the source folder. Reference from source as top folder.
   * For example: from sample_utils.paths import get_sample_data_path
   * for example: import applications.basic.file_formats.convert_zdf

## Description of Code (John)

### Zivid Classes

https://github.com/zivid/zivid-python/tree/master/modules/zivid

| Class/Name | Description | Members | Summary | Use in Code
| ----------- | ----------- | ----------- | ----------- | ----------- |
| Application |  class can be used as a context manager to guarantee that resources are released deterministically | create_file_camera, connect_camera, cameras, release | | |
| Calibration | | | | |
| Camera | interface to one Zivid camera, but only to access | capture, info, state, connect, disconnect, write_user_data, user_data, release | | |
| Camera_Info | firmware_version, model_name, serial_number, revision, user_data, firmware_version, | | | |
| :Revision | | major, minor | | |
| :UserData | | | | |
| Camera_State | extract information from internal function of Zivid camera, such as temperature or lens info | available, connected | | |
| :Temperature | | dmd, general, led, lens, pcb | | |
| Capture_Assistant | | ambient_light_frequency, max_capture_time, _convert_to_internal, suggest_settings | | |
| Frame | contains the point cloud, stored on compute device memory | point_cloud, save, load, release | | |
| Frame_2D | contains a 2D image as well as metadata | image_rgba, settings, state, info, release | | |
| Frame_Info | | core, time_stamp, software_version | | |
| Image | A two-dimensional image stored on the host | height, width, save, copy_data, release | | |
| PointCloud | Point cloud with x, y, z, RGB and color laid out on a 2D grid | height, width, release | | |
| SDK_Version | get the version of the loaded library | | | |
| Settings | | Acquisition, Processing, Color, Balance, Color, Filters, Noise, Smoothing, Gaussian, Experimental, ContrastDistortion, Correction, Removal, Reflection, Settings, Outlier, Brightness, Aperture, ExposureTime, Gain, ContrastDistortion, Enabled, Strength, Threshold, | | |
| :Acquisition | | | | |
| Settings2D | | Acquisition, Processing, Color, Balance | | |

### Zivid Modules

| Class/Name | Description | Members | Summary | Source Code
| ----------- | ----------- | ----------- | ----------- | ----------- |
| _init_.py | imports all non protected classes, modules and packages from the current level | | | https://github.com/zivid/zivid-python/blob/master/modules/zivid/__init__.py |
| _setting2_d_converter.py | implementation of 2D evaluation process | | | https://github.com/zivid/zivid-python/blob/master/modules/zivid/_settings2_d_converter.py |
| application.py | class can be used as a context manager | | | https://github.com/zivid/zivid-python/blob/master/modules/zivid/application.py |
| calibration.py | module for calibration features | | | https://github.com/zivid/zivid-python/blob/master/modules/zivid/calibration.py |
| camera.py | contains camera class | | | https://github.com/zivid/zivid-python/blob/master/modules/zivid/camera.py |
| capture_assistant.py | class representing parameters to capture assistant | | | https://github.com/zivid/zivid-python/blob/master/modules/zivid/capture_assistant.py |
| frame.py | contains the frame class | | | https://github.com/zivid/zivid-python/blob/master/modules/zivid/frame.py |
| frame_2d.py | contains a 2D image as well as metadata at the time of capture | | | https://github.com/zivid/zivid-python/blob/master/modules/zivid/frame_2d.py |
| image.py | contains the image class | | | https://github.com/zivid/zivid-python/blob/master/modules/zivid/image.py |

### Calibration Modules

| Class/Name | Description | Members | Summary | Source Code
| ----------- | ----------- | ----------- | ----------- | ----------- |
| hand_eye.py |implementation of hand-eye calibration functionality | | |  https://github.com/zivid/zivid-python/blob/master/modules/zivid/_calibration/hand_eye.py|
| detector.py | implementation of feature point detection functionality | | | https://github.com/zivid/zivid-python/blob/master/modules/zivid/_calibration/detector.py |
