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
    while True:
        hole_0, hole_1 = motor.get_hole_pos(cam.motor_egg_count)
        motor.move_MODE_P(0, hole_0)
        motor.move_MODE_P(1, hole_1, wait=True)
        cam.motor_egg_count += 1

except KeyboardInterrupt:
    motor.move_MODE_P(0, motor.block_init_pos[0])
    motor.move_MODE_P(1, motor.block_init_pos[1])
motor.move_MODE_P(0, motor.block_init_pos[0])
motor.move_MODE_P(1, motor.block_init_pos[1])
