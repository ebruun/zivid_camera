# zerowaste

## Making clean environment.yml file

export only explictly downloaded packages:

`conda env export --from-history --name  ziv281_cfab270 > environment.yml`

create new from environment.yml file:
`conda env create`

doesn't work on mac, currently if any other packages are installed with open3d we get a seg fault

check to see if this works for windows...

## Linting and Pre-commit

make sure .pre-commit-config.yaml file is up to date

language_version: python (use system version of python)

run this: `pre-commit install`

in .vscode/settings.json make sure formatonsave = TRUE

## Zivid Code

zivid-python-samples version:
* working with old branch 7090186 (which is from around December 2022)
* [link to github](https://github.com/zivid/zivid-python-samples/commit/3a045d9691a35066d5e1461dda0ea40c0fe29fcd#diff-d9aab9bce282566685b4294adf74066e8b2e36e5d660d3379b0cd6646f180468)
* Major changes to sample_utils after, deleted TransformationMatrix object
  * [old transformation_matrix.py](https://github.com/zivid/zivid-python-samples/blob/70901876a8de73e9950dce1ee08dda232077b33e/source/sample_utils/transformation_matrix.py)
* Probably an easy fix using zivid.Matrix4x4 object in save_load_matrix, but that changed too...
  * [old save_load_matrix.py](https://github.com/zivid/zivid-python-samples/blob/70901876a8de73e9950dce1ee08dda232077b33e/source/sample_utils/save_load_matrix.py)
* annoying since new save_load_matrix.py needs a running instance of Zivid :: Application
* don't have time to fix it, so keep old code for now...

version: *Working for SDK V2.6.1, as of April, 2022*

About version 2.7 (need to update still): <https://blog.zivid.com/sdk-2.7-preserve-the-details-in-your-point-clouds?utm_campaign=software&utm_medium=email&_hsmi=217086722&_hsenc=p2ANqtz-_ICS7K6EMNJlBN-M5Ul41QWuTe80zmZiisC4dljNtvQbqMnPRfgvocFtiyan01y9MzoD19lY1DPjNzsUy1KsLA2aOfig&utm_content=217087514&utm_source=hs_email>

note: when upgrading to SDK V2.7 need to update the capture settings .yml  from `Settings::Processing::Color::Experimental::ToneMapping::Enabled` to `Settings::Processing::Color::Experimental::Mode` as per <https://support.zivid.com/latest/reference-articles/settings/processing-settings/tone-mapping.html?hsLang=en>

note: when upgrading 50 SKD V2.8.1, the zivid2 no longer works through USB. Works fine through ethernet, but then have to change the network settings from the robot control setup. Works if just using the camera, but how will it work with robot control?

Zivid provides example code from the following repos:

| Repo      | Folder |
| ----------- | ----------- |
| <https://github.com/zivid/zivid-python>      | Samples       |
| <https://github.com/zivid/zivid-python-samples>   | Source        |

Note that at the time of writing, the code in zivid-python-samples repo is just a more comprehensive set of code than what is provided in the samples folder in zivid-python repo. So can probably ignore the samples folder provided in the zivid-python repo, but check this to make sure...

WARNING: **DO NOT MAKE CHANGES TO ZIVID BASE CODE SAMPLES**

The code in this repo extends the functionality of the sample code provided by Zivid. Some functions we use will rely on their code base, which we will keep updated as new versions are released. The idea is to keep their code as a "template" for our own implementation. If we need to make any changes to their provided code, make a copy, reference where it came from (so can update easier), and save our own version in this repo.

WARNING: **DO NOT MAKE CHANGES TO ZIVID BASE CODE SAMPLES**

To use the provided Zivid code modules as imports to new code, ensure the source code location is added to the PYTHONPATH environment variable. This will ensure that python module imports work.

Suggest the following steps:

1. Clone the <https://github.com/zivid/zivid-python-samples> repo
2. Add the source code folder to the PYTHONPATH
    * Read section 3.6 in the following link: <https://docs.python.org/3/using/windows.html>
    * in command line: echo %PYTHONPATH% (will be empty if the variable is not set)
    * to add temporarily to current shell: set PYTHONPATH=%PYTHONPATH%;C:\new\path\to\source\code
    * to add permanently: go through System Properties, Environment Variables, Edit or Add New (need to restart shell to see changes)
    * downside of permanent method is that all versions on python will refer to this folder, so make sure this won't cause any issues
3. Test that this works, should now be able to import any of the modules in the source folder. Reference from source as top folder.
   * For example: from sample_utils.paths import get_sample_data_path
   * for example: import applications.basic.file_formats.convert_zdf

## Description of Code (John, LOL)

### Zivid Classes

<https://github.com/zivid/zivid-python/tree/master/modules/zivid>

| Class/Name | Description | Members | Summary | Use in Code
| ----------- | ----------- | ----------- | ----------- | ----------- |
| Application |  manager class for Zivid | create_file_camera, connect_camera, cameras, release | | |
| Calibration | calibration features, such as HandEye and MultiCamera | HandEyeInput, HandEyeResidual, HandEyeOutput | | |
| Camera | interface to one Zivid camera, but only to access | capture, info, state, connect, disconnect, write_user_data, user_data, release | | |
| Camera_Info | contains information about camera hardware and firmware | firmware_version, model_name, serial_number, revision, user_data, firmware_version, | | |
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
| *init*.py | imports all non protected classes, modules and packages from the current level | | | <https://github.com/zivid/zivid-python/blob/master/modules/zivid/>**init**.py |
| _setting2_d_converter.py | implementation of 2D evaluation process | | | <https://github.com/zivid/zivid-python/blob/master/modules/zivid/_settings2_d_converter.py> |
| application.py | class can be used as a context manager | | | <https://github.com/zivid/zivid-python/blob/master/modules/zivid/application.py> |
| calibration.py | module for calibration features | | | <https://github.com/zivid/zivid-python/blob/master/modules/zivid/calibration.py> |
| camera.py | contains camera class | | | <https://github.com/zivid/zivid-python/blob/master/modules/zivid/camera.py> |
| capture_assistant.py | class representing parameters to capture assistant | | | <https://github.com/zivid/zivid-python/blob/master/modules/zivid/capture_assistant.py> |
| frame.py | contains the frame class | | | <https://github.com/zivid/zivid-python/blob/master/modules/zivid/frame.py> |
| frame_2d.py | contains a 2D image as well as metadata at the time of capture | | | <https://github.com/zivid/zivid-python/blob/master/modules/zivid/frame_2d.py> |
| image.py | contains the image class | | | <https://github.com/zivid/zivid-python/blob/master/modules/zivid/image.py> |

### Calibration Modules

| Class/Name | Description | Members | Summary | Source Code
| ----------- | ----------- | ----------- | ----------- | ----------- |
| hand_eye.py |implementation of hand-eye calibration functionality | | |  <https://github.com/zivid/zivid-python/blob/master/modules/zivid/_calibration/hand_eye.py>|
| detector.py | implementation of feature point detection functionality | | | <https://github.com/zivid/zivid-python/blob/master/modules/zivid/_calibration/detector.py> |
