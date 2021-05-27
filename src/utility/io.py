"""
Utilities for working with Zivid Camera
"""

import os
from pathlib import Path


def get_sample_data_path_edvard():
    """Get sample data path.

    Returns:
        path: Sample data path

    """

    path = Path(__file__).parents[1] / "ZividSampleData2"
    return path

def get_output_data_path_edvard():
    """Get output data path.

    Returns:
        path: Output data path

    """

    path = Path(__file__).parents[1] / "output"
    return path

def create_file_path(folder,filename):
    """create output data path.

    Returns:
        path: Output data path

    """

    path = Path(__file__).parents[2] / folder / filename

    return os.path.abspath(path)