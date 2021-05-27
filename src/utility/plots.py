from matplotlib import pyplot as plt
from cv2 import cv2
import copy


def plot_flex(imgs, dims):

    fig, axs = plt.subplots(dims[0],dims[1], figsize=(18, 8), facecolor='w', edgecolor='k')

    #gs = fig.add_gridspec(3,4)

    for item in imgs.items():
        i = item[1]

        axs[i["pos"]].imshow(i['img_file'],cmap="gray")
        axs[i["pos"]].set_title(i['name'])

def plot_summary(img, contours, contours_save, corners, found_shapes, edges):
    img_copy = copy.deepcopy(img)
    fig = plt.figure(figsize=(12, 6))

    cv2.drawContours(img_copy, contours, -1, (0, 255, 0), 10)
    cv2.drawContours(img, contours_save, -1, (0, 255, 0), 10)

    for corner in corners:
        x,y = corner.ravel()
        cv2.circle(img,(int(x),int(y)),10,(0,0,255),-1)

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



    plt.show()
    plt.pause(1)