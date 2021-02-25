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

Note that at the time of writing (Feb, 2021), the code in zivid-python-samples is just a more comprehensive set of code than what is provided in zivid-python. So can probably ignore zivid-python samples, but check this to make sure...

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
