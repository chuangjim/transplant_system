# -*- coding: utf-8 -*-
import cv2


# build VideoCapture object
ipcam = cv2.VideoCapture(1)
# ipcam.set(3,1920)
# ipcam.set(4,1080)

# read camera until 'q' pressed
while True:
    # read camera
    stat, I = ipcam.read()

    # use imshow and waitkey to display image
    cv2.imshow('Image', I)
    if cv2.waitKey(1) == 27:
        ipcam.release()
        cv2.destroyAllWindows()
        break