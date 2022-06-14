from mt24x import MT24X
from image import ImageProcessing
import time
import colorama
from colorama import Fore
from colorama import Style
colorama.init()
acc_step, dec_step, vec_step = 36000, 36000, 12000
motor = MT24X(acc_step,  dec_step, vec_step, 'COM3', 115200)
folder_name = input('input folder name:')
image_path = f"./img/take_picture/{folder_name}"
print(f"save images at: {image_path}")
cam = ImageProcessing(image_path)
motor.move_MODE_P(0, motor.block_init_pos[0])
motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
try:
    for i in range(motor.block_size[0]):
        for j in range(motor.block_size[1]):
            # if motor.block_count in []
            print(Fore.GREEN+"-"*40+f"block count: {motor.block_count}"+"-"*40+Style.RESET_ALL)
            img = cam.take_photo()
            motor.move_MODE_P_REL(1, -motor.block_step[1])
            motor.block_count += 1
            # cam.show(img)
            if j == 11:
                print(Fore.GREEN+"-"*40+f"block count: {motor.block_count}"+"-"*40+Style.RESET_ALL)
                img = cam.take_photo()
                motor.move_MODE_P_REL(0, motor.block_step[0])
                motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
                motor.block_count += 1

except KeyboardInterrupt:
    motor.move_MODE_P(0, motor.block_init_pos[0])
    motor.move_MODE_P(1, motor.block_init_pos[1])
motor.move_MODE_P(0, motor.block_init_pos[0])
motor.move_MODE_P(1, motor.block_init_pos[1])
