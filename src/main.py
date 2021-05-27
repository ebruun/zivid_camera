import numpy as np

from src.camera.use import capture_image
from src.camera.convert import convert2depth, convert2png

from src.processing.detect import find_features


name_image = "may26_image.png"
name_depth = "may26_depth.png"
name_zdf = "_3D_frame_fromassistant.zdf"

#capture_image(output_file = "test_output.zdf")

convert2png(
  input_file = name_zdf,
  output_file = name_image,
  )

convert2depth(
  input_file = name_zdf,
  output_file = name_depth,
  #feature_points = features,
  )

features = find_features(
  input_file_zdf = name_zdf, 
  input_file_image = name_image,
  plot = False,
  )

