import cv2

# 图片保存路径
IMG_SAVE_PATH = "./img/"


if __name__ == '__main__':
    num = 1
    camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    # camera = cv2.VideoCapture(1)
    # camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    camera.set(3,1920)
    camera.set(4,1080)
    cv2.namedWindow("src", 0)
    cv2.resizeWindow("src", 960, 540)
    while True:
        state, src = camera.read()
        cv2.imshow('src', src)

        if cv2.waitKey(10) & 0xff == ord(' '):
            cv2.imwrite(IMG_SAVE_PATH + str(num) + '.jpg', src)
            print("Saved img_" + IMG_SAVE_PATH + str(num) + "!")
            num += 1
        if cv2.waitKey(10) & 0xff == ord('q'):
            break
    cv2.destroyAllWindows()
