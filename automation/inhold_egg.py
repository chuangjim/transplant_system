from mt24x import MT24X
from image import ImageProcessing
import cv2
import time
import colorama
from colorama import Fore
from colorama import Style
colorama.init()
# slow_mode = input("slow mode?(y/n)")
slow_mode ="n"
if slow_mode == "y" or "":
    acc_step, dec_step, vec_step = 6000, 6000, 2000
elif slow_mode == "n":
    acc_step, dec_step, vec_step = 36000, 36000, 12000
motor = MT24X(acc_step,  dec_step, vec_step, 'COM3', 115200, ratio=1.8195)
motor.calibration(3, 3000, 3000, 1000)

# folder_name = input('input folder name:')
folder_name = "test"
image_path = f"./img/inhold_egg/{folder_name}"
print(f"save images at: {image_path}")
cam = ImageProcessing(image_path)

motor.move_MODE_P(0, motor.block_init_pos[0])
motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
print(f"initial position: {motor.block_init_pos[0]}, {motor.block_init_pos[1]}")



egg_count = 0
try: 
    for i in range(motor.block_size[0]):
        for j in range(motor.block_size[1]):
            print(Fore.GREEN+"-"*40+f"block count: {motor.block_count}"+"-"*40+Style.RESET_ALL)
            motor.frame_init_pos = motor.get_p
            while True:
                # find egg centers
                centers = cam.find_center_white_plate(show=False)
                if not centers :
                    print(f"{Fore.RED}egg not found!{Style.RESET_ALL}")
                    break
                elif egg_count == 96:
                    print(f"{Fore.RED}egg plate is full, please change plate!{Style.RESET_ALL}")
                    break
                # start inholding eggs
                for center in centers:
                    print(Fore.GREEN+"-"*30+f"Egg count: {egg_count}"+"-"*30+Style.RESET_ALL)
                    motor.move_to_center(center)
                    time.sleep(0.2)
                    cam.take_photo()

                    # inhold egg
                    motor.set_out(0, 0)
                    motor.move_MODE_P(3, -4050, 12000, 12000, 3000, wait=True)
                    time.sleep(0.2)
                    cam.take_photo()
                    motor.move_MODE_P(3, -3000, 12000, 12000, 3000, wait=True)
                    hole_0, hole_1 = motor.get_hole_pos(egg_count)
                    motor.move_MODE_P(0, hole_0)
                    motor.move_MODE_P(1, hole_1, wait=True)
                    time.sleep(0.2)
                    cam.take_photo()

                    # release egg
                    motor.set_out(0, 1)
                    time.sleep(1)
                    
                    # inhold egg
                    motor.set_out(0, 0)
                    cam.take_photo()
                    motor.move_MODE_P(0, motor.frame_init_pos[0])
                    motor.move_MODE_P(1, motor.frame_init_pos[1], wait=True) 
                    egg_count+=1  

            # move to next block
            motor.move_MODE_P_REL(1, -motor.block_step[1], wait=True)
            motor.block_count += 1
        if j == 11:
            print(Fore.GREEN+"-"*40+f"block count: {motor.block_count}"+"-"*40+Style.RESET_ALL)
            motor.move_MODE_P_REL(0, motor.block_step[0])
            motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
            motor.block_count += 1
except KeyboardInterrupt:
    motor.calibration(3, 3000, 3000, 1000)
    motor.move_MODE_P(0, motor.block_init_pos[0])
    motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
    print(f"{Fore.GREEN}KEYBOARD INTERRUPT{Style.RESET_ALL}")

motor.calibration(3, 3000, 3000, 1000)
motor.move_MODE_P(0, motor.block_init_pos[0])
motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
