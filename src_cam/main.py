# LOCAL IMPORTS
import imp
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
def main(camera_id=False):

    if camera_id:
        filename = create_dynamic_filename(n=00)

        camera = camera_connect(camera_id)
        # settings = camera_capture_settings(camera, "capture_settings_z1.yml")
        settings = camera_capture_settings(camera)
        camera_capture_and_save(
            camera,
            settings,
            "input",
            filename + ".zdf",
        )
    else:
        saved_files = [
            "save_single01",
            "save_single02",
            "save_triple01",
        ]

        filename = saved_files[0]

    pc = load_pointcloud(folder="input", input_file=filename + ".zdf")

    #########################################
    # 2. CONVERT AND FIND CORNERS/MIDPOINTS
    #########################################
    img_png = convert2png(
        pointcloud=pc,
        folder="output",
        output_file=filename + "_rgb.png",
    )

    corners, midpoints = find_features(
        pointcloud=pc,
        folder="output",
        input_file_image=filename + "_rgb.png",
        plot=True,
    )

    img_depth = convert2depth(
        pointcloud=pc,
        folder="output",
        output_file=filename + "_depth.png",
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
    save_frames_as_matrix_yaml("zerowaste_robot/transformations", "H1_cam_obj2.yaml", frames)

    plot_frames(img_png, frames, "intrinsics_zivid1.yml")
    plot_ordered_features(img_png, rectangles)


if __name__ == "__main__":
    camera_ids = {
        "zivid_one": "19010186",
        "zivid_two": "2147EFB1",
    }

    # main()  # If you want to run from saved data
    main(camera_ids["zivid_one"])  # If you want to capture live data
