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
#init colorbar
colorama.init()

# slow_mode = input("slow mode?(y/n)")
slow_mode ="n"
if slow_mode == "y" or "":
    acc_step, dec_step, vec_step = 6000, 6000, 2000
elif slow_mode == "n":
    acc_step, dec_step, vec_step = 36000, 36000, 12000
    # acc_step, dec_step, vec_step = 75000, 75000, 25000


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


# motor_positioning = input("start motor positioning?(y/n)")
# if motor_positioning == "y":
#     # TODO: motor move to edge to callibrate camera 
#     motor.move_MODE_P()    

# # set folder path
folder_name = input('input folder name:')
# folder_name = "dataset_5"
image_path = f"./img/inhold_egg/{folder_name}"
print(f"save images at: {image_path}")

# motor move to first hole
motor.move_MODE_P(2, -27900)
motor.move_MODE_P(0, motor.plate_init_pos[0])
motor.move_MODE_P(1, motor.plate_init_pos[1], wait=True)
print(f"plate position: {motor.block_init_pos[0]}, {motor.block_init_pos[1]}")

 # initialize camera
try:
    cam = ImageProcessing(image_path)
except AttributeError as e:
    print(Fore.RED+"Cannot connect camera, please unplug or close camera app"+Style.RESET_ALL)
    print(e)
    sys.exit(1)

# start transplantation
try: 
    motor.move_MODE_P(0, motor.block_init_pos[0])
    motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
    for i in range(motor.block_size[0]):
        for j in range(motor.block_size[1]):
            print(Fore.GREEN+"-"*40+f"block count: {motor.block_count}"+"-"*40+Style.RESET_ALL)
            motor.frame_init_pos = [motor.get_p(0), motor.get_p(1)]
            print(f"frame init pos: {motor.frame_init_pos}")

            # find egg centers
            cam.take_photo()
            # centers = cam.find_center_white_plate(show=True)
            centers = cam.find_center_white_plate(show=False)
            if not centers :
                print(f"{Fore.RED}egg not found!{Style.RESET_ALL}")
            else:
                # start inholding eggs
                for center in centers:
                    if cam.motor_egg_count > 95:
                        print(f"{Fore.RED}egg plate is full, please change plate!{Style.RESET_ALL}")
                        sound = Sound
                        sound.play_sound()                        
                        raise 
                    print(f"center: {center}")
                    print(Fore.GREEN+"-"*30+f"Egg count: {cam.motor_egg_count}"+"-"*30+Style.RESET_ALL)
                    motor.move_to_center(center)
                    # time.sleep(1)
                    cam.take_photo()

                    # inhold egg
                    motor.set_out(0, 0)
                    motor.move_MODE_P(3, -4150, 12000, 12000, 3000, wait=True)
                    # time.sleep(1)
                    cam.take_photo()
                    motor.move_MODE_P(3, -3300, 12000, 12000, 3000, wait=True)

                    # motor move to hole
                    hole_0, hole_1 = motor.get_hole_pos(cam.motor_egg_count)
                    motor.move_MODE_P(0, hole_0)
                    motor.move_MODE_P(1, hole_1, wait=True)
                    cam.motor_egg_count += 1
                    # time.sleep(1)
                    cam.take_photo()

                    # release egg
                    motor.set_out(0, 1)
                    time.sleep(1)
                    
                    # finish
                    motor.set_out(0, 0)
                    # TODO check hight
                    motor.calibration(3, 12000, 12000, 3000, wait = True)
                    cam.take_photo()
                    motor.move_MODE_P(0, motor.frame_init_pos[0])
                    motor.move_MODE_P(1, motor.frame_init_pos[1], wait=True) 

            # move to next block
            # print(f"{Fore.RED}move to next block!{Style.RESET_ALL}")
            motor.block_count += 1
            if j == (motor.block_size[1]-1):
                print(f"{Fore.RED}move to next block column!{Style.RESET_ALL}")
                motor.move_MODE_P_REL(0, motor.block_step[0])
                motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
            else:
                motor.move_MODE_P_REL(1, -motor.block_step[1], wait=True)

except KeyboardInterrupt :
    print(f"{Fore.GREEN}Keyboard Interrrupt{Style.RESET_ALL}")
except Exception as e :
    print(e)
    # print(f"{Fore.GREEN}{Style.RESET_ALL}")
    # motor.calibration(3, 3000, 3000, 1000)
    # motor.move_MODE_P(0, motor.block_init_pos[0])
    # motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
    pass
motor.calibration(3, 3000, 3000, 1000)
motor.move_MODE_P(0, motor.transplate_init_pos[0])
motor.move_MODE_P(1, motor.transplate_init_pos[1], wait=True)
