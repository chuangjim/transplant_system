import cv2
import numpy as np
import os
import time
class ImageProcessing:
    def __init__(self, image_path, test = False):
        self.cam_id = 0
        self.image_path = image_path
        self.image_crop_path = f"{self.image_path}/crop"
        self.cam = cv2.VideoCapture(self.cam_id, cv2.CAP_DSHOW)
        # self.cam.set(cv2.CAP_PROP_BUFFERSIZE, 0)
        self.cam.set(3,1920)
        self.cam.set(4,1080)
        self.img_count = 0
        self.img_egg_count = 0
        self.motor_egg_count = 0
        self.take_photo(save=False)
        if test:
            self.test()

    def test(self):
        # cv2.namedWindow("egg", 0)
        # cv2.resizeWindow("egg", 960, 540)
        # self.cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, self.img = self.cam.read()
        if not ret:
            print("failed to grab frame")    
        else: self.show(self.img)

    def show(self, img):
        cv2.namedWindow("egg", 0)
        cv2.resizeWindow("egg", 960, 540)    
        while True:
            cv2.imshow("egg",img)
            if cv2.waitKey(10) & 0xff == ord('q'):
                break
        cv2.destroyAllWindows()
        
    def take_photo(self, show=False, save=True):
        # self.cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, self.img = self.cam.read()
        while not ret:
            print('!!!!!!!!!!camera shut down. reload camera!!!!!!!!!')
            self.cam.release()  
            cv2.destroyAllWindows()    
            self.cam = cv2.VideoCapture(self.cam_id, cv2.CAP_DSHOW)
            self.cam.set(3,1920)
            self.cam.set(4,1080)
            ret, self.img = self.cam.read()
            time.sleep(0.1)

        if show:
            self.show(self.img)
        # cv2.destroyAllWindows()
        if save:
            self.save_img(self.img)
        return self.img

    def save_img(self,img, crop = False):
        if crop:
            folder_path = self.image_crop_path
            count = self.img_egg_count
            self.img_egg_count += 1
        else:
            folder_path = self.image_path
            count = self.img_count
            self.img_count += 1
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = f"{folder_path}/{count}.jpg"
        cv2.imwrite(file_path, img)
        print(f"save images at: {file_path}")
        return self.img
    
    def find_center_filter_screen(self):
        # self.cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.img = self.take_photo()
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
        # self.cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.img = self.take_photo()
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
        for i, center in enumerate(centroids):
            # print(stats[i][-1])
            # area filtering
            # TODO: find suitable area
            if 1000 < stats[i][-1] < 4500:
                center = center.astype(int)
                self.obj_center.append(center)
                # print(center[0], center[1], stats[i])
                cv2.circle(img_cp, (center[0], center[1]), 5, (255, 0, 0), -1)
                cv2.putText(img_cp, f'({center[0]}, {center[1]})', (center[0] - 25, center[1] - 25), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                # crop one egg frop image
                top = 0 if (center[1]-50 < 0) else center[1]-50
                down = 1080 if (center[1]+50 > 1080) else center[1]+50
                left = 0 if (center[0]-50 < 0) else center[0]-50
                right = 1920 if (center[0]+50 > 1920) else center[0]+50


                crop_img = self.img[top:down, left:right]
                # print(crop_img)
                # self.show(crop_img)
                self.save_img(crop_img, crop=True)
        if show:
            self.show(img_cp)
        self.save_img(img_cp)
#         cv2.imwrite('center.jpg', img_center)
        if self.obj_center:
            print("egg center at:", self.obj_center)
        return self.obj_center

    def detect_hole(self, show=False):
        # show_rgb(img)
        self.img = self.take_photo()
        img_b, _, _= cv2.split(self.img)
        # show(img_b)
        # reverse
        img_rev = 255 - img_b
        circles = cv2.HoughCircles(img_rev,cv2.HOUGH_GRADIENT,1,600,
                                    param1=50,param2=50,minRadius=176,maxRadius=235)
        circles = np.uint16(np.around(circles))
        img_draw = img_rev.copy()
        # for i in circles[0,:]:
        #     cv2.circle(img_draw,(i[0],i[1]),i[2],(0,255,0),2)
        #     cv2.circle(img_draw,(i[0],i[1]),2,(0,0,255),3)
        # show(img_draw)
        min = np.argmin(circles[0,:], axis=0)[0]
        circle = circles[0,:][min]
        mask = np.full(img_b.shape[:2], 0, dtype=np.uint8)
        mask = cv2.circle(mask, (circle[0], circle[1]), circle[2], (255, 255, 255),-1)
        img_draw = cv2.bitwise_and(img_draw, img_draw, mask=mask)
        y1 = int(circle[1])-circle[2] if (int(circle[1])-circle[2]) > 0 else 0
        y2 = int(circle[1])+circle[2] if (int(circle[1])+circle[2]) < 1080 else 1080
        x1 = int(circle[0])-circle[2] if (int(circle[0])-circle[2]) > 0 else 0
        x2 = int(circle[0])+circle[2] if (int(circle[0])+circle[2]) < 1920 else 1920
        img_draw = img_draw[y1:y2, x1:x2]
        # show(img_draw)
        ret, img_th = cv2.threshold(img_draw,170,255,cv2.THRESH_BINARY)
        # show(img_th)
        # find contours in the binary image
        contours, hierarchy = cv2.findContours(img_th, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            # calculate moments for each contour
            M = cv2.moments(c)
            print(f'area:{cv2.contourArea(c)}, M["m00"]: {M["m00"]}')
            if 507 < cv2.contourArea(c) < 620:
                # calculate x,y coordinate of center
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.circle(img_draw, (cX, cY), 5, (255, 0, 0), -1)
                cv2.putText(img_draw, f'({cX}, {cY})', (cX - 25, cY - 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
                if show:
                    self.show(img_draw)
                return True