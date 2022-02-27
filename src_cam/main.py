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
from src_cam.utility.plots import (
    plot_thresholding,
    plot_feature_contours,
    plot_feature_points,
    plot_frames_undistort,
    plot_frames,
)


################################
# 1. CAPTURE IMAGE
################################
def main(rob_num=False, filename=False, plot=False):

    if rob_num:
        filename = create_dynamic_filename(rob_num, n=00)

        camera = camera_connect(rob_num)
        settings = camera_capture_settings(
            camera,
            folder="input_settings",
            input_file="capture_settings_z{}.yml".format(rob_num),
        )
        # settings = camera_capture_settings(camera) # For auto-capture

        camera_capture_and_save(camera, settings, folder="saved_pc", output_file=filename + ".zdf")

        pc = load_pointcloud(folder="saved_pc", input_file=filename + ".zdf")

    else:
        rob_num = int(filename.split("_")[0][1])

        pc = load_pointcloud(
            folder="saved_pc",
            input_file=filename + ".zdf",
        )

    #########################################
    # 2. CONVERT AND FIND CORNERS/MIDPOINTS
    #########################################
    img_png = convert2png(
        pointcloud=pc,
        folder="saved_output",
        output_file=filename + "_rgb.png",
    )

    corners, midpoints, plot_data = find_features(
        pointcloud=pc,
        folder="saved_output",
        input_file_image=filename + "_rgb.png",
        plot=True,
    )

    try:
        img_depth = convert2depth(
            pointcloud=pc,
            folder="saved_output",
            output_file=filename + "_depth.png",
            points=midpoints,
        )

        rectangles = calc_rectangles(corners, midpoints)

        ##########################################
        # 3. CALCULATE MEMBER FRAMES
        ##########################################
        frames = calc_frames(pointcloud=pc, features=[rectangles, midpoints])

        # Saves as a transformation matrix, in robot control module
        # Represents the pose of the member
        save_frames_as_matrix_yaml(
            frames,
            folder="zerowaste_robot/transformations",
            output_file="H1_cam_obj_R{}.yaml".format(rob_num),
        )
    except ValueError:
        pass

    ##########################################
    # 4. PLOT
    ##########################################
    if plot:
        plot_thresholding(plot_data)
        plot_feature_contours(plot_data[-1])
        plot_feature_points(img_png, img_depth, corners, midpoints)

        plot_frames_undistort(
            img_png,
            frames,
            folder="input_settings",
            input_file="intrinsics_z{}.yml".format(rob_num),
        )

        plot_frames(img_png, rectangles)  # has to come after


if __name__ == "__main__":

    # # If you want to run from saved data
    # saved_file_names = {
    #     0: "R1_save_single01",
    #     1: "R1_save_single02",
    #     2: "R1_save_triple01",
    #     3: "R2_save_single01",
    # }

    # main(filename=saved_file_names[0], plot=True)

    main(rob_num=2, plot=True)  # If you want to capture live data
