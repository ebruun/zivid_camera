"""
Utilities for working with Zivid Camera
"""

import os
from datetime import datetime



def create_file_path(folder,filename):
    """create output data path.

    Returns:
        path: Output data path

    """
    path = os.path.join(os.getcwd(),folder, filename)
    print("created path...",path)
    return path

def file_name(file_name,type):
    return file_name + type

def dynamic_name(n = 00, type = "online"):
    str2 = datetime.now().strftime("%m_%d_n")
    return str2 + str(n) + "_" + type
