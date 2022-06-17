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

# slow_mode = input("slow mode?(y/n)")
slow_mode ="n"
if slow_mode == "y" or "":
    acc_step, dec_step, vec_step = 6000, 6000, 2000
elif slow_mode == "n":
    acc_step, dec_step, vec_step = 36000, 36000, 12000

# initialize motor
try:
    motor = MT24X(acc_step,  dec_step, vec_step, 'COM3', 115200, ratio=1.8195)
    motor.calibration(0, 36000, 36000, -12000)
    motor.calibration(1, 36000, 36000, -12000)
    motor.calibration(2, 36000, 36000, 12000)
    motor.calibration(3, 3000, 3000, 1000, wait = True)
except SerialException:
    print(Fore.RED+"Cannot connect motor, please turnoff MTHelper.exe, check COM port number, or replug cable"+Style.RESET_ALL)
    sys.exit(1)
motor.calibration(3, 3000, 3000, 1000)


# # set folder path
# folder_name = input('input folder name:')
folder_name = "test"
image_path = f"./img/inhold_egg/{folder_name}"
print(f"save images at: {image_path}")

# initialize camera
try:
    cam = ImageProcessing(image_path)
except AttributeError as e:
    print(Fore.RED+"Cannot connect camera, please unplug or close camera app"+Style.RESET_ALL)
    print(e)
    sys.exit(1)

# motor move to first block
motor.move_MODE_P(2, -27900)
motor.move_MODE_P(0, motor.block_init_pos[0])
motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
print(f"initial position: {motor.block_init_pos[0]}, {motor.block_init_pos[1]}")


# start transplantation
egg_count = 0
try: 
    for i in range(motor.block_size[0]):
        for j in range(motor.block_size[1]):
            print(Fore.GREEN+"-"*40+f"block count: {motor.block_count}"+"-"*40+Style.RESET_ALL)
            motor.frame_init_pos = [motor.get_p(0), motor.get_p(1)]
            print(f"frame init pos: {motor.frame_init_pos}")

            # find egg centers
            cam.take_photo()
            centers = cam.find_center_white_plate(show=True)
            if not centers :
                print(f"{Fore.RED}egg not found!{Style.RESET_ALL}")
            elif egg_count == 96:
                print(f"{Fore.RED}egg plate is full, please change plate!{Style.RESET_ALL}")
                raise 
            else:
                # start inholding eggs
                for center in centers:
                    print(Fore.GREEN+"-"*30+f"Egg count: {egg_count}"+"-"*30+Style.RESET_ALL)
                    motor.move_to_center(center)
                    time.sleep(0.2)
                    cam.take_photo()

                    # inhold egg
                    motor.set_out(0, 0)
                    motor.move_MODE_P(3, -4045, 12000, 12000, 3000, wait=True)
                    time.sleep(0.2)
                    cam.take_photo()
                    motor.move_MODE_P(3, -3300, 12000, 12000, 3000, wait=True)

                    # motor move to hole
                    hole_0, hole_1 = motor.get_hole_pos(egg_count)
                    motor.move_MODE_P(0, hole_0)
                    motor.move_MODE_P(1, hole_1, wait=True)
                    time.sleep(0.2)
                    cam.take_photo()

                    # release egg
                    motor.set_out(0, 1)
                    time.sleep(1)
                    
                    # finish
                    motor.set_out(0, 0)
                    # TODO check hight
                    motor.move_MODE_P(3, -2800, 12000, 12000, 3000, wait=True)
                    cam.take_photo()
                    motor.move_MODE_P(0, motor.frame_init_pos[0])
                    motor.move_MODE_P(1, motor.frame_init_pos[1], wait=True) 
                    egg_count+=1  

            # move to next block
            # print(f"{Fore.RED}move to next block!{Style.RESET_ALL}")
            motor.move_MODE_P_REL(1, -motor.block_step[1], wait=True)
            motor.block_count += 1
            if j == 10:
                print(Fore.GREEN+"-"*40+f"block count: {motor.block_count}"+"-"*40+Style.RESET_ALL)
                print(f"{Fore.RED}move to next block column!{Style.RESET_ALL}")
                motor.move_MODE_P_REL(0, motor.block_step[0])
                motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
                motor.block_count += 1
except KeyboardInterrupt :
    print(f"{Fore.GREEN}Keyboard Interrrupt{Style.RESET_ALL}")
except Exception as e :
    print(e)
    # print(f"{Fore.GREEN}{Style.RESET_ALL}")
    pass
motor.calibration(3, 3000, 3000, 1000)
motor.move_MODE_P(0, motor.block_init_pos[0])
motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
