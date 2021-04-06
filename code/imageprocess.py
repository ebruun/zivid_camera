import numpy as np
from cv2 import cv2
from matplotlib import pyplot as plt

# PYTHON IMPORTS
from pathlib import Path

# LOCAL IMPORTS
from utils import get_output_data_path_edvard as get_output_data_path


#img_path = Path() / get_output_data_path() / "emulated_output_frame.png"
img_path = Path() / get_output_data_path() / "lab_test_april6.png"

print(img_path)

img = cv2.imread(str(img_path),0)
edges = cv2.Canny(img,100,200)

plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

plt.show()

