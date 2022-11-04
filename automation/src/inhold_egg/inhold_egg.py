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
egg_count = 0

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
    motor = MT24X(acc_step,  dec_step, vec_step, 'COM5', 115200, ratio=1.9322) # ratio(well)=1.8195, ratio(larve)=1.7857
    motor.move_MODE_P(2, -10000, 36000, 36000, 6000, wait = True)
    motor.calibration(0, 36000, 36000, -6000)
    motor.calibration(1, 36000, 36000, -3000)
    motor.calibration(2, 36000, 36000, 6000)
    motor.calibration(3, 3000, 3000, 1000, wait = True)
except SerialException:
    print(Fore.RED+"Cannot connect motor, please turn off MTHelper.exe, check COM port number, or replug cable"+Style.RESET_ALL)
    sys.exit(1)

mode = 400
if mode == 400:
    motor.plate_init_pos = [27356, 67680]
    motor.plate_size = [20, 20]
    motor.plate_step = [1793, 1803]
    motor.block_init_pos = [17301, 66635]
    motor.z_pos = -27531
    motor.w_pick_pos = -5300
    motor.w_place_pos = -4400
    motor.w_safe_pos = -4000
    motor.niddle_center_pos = [1066, 583]

elif mode == 96:
    motor.plate_init_pos = [25599, 44813] 
    motor.plate_size = [8, 12]
    motor.plate_step = [1800, 1806]
    motor.block_init_pos = [15066, 45084]
    motor.z_pos = -21500
    motor.w_pick_pos = -4050
    motor.w_place_pos = -3450
    motor.niddle_center_pos = [1212, 602]
    motor.w_safe_pos = -2000

# motor_positioning = input("start motor positioning?(y/n)")
# if motor_positioning == "y":
#     # TODO: motor move to edge to callibrate camera 
#     motor.move_MODE_P()    

# # set folder path
# folder_name = input('input folder name:')
folder_name = "test"
image_path = f"../../data/img/inhold_egg/{folder_name}"
print(f"save images at: {image_path}")

# motor move to first hole
motor.move_MODE_P(2, motor.z_pos, 36000, 36000, 6000)
motor.move_MODE_P(0, motor.plate_init_pos[0], 36000, 36000, 6000)
motor.move_MODE_P(1, motor.plate_init_pos[1], 36000, 36000, 5000, wait=True)

 # initialize camera
try:
    cam = ImageProcessing(image_path)
except AttributeError as e:
    print(Fore.RED+"Cannot connect camera, please unplug or close camera app"+Style.RESET_ALL)
    print(e)
    sys.exit(1)

# start transplantation
cam.motor_egg_count = egg_count
try: 
    before = time.time()
    while cam.motor_egg_count <= mode:
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
                centers, frame_pos = cam.find_center_white_plate(show=False, position=motor.frame_init_pos)
                if not centers :
                    print(f"{Fore.RED}egg not found!{Style.RESET_ALL}")
                else:
                    # start inholding eggs
                    for center in centers:
                        if cam.motor_egg_count == mode:
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
                        motor.move_MODE_P(3, motor.w_pick_pos, 12000, 12000, 3000, wait=True)
                        # time.sleep(1)
                        cam.take_photo()
                        motor.move_MODE_P(3, motor.w_safe_pos, 12000, 12000, 3000, wait=True)

                        # motor move to hole
                        hole_0, hole_1 = motor.get_hole_pos(cam.motor_egg_count)
                        motor.move_MODE_P(0, hole_0)
                        motor.move_MODE_P(1, hole_1, wait=True)
                        motor.move_MODE_P(3, motor.w_place_pos, 12000, 12000, 3000, wait=True)
                        # time.sleep(1)
                        cam.take_photo()

                        # release egg,
                        motor.set_out(0, 1)
                        time.sleep(1)
                        
                        # finish
                        motor.set_out(0, 0)
                        motor.calibration(3, 12000, 12000, 3000, wait=True)
                        cam.take_photo()

                        # TODO: debug circles(loop of ufunc does not support argument\
                        #  0 of type NoneType which has no callable rint method)

                        # egg_in_hole = cam.detect_hole(show=False)
                        # if egg_in_hole:
                        #     print("egg in hole, count+1")
                        cam.motor_egg_count += 1
                        # else:
                        #     print('egg not in hole')

                        motor.move_MODE_P(0, motor.frame_init_pos[0])
                        motor.move_MODE_P(1, motor.frame_init_pos[1], wait=True) 

                # move to next block
                # print(f"{Fore.RED}move to next block!{Style.RESET_ALL}")
                motor.block_count += 1
                if j == (motor.block_size[1]-1):
                    print(f"{Fore.RED}move to next block column!{Style.RESET_ALL}")
                    motor.move_MODE_P_REL(0, -motor.block_step[0])
                    motor.move_MODE_P(1, motor.block_init_pos[1], wait=True)
                else:
                    motor.move_MODE_P_REL(1, -motor.block_step[1], wait=True)
        if cam.motor_egg_count <= mode:  
            print(f"{Fore.RED}out of egg, please add eggs{Style.RESET_ALL}") 
            motor.calibration(3, 12000, 12000, 3000, wait=True)
            time.sleep(2)
            motor.move_MODE_P(1, motor.transplate_init_pos[1], wait=True)
            motor.move_MODE_P(0, motor.transplate_init_pos[0], wait=True)
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
motor.calibration(3, 12000, 12000, 3000, wait=True)
time.sleep(2)
motor.move_MODE_P(1, motor.transplate_init_pos[1], wait=True)
motor.move_MODE_P(0, motor.transplate_init_pos[0], wait=True)

