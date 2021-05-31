import numpy as np
from cv2 import cv2

def _group(corners, midpoints):
    print("--grouping corners into rectangles\n")

    # find which midpoint a corner is closest to
    group = []
    for corner in corners:
        group.append(np.argmin(np.linalg.norm(corner - midpoints, axis=1)))
    
    group = np.asarray(group)

    # group into clusters of 4 (each rectangle)
    corners_grouped = [corners[np.where(x == group)] for x in range(len(midpoints))]
    
    return corners_grouped


def calc_rectangles(corners, midpoints):
    rectangles = _group(corners, midpoints)

    print("--reordering rectangles\n")
    
    #Reorder the rectangles in this order (relative)
    #3------2      0------1
    #|      |      |      |
    #|      |      |      |
    #1------0      2------3
    for i,rectangle in enumerate(rectangles):
        distances = np.linalg.norm(rectangle[0] - rectangle, axis = 1)
        rectangle = np.squeeze([rectangle[x] for x in np.argsort(distances)])
        
        rectangles[i] = rectangle



    return rectangles

if __name__ == "__main__":
    corners = np.array([
        [1734.,  589.],
        [1675.,  392.],
        [1064.,  668.],
        [ 541.,  885.],
        [ 464.,  885.],
        [ 540.,  685.],
        [ 463.,  685.],
        [ 897.,  530.],
        [ 999.,  703.],
        [ 964.,  487.],
        [1670.,  588.],
        [1737.,  396.],
    ]).astype('int32')

    midpoints = np.array([
        [501, 785],
        [981, 594],
        [1704, 491],
    ]).astype('int32')
    
    calc_rectangles(corners,midpoints)