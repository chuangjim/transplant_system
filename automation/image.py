import cv2
import numpy as np
# from  matplotlib import pyplot as plt
import os

class ImageProcessing:
    def __init__(self, image_path):
        self.image_path = image_path
        self.cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cam.set(3,1920)
        self.cam.set(4,1080)
        self.img_count = 0
        ret, self.img = self.cam.read()
        self.h, self.w = self.img.shape[:2]
        self.img_center = (int(self.h/2), int(self.w/2))

        self.test()

    def test(self):
        cv2.namedWindow("egg", 0)
        cv2.resizeWindow("egg", 960, 540)
        ret, self.img = self.cam.read()
        if not ret:
            print("failed to grab frame")    
        else: self.show(self.img)

    def show(self, img):
        cv2.namedWindow("egg", 0)
        cv2.resizeWindow("egg", 960, 540)
        self.img = img         
        while True:
            cv2.imshow("egg",self.img)
            if cv2.waitKey(10) & 0xff == ord('q'):
                break
        cv2.destroyAllWindows()
        
    def take_photo(self):
        ret, self.img = self.cam.read()
        # cv2.namedWindow("egg", 0)
        # cv2.resizeWindow("egg", 960, 540)        
        # self.show(self.img)
        # cv2.destroyAllWindows()
        self.save_img(self.img)
        return self.img

    def save_img(self,img):
        if not os.path.exists(self.image_path):
            os.mkdir(self.image_path)
        path = f"{self.image_path}/{self.img_count}.jpg"
        cv2.imwrite(path, img)
        print(f"save images at: {path}")
        self.img_count += 1
        return self.img
    
    def find_center_filter_screen(self):
        ret, self.img = self.cam.read()
        img_b, img_g, img_r= cv2.split(self.img)

        # reverse
        img_rev = 255 - img_b

        # gaussian blur
        img_blur = cv2.GaussianBlur(img_rev,(5,5),0)
        ret,img_th = cv2.threshold(img_blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        print(f"Otsu threashold value: {ret}")
#         print(ret)
#         show(img_th)

        # opening
        kernel = np.ones((20,20),np.uint8)
        img_open = cv2.morphologyEx(img_th, cv2.MORPH_OPEN, kernel)
#         show(img_open)

        # closing
        img_close = cv2.morphologyEx(img_open, cv2.MORPH_CLOSE, kernel)
#         show(img_close)

        # find center
        img_center = img_close.copy()
        # find contours in the binary image
        contours, hierarchy = cv2.findContours(img_center, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        img_center = cv2.cvtColor(img_center, cv2.COLOR_GRAY2BGR)
        self.obj_center = []
        for c in contours:
            # calculate moments for each contour
            M = cv2.moments(c)
            print(f"contour area: {cv2.contourArea(c)}")
            if 2500<cv2.contourArea(c)<12000:
                # calculate x,y coordinate of center
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                self.obj_center.append((cX, cY))
                cv2.circle(img_center, (cX, cY), 5, (255, 0, 0), -1)
                cv2.putText(img_center, f'({cX}, {cY})', (cX - 25, cY - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 10)
        self.show(img_center)
        self.save_img(img_center)
#         cv2.imwrite('center.jpg', img_center)
        print("egg center at:", self.obj_center)
        return self.obj_center

    def find_center_white_plate(self, show=False):
        _, self.img = self.cam.read()
        img_b, _, _= cv2.split(self.img)

        # reverse
        img_rev = 255 - img_b

        # gaussian blur
        img_blur = cv2.GaussianBlur(img_rev,(5,5),0)
        _, img_th = cv2.threshold(img_blur,150,255,cv2.THRESH_BINARY)
        # noise removal
        kernel = np.ones((7,7),np.uint8)
        opening = cv2.morphologyEx(img_th,cv2.MORPH_OPEN,kernel, iterations = 2)
        # sure background area
        sure_bg = cv2.dilate(opening,kernel,iterations=3)
        # Finding sure foreground area
        dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
        _, sure_fg = cv2.threshold(dist_transform,0.1*dist_transform.max(),255,0)
        # Finding unknown region
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg,sure_fg)
        # Marker labelling
        img_cp = self.img.copy()
        numbers, markers, stats, centroids = cv2.connectedComponentsWithStats(sure_fg)
        # show(markers)
        # Add one to all labels so that sure background is not 0, but 1
        markers = markers+1
        # Now, mark the region of unknown with zero
        markers[unknown==255] = 0
        markers = cv2.watershed(img_cp,markers)
        img_cp[markers == -1] = [0,255,0]
        self.obj_center = []
        # show_rgb(img)
        for i, center in enumerate(centroids):
            print(stats[i][-1])
            # area filtering
            if 1000 < stats[i][-1] < 3000:
                center = center.astype(int)
                self.obj_center.append(center)
                print(center[0], center[1], stats[i])
                cv2.circle(img_cp, (center[0], center[1]), 5, (255, 0, 0), -1)
                cv2.putText(img_cp, f'({center[0]}, {center[1]})', (center[0] - 25, center[1] - 25), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        if show:
            self.show(img_cp)
        self.save_img(img_cp)
#         cv2.imwrite('center.jpg', img_center)
        print("egg center at:", self.obj_center)
        return self.obj_center
