# LOCAL IMPORTS
from src.camera.use import capture_image
from src.camera.convert import convert2depth, convert2png, load_pointcloud

from src.processing.detect import find_features
from src.processing.calc_rectangles import calc_rectangles
from src.processing.calc_frames import calc_frames

from src.utility.io import file_name, dynamic_name
from src.utility.plots import plot_features, plot_ordered_features, plot_frames

from calibration_planes import make_yaml_frame


################################
# 1. CAPTURE IMAGE
################################

def main(online=False):

    if online:  # capture with camera
        name = dynamic_name(n=00, type="online")
        capture_image(
            folder="input",
            output_file=file_name(name, ".zdf"),
            # setting_file="capture_settings_calibration.yml",
        )
    else:  # read in saved pointcloud
        # name = "04_20_n00_online" #Multiple detected
        name = "06_23_n0_online"

    pc = load_pointcloud(
        folder="input",
        input_file=file_name(name, ".zdf")
    )

    #########################################
    # 2. CONVERT AND FIND CORNERS/MIDPOINTS
    #########################################
    img_png = convert2png(
        pointcloud=pc,
        folder="output",
        output_file=file_name(name, "_rgb.png"),
        )

    corners, midpoints = find_features(
        pointcloud=pc,
        folder="output",
        input_file_image=file_name(name, "_rgb.png"),
        plot=True,
        )

    img_depth = convert2depth(
        pointcloud=pc,
        folder="output",
        output_file=file_name(name, "_depth.png"),
        points=midpoints,
        )

    plot = True  # Turn on all the random plots
    if plot:
        plot_features(img_png, img_depth, corners, midpoints)

    rectangles = calc_rectangles(corners, midpoints)

    ##########################################
    # 3. CALCULATE MEMBER FRAMES
    ##########################################
    frames = calc_frames(pointcloud=pc, features=[rectangles, midpoints])

    # Saves as a transformation matrix, to use in robot control module
    # Represents the pose of the member
    make_yaml_frame("transformations", "H1_cam_obj.yaml", frames)

    plot_frames(img_png, frames)
    plot_ordered_features(img_png, rectangles)


if __name__ == "__main__":
    # main(online=False)  # If you want to run from saved data
    main(online=True)  # If you want to capture live data
