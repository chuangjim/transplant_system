from tkinter import EXCEPTION
from mt24x import MT24X
from image import ImageProcessing
import time
import colorama
from colorama import Fore
from colorama import Style
from serial import SerialException
from sound import Sound
import sys
from server_connection import Linux
import traceback
egg_count = 0

class Classification():
    def __init__(self, egg_count, mode, folder_name=False, callibration=True):

        #init colorbar
        colorama.init()

        # slow_mode = input("slow mode?(y/n)")
        slow_mode ="y"
        if slow_mode == "y" or "":
            acc_step, dec_step, vec_step = 12000, 12000, 5000
        elif slow_mode == "n":
            acc_step, dec_step, vec_step = 72000, 72000, 20000
            # acc_step, dec_step, vec_step = 75000, 75000, 25000

        # initialize motor and set speed
        try:
            self.motor = MT24X(acc_step,  dec_step, vec_step, 'COM5', 115200, ratio=1.9322) # ratio(well)=1.8195, ratio(larve)=1.7857
            self.motor.calibration(3, 3000, 3000, 1000, wait = True)
            if callibration:
                self.motor.move_MODE_P(2, -10000, 36000, 36000, 6000, wait = True)
                self.motor.calibration(0, 36000, 36000, -3000)
                self.motor.calibration(1, 36000, 36000, -3000)
                self.motor.calibration(2, 36000, 36000, 3000)
                self.motor.calibration(3, 3000, 3000, 1000, wait = True)
            self.motor.mode = mode
        except SerialException:
            print(Fore.RED+"Cannot connect motor, please turn off MTHelper.exe, check COM port number, or replug cable"+Style.RESET_ALL)
            sys.exit(1)

        # set motor variables
        if self.motor.mode == 400:
            self.motor.plate_init_pos = [27356, 67680]
            self.motor.plate_size = [20, 20]
            self.motor.plate_step = [1793, 1803]
            self.motor.block_init_pos = [17301, 66635]
            self.motor.z_pos = -27651
            self.motor.w_pick_pos = -5300
            self.motor.w_place_pos = -4400
            self.motor.w_safe_pos = -4000
            self.motor.niddle_center_pos = [1056, 586]

        # folder_name = input('input folder name:')
        if not folder_name:
            folder_name = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        image_path = f"../../data/img/inhold_egg/{folder_name}"
        print(f"save images at: {image_path}")

        # motor move to first hole
        if callibration:
            self.motor.move_MODE_P(2, self.motor.z_pos, 36000, 36000, 12000)
            self.motor.move_MODE_P(0, self.motor.plate_init_pos[0], 36000, 36000, 12000)
            self.motor.move_MODE_P(1, self.motor.plate_init_pos[1], 36000, 36000, 3000, wait=True)

        # initialize camera
        try:
            self.cam = ImageProcessing(image_path)
            self.cam.motor_egg_count = egg_count
        except AttributeError as e:
            print(Fore.RED+"Cannot connect camera, please unplug or close camera app"+Style.RESET_ALL)
            print(e)
            sys.exit(1)
        # return motor, cam

    def take_photo(self):
        block_count = 0
        self.motor.move_MODE_P(0, self.motor.block_init_pos[0])
        self.motor.move_MODE_P(1, self.motor.block_init_pos[1], wait=True)
        print(f"initial position: {self.motor.block_init_pos[0]}, {self.motor.block_init_pos[1]}")

        self.egg_center=[]
        self.frame_pos=[]
        try: 
            for i in range(self.motor.block_size[0]+1):
                for j in range(self.motor.block_size[1]):
                    self.motor.frame_init_pos = [self.motor.get_p(0), self.motor.get_p(1)]
                    # img = cam.take_photo()
                    centers, pos = self.cam.find_center_white_plate(self.motor.frame_init_pos, show=False)
                    if centers:
                        self.egg_center.extend(centers)
                        self.frame_pos.extend(pos)
                    self.motor.move_MODE_P_REL(1, -self.motor.block_step[1], wait=True)
                    block_count += 1
                # img = cam.take_photo()
                self.motor.move_MODE_P_REL(0, -self.motor.block_step[0])
                self.motor.move_MODE_P(1, self.motor.block_init_pos[1], wait=True)
        except KeyboardInterrupt:
            self.motor.move_MODE_P(0, self.motor.block_init_pos[0])
            self.motor.move_MODE_P(1, self.motor.block_init_pos[1])
        # return egg_center, frame_pos

    def image_classification(self, local_path=False):
        # host = Linux('192.168.1.105', 'jim', 'password', '/Users/jim/.ssh/id_rsa')
        self.host = Linux('192.168.1.105', 'jim', 'password', 'D:/Saka/Desktop/莊詠竣/.ssh/id_rsa')
        self.host.connect()
        if not local_path:
            local_path = self.cam.image_crop_path
        remote_path = '/home/jim/Documents/lacewing/transferlearning/predict/0'
        # local_path = '/Users/jim/Desktop/研究所學習資料/碩論/軟硬體資料/data/20220307/20220307-0309/'
        self.host.sftp_put_dir(local_path, remote_path)
        self.classification_result = self.host.send('/usr/bin/zsh /home/jim/Documents/lacewing/transferlearning/cocoon_classifier_test.sh')
        self.host.close()
        # return classification_result

    def inhold_egg(self):

        # motor move to first hole
        self.motor.move_MODE_P(2, self.motor.z_pos, 36000, 36000, 6000)
        self.motor.move_MODE_P(0, self.motor.plate_init_pos[0], 36000, 36000, 6000)
        self.motor.move_MODE_P(1, self.motor.plate_init_pos[1], 36000, 36000, 5000, wait=True)

        # test camera
        self.cam.test()

        # start transplantation
        

        try: 
            before = time.time()
            while self.cam.motor_egg_count <= self.motor.mode:
                self.motor.move_MODE_P(0, self.motor.block_init_pos[0])
                self.motor.move_MODE_P(1, self.motor.block_init_pos[1], wait=True)
                # TODO: from relative position to absolute position
                for i, egg_center in enumerate(self.egg_center):
                    if self.classification_result[i] == '1':
                        if self.cam.motor_egg_count == self.motor.mode:
                            print(f"{Fore.RED}egg plate is full, please change plate!{Style.RESET_ALL}")
                            sound = Sound
                            sound.play_sound()                        
                            raise 
                        print(f"center: {egg_center}")
                        print(Fore.GREEN+"-"*30+f"Egg count: {self.cam.motor_egg_count}"+"-"*30+Style.RESET_ALL)
                        self.motor.move_to_center(egg_center, self.frame_pos[i], absolute=True)
                        # time.sleep(1)
                        self.cam.take_photo()

                        # inhold egg
                        self.motor.set_out(0, 0)
                        self.motor.move_MODE_P(3, self.motor.w_pick_pos, 12000, 12000, 3000, wait=True)
                        # time.sleep(1)
                        self.cam.take_photo()
                        self.motor.move_MODE_P(3, self.motor.w_safe_pos, 12000, 12000, 3000, wait=True)

                        # motor move to hole
                        hole_0, hole_1 = self.motor.get_hole_pos(self.cam.motor_egg_count)
                        self.motor.move_MODE_P(0, hole_0)
                        self.motor.move_MODE_P(1, hole_1, wait=True)
                        self.motor.move_MODE_P(3, self.motor.w_place_pos, 12000, 12000, 3000, wait=True)
                        # time.sleep(1)
                        self.cam.take_photo()

                        # release egg,
                        self.motor.set_out(0, 1)
                        time.sleep(1)
                        
                        # finish
                        self.motor.set_out(0, 0)
                        self.motor.calibration(3, 12000, 12000, 3000, wait=True)
                        self.cam.take_photo()

                        # TODO: debug circles(loop of ufunc does not support argument\
                        #  0 of type NoneType which has no callable rint method)

                        # egg_in_hole = cam.detect_hole(show=False)
                        # if egg_in_hole:
                        #     print("egg in hole, count+1")
                        self.cam.motor_egg_count += 1
                        # else:
                        #     print('egg not in hole')

                        self.motor.move_MODE_P(0, self.motor.frame_init_pos[0])
                        self.motor.move_MODE_P(1, self.motor.frame_init_pos[1], wait=True) 
                        
            if self.cam.motor_egg_count <= self.motor.motor.mode:  
                print(f"{Fore.RED}out of egg, please add eggs{Style.RESET_ALL}") 
                self.motor.calibration(3, 12000, 12000, 3000, wait=True)
                time.sleep(2)
                self.motor.move_MODE_P(1, self.motor.transplate_init_pos[1], wait=True)
                self.motor.move_MODE_P(0, self.motor.transplate_init_pos[0], wait=True)
                input("press enter after adding eggs")
                    
        except KeyboardInterrupt :
            print(f"{Fore.GREEN}Keyboard Interrrupt{Style.RESET_ALL}")
        except Exception as e :
            print(e)
            # print(f"{Fore.GREEN}{Style.RESET_ALL}") 
            # motor.calibration(3, 3000, 3000, 1000)
            # motor.move_MODE_P(0, motor.block_init_pos[0])
            # motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
            pass
        after = time.time()
        print(f'time last: {after-before}')
        self.motor.calibration(3, 12000, 12000, 3000, wait=True)
        time.sleep(2)
        self.motor.move_MODE_P(1, self.motor.transplate_init_pos[1], wait=True)
        self.motor.move_MODE_P(0, self.motor.transplate_init_pos[0], wait=True)

if __name__=="__main__":
    # device = Classification(0, 400, 'test', callibration=False)
    device = Classification(0, 400, callibration=False)
    device.take_photo()
    device.image_classification()
    device.inhold_egg()
    # motor, cam = init(0, 400, 'test')
    # egg_center_dict, frame_pos = take_photo(motor, cam)
    # classification_result = image_classfication(cam.image_crop_path)
    # classification_result = image_classification('D:/Saka/Desktop/莊詠竣/transplant_system/transplant_system/data/img/inhold_egg/test/crop')
    # inhold_egg(motor, cam, egg_center_dict, frame_pos, classification_result)