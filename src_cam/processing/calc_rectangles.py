# PYTHON IMPORTS
# from ast import parse
import numpy as np


def _group(corners, midpoints):
    print("--grouping corners into rectangles")

    # find which midpoint a corner is closest to
    group = []
    for corner in corners:
        group.append(np.argmin(np.linalg.norm(corner - midpoints, axis=1)))

    group = np.asarray(group)

    # group into clusters of 4 (each rectangle)
    corners_grouped = [corners[np.where(x == group)] for x in range(len(midpoints))]

    # return np.squeeze(corners_grouped)
    return corners_grouped


def _reorder_corners(rectangles, midpoints):
    print("--reordering corners in rectangles")

    # Reorder the rectangles in this order
    # 3------2
    # |      |
    # |      |
    # |      |
    # 1------0

    # Find index of bottom right corner, make it first row
    for i, rectangle in enumerate(rectangles):
        midpoint = midpoints[i]
        a = rectangle[:, 0] > midpoint[0]
        b = rectangle[:, 1] > midpoint[1]
        idx = np.where(a / b == 1)[0][0]

        rectangle[[0, idx]] = rectangle[[idx, 0]]

        rectangles[i] = rectangle

    # reorder as shown above
    for i, rectangle in enumerate(rectangles):
        distances = np.linalg.norm(rectangle[0] - rectangle, axis=1)
        rectangle = np.squeeze([rectangle[x] for x in np.argsort(distances)])

        rectangles[i] = rectangle

    # check that the member is vertically oriented, otherwise swap
    for i, rectangle in enumerate(rectangles):
        b = rectangle[:, 1] > midpoint[1]
        if b[0] and b[1]:  # small width is below middle point (it is vertical)
            pass
        else:
            rectangle[[0, 1]] = rectangle[[1, 0]]
            rectangle[[2, 3]] = rectangle[[3, 2]]

    return rectangles


def calc_rectangles(corners, midpoints):
    print("\nCALCULATING RECTANGLES")
    rectangles = _group(corners, midpoints)
    rectangles = _reorder_corners(rectangles, midpoints)

    return rectangles


if __name__ == "__main__":
    corners = np.array(
        [
            [1734.0, 589.0],
            [1675.0, 392.0],
            [1064.0, 668.0],
            [541.0, 885.0],
            [464.0, 885.0],
            [540.0, 685.0],
            [463.0, 685.0],
            [897.0, 530.0],
            [999.0, 703.0],
            [964.0, 487.0],
            [1670.0, 588.0],
            [1737.0, 396.0],
        ]
    ).astype("int32")

    midpoints = np.array(
        [
            [501, 785],
            [981, 594],
            [1704, 491],
        ]
    ).astype("int32")

    calc_rectangles(corners, midpoints)
