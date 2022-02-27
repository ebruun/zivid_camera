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

    # recall that in cv img the 0 is top left corner

    # Reorder the rectangles in this order
    # 3------2
    # |      |
    # |      |
    # |      |
    # 1------0

    # Find index of bottom right corner, make it first row
    for i, rectangle in enumerate(rectangles):
        midpoint = midpoints[i]

        idx_close = np.argmin(np.sum((rectangle[0] - rectangle[1:4]) ** 2, axis=1)) + 1

        idx_side1 = np.array([0, idx_close])
        idx_side2 = np.delete(np.array([0, 1, 2, 3], dtype=np.int64), [0, idx_close])

        center_vector = np.mean(rectangle[idx_side1], axis=0) - np.mean(
            rectangle[idx_side2], axis=0
        )

        if center_vector[1] >= 0:  # side 1 is bottom
            idx = idx_side1[np.argmax(rectangle[idx_side1, 0], axis=0)]
        else:  # side 2 is bottom
            idx = idx_side2[np.argmax(rectangle[idx_side2, 0], axis=0)]

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
            [10, 10],
            [8, 0],
            [11, 0],
            [7, 10],
            [17, 10],
            [20, 10],
            [18, 0],
            [21, 0],
            [31, 0],
            [30, 10],
            [27, 10],
            [28, 0],
            [38, 0],
            [41, 0],
            [37, 10],
            [40, 10],
        ]
    ).astype("int32")

    midpoints = np.array(
        [
            [9, 5],
            [19, 5],
            [29, 5],
            [39, 5],
        ]
    ).astype("int32")

    print(calc_rectangles(corners, midpoints))
