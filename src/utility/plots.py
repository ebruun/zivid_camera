from matplotlib import pyplot as plt
from cv2 import cv2
import copy


def plot_flex(imgs, dims):

    fig, axs = plt.subplots(dims[0],dims[1], figsize=(18, 8), facecolor='w', edgecolor='k')

    for item in imgs.items():
        i = item[1]

        axs[i["pos"]].imshow(i['img_file'],cmap="gray")
        axs[i["pos"]].set_title(i['name'])

def plot_summary(img, contours, contours_save, midpoint_save, corners, found_shapes, edges):
    img_copy = copy.deepcopy(img)
    fig = plt.figure(figsize=(12, 6))

    cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 10)
    cv2.drawContours(img, contours_save, -1, (0, 255, 0), 10)

    for corner in corners:
        x,y = corner.ravel()
        cv2.circle(img,(int(x),int(y)),10,(0,0,255),-1)

    for midpoint in midpoint_save:
        x,y = midpoint.ravel()
        cv2.circle(img,(int(x),int(y)),20,(255,0,0),-1)        

    plt.subplot(221),
    plt.imshow(img_copy,cmap = 'gray')
    plt.title('Masked RGB + ALL contours'), plt.xticks([]), plt.yticks([])\

    plt.subplot(222),
    plt.imshow(img,cmap = 'gray')
    plt.title('Masked RGB + selected contours/corners'), plt.xticks([]), plt.yticks([])

    plt.subplot(223),
    plt.imshow(found_shapes, cmap = 'gray')
    plt.title('Found Box'), plt.xticks([]), plt.yticks([])

    plt.subplot(224),
    plt.imshow(edges,cmap = 'gray')
    plt.title('Edges of rectangles'), plt.xticks([]), plt.yticks([])


def plot_features(img_png, img_depth, points, midpoints):
    fig = plt.figure(figsize=(12, 6))

    plt.subplot(121),
    plt.imshow(img_png,cmap = 'gray')
    plt.title('Original Image'),
    plt.xticks([]), plt.yticks([])

    # Add a white/black square on the depth map to show where the feature point is
    for point in points:
        x,y = point.ravel()

        x = int(x)
        y = int(y)

        img_depth[(y-5):(y+5),(x-5):(x+5)] = [255,255,255]
        img_depth[(y-2):(y+2),(x-2):(x+2)] = [0,0,0]

    for point in midpoints:
        x,y = point.ravel()

        x = int(x)
        y = int(y)

        img_depth[(y-5):(y+5),(x-5):(x+5)] = [255,255,255]
        img_depth[(y-2):(y+2),(x-2):(x+2)] = [255,0,0]

    img_depth = cv2.cvtColor(img_depth, cv2.COLOR_BGR2RGB)

    plt.subplot(122),
    plt.imshow(img_depth,cmap = 'gray')
    plt.title('Depth Image'),
    plt.xticks([]), plt.yticks([])
    plt.show()


def plot_ordered_features(img_png, rectangles):

    for rectangle in rectangles:
        for i,point in enumerate(rectangle):
            x,y = point.ravel()
            cv2.circle(img_png,(int(x),int(y)),10,(255,0,0),-1)
            cv2.putText(
                img = img_png,
                text = str(i),
                org = (x+10,y-10),
                fontFace= cv2.FONT_HERSHEY_COMPLEX,
                fontScale = 1.5,
                thickness = 4,
                color = (0, 0, 255),
                )

    fig = plt.figure(figsize=(12, 6))
    
    plt.subplot(111),
    plt.imshow(img_png,cmap = 'gray')
    plt.title('Original Image'),
    plt.xticks([]), plt.yticks([])
    plt.show()