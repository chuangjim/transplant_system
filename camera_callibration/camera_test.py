# -*- coding: utf-8 -*-
import cv2

# ip camera 的擷取路徑

# 建立 VideoCapture 物件
ipcam = cv2.VideoCapture(1)
# ipcam.set(3,1920)
# ipcam.set(4,1080)
# 使用無窮迴圈擷取影像，直到按下Esc鍵結束
while True:
    # 使用 read 方法取回影像
    stat, I = ipcam.read()

    # 加上一些影像處理...

    # imshow 和 waitkey 需搭配使用才能展示影像
    cv2.imshow('Image', I)
    if cv2.waitKey(1) == 27:
        ipcam.release()
        cv2.destroyAllWindows()
        break