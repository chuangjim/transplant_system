from tkinter import EXCEPTION
from mt24x import MT24X
from image import ImageProcessing
import cv2
import time
import colorama
from colorama import Fore
from colorama import Style
from serial import SerialException
import sys
#init colorbar
colorama.init()




print(Fore.GREEN+"start camera and motor callibration"+Style.RESET_ALL)
acc_step, dec_step, vec_step = 36000, 36000, 12000
# initialize motor
try:
    motor = MT24X(acc_step,  dec_step, vec_step, 'COM3', 115200, ratio=1.8195)
    motor.calibration(0, 36000, 36000, -12000)
    motor.calibration(1, 36000, 36000, -12000)
    motor.calibration(2, 36000, 36000, 12000)
    motor.calibration(3, 3000, 3000, 1000, wait = True)
except SerialException:
    print(Fore.RED+"Cannot connect motor, please turn off MTHelper.exe, check COM port number, or replug cable"+Style.RESET_ALL)
    sys.exit(1)
folder_name = "test"
image_path = f"./img/inhold_egg/{folder_name}"

 # initialize camera
try:
    cam = ImageProcessing(image_path)
except AttributeError as e:
    print(Fore.RED+"Cannot connect camera, please unplug or close camera app"+Style.RESET_ALL)
    print(e)
    sys.exit(1)

print(Fore.GREEN+"egg position callibration"+Style.RESET_ALL)

try: 
    motor.move_MODE_P(0, motor.block_init_pos[0])
    motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
    for i in range(motor.block_size[0]):
        for j in range(motor.block_size[1]):
            print(Fore.GREEN+"-"*40+f"block count: {motor.block_count}"+"-"*40+Style.RESET_ALL)
            motor.frame_init_pos = [motor.get_p(0), motor.get_p(1)]
            print(f"frame init pos: {motor.frame_init_pos}")

            # centers = cam.find_center_white_plate(show=True)
            centers = cam.find_center_white_plate(show=False)
            if not centers :
                print(f"{Fore.RED}egg not found!{Style.RESET_ALL}")
            else:
                # start inholding eggs
                for center in centers:
                    motor.move_to_center(center)
                    cv2.namedWindow("egg", 0)
                    cv2.resizeWindow("egg", 960, 540)
                    while True:
                        ret, cam.img = cam.cam.read()
                        cv2.imshow("egg",cam.img)
                        motor.set_out(0, 0)
                        motor.move_MODE_P(3, -4180, 12000, 12000, 3000, wait=True)

                        if cv2.waitKey(10) & 0xff == ord('q'):
                            break



except KeyboardInterrupt :
    print(f"{Fore.GREEN}Keyboard Interrrupt{Style.RESET_ALL}")
except Exception as e :
    print(e)
motor.calibration(3, 3000, 3000, 1000)
motor.move_MODE_P(0, motor.transplate_init_pos[0])
motor.move_MODE_P(1, motor.transplate_init_pos[1], wait=True)


def update_cfg_value(cmd, t_dict, key, delta):
    if cmd==ord('q'):
        exit()
    elif cmd==ord('h'):
        t_dict[key] += delta
    elif cmd==ord('l'):
        t_dict[key] -= delta
    elif cmd==ord('k'):
        print()
        print("OK!")
        return True
    
    print(t_dict[key], end="                    \r")
    return False