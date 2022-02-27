# LOCAL IMPORTS
from src_cam.camera.use import (
    camera_connect,
    camera_capture_settings,
    camera_capture_and_save,
)
from src_cam.camera.convert import (
    convert2depth,
    convert2png,
    load_pointcloud,
)

from src_cam.processing.detect import find_features
from src_cam.processing.calc_rectangles import calc_rectangles
from src_cam.processing.calc_frames import calc_frames

from src_cam.utility.io import (
    create_dynamic_filename,
    save_frames_as_matrix_yaml,
)
from src_cam.utility.plots import plot_features, plot_ordered_features, plot_frames


################################
# 1. CAPTURE IMAGE
################################
def main(rob_num=False):

    if rob_num:
        filename = create_dynamic_filename(n=00)

        camera = camera_connect(rob_num)
        settings = camera_capture_settings(camera, "capture_settings_z{}.yml".format(rob_num))
        # settings = camera_capture_settings(camera)

        camera_capture_and_save(
            camera,
            settings,
            "input",
            filename + "_R{}".format(rob_num) + ".zdf",
        )

        pc = load_pointcloud(folder="input", input_file=filename + "_R{}".format(rob_num) + ".zdf")

    else:
        saved_files = ["save_single01_R1", "save_single02_R1", "save_triple01_R1", "02_27_n0_R2"]

        filename = saved_files[3]
        rob_num = int(filename.split("_")[-1][1])

        pc = load_pointcloud(folder="input", input_file=filename + ".zdf")

    #########################################
    # 2. CONVERT AND FIND CORNERS/MIDPOINTS
    #########################################
    img_png = convert2png(
        pointcloud=pc,
        folder="output",
        output_file=filename + "_rgb_R{}.png".format(rob_num),
    )

    corners, midpoints = find_features(
        pointcloud=pc,
        folder="output",
        input_file_image=filename + "_rgb_R{}.png".format(rob_num),
        plot=True,
    )

    img_depth = convert2depth(
        pointcloud=pc,
        folder="output",
        output_file=filename + "_depth_R{}.png".format(rob_num),
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

    # Saves as a transformation matrix, in robot control module
    # Represents the pose of the member
    save_frames_as_matrix_yaml(
        "zerowaste_robot/transformations", "H1_cam_obj_R{}.yaml".format(rob_num), frames
    )

    plot_frames(img_png, frames, "intrinsics_z{}.yml".format(rob_num))
    plot_ordered_features(img_png, rectangles)


if __name__ == "__main__":
    main()  # If you want to run from saved data
    # main(rob_num=2)  # If you want to capture live data
