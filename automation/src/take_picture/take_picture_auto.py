# # add system path to use class/module from other folder
# import os
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__),'../../'))
# print(sys.path)
# from src.inhold_egg.mt24x import MT24X
# from src.inhold_egg.image import ImageProcessing
from mt24x import MT24X
from image import ImageProcessing
import time
from datetime import datetime
acc_step, dec_step, vec_step = 36000, 36000, 12000

motor = MT24X(acc_step,  dec_step, vec_step, 'COM3', 115200)
dim_0 = 8
dim_1 = 12
step_0 = 1800
step_1 = 1806


# init_x = motor.get_p(0)
# init_y = motor.get_p(1)
init_x = 43100
init_y = 46300
init_z = -30073
motor.move_MODE_P(2, init_z, wait=True)
motor.move_MODE_P(0, init_x)
motor.move_MODE_P(1, init_y, wait=True)
print(f"initial position: {init_x}, {init_y}")
init_pos = {
    1:[45645,48073],
    2:[25749,48073],
    3:[3754,48073],
    
}
try: 
    for i in range(1,4):
        motor.move_MODE_P(0, init_pos[i][0])
        motor.move_MODE_P(1, init_pos[i][1], wait=True)
        count = 0
        now = datetime.now()
        folder_name = now.strftime('%Y%m%d_%H%M%S')
        folder_name += f'_{i}'
        image_path = f"../../data/img/take_picture/{folder_name}"
        print(f"save images at: {image_path}")
        cam = ImageProcessing(image_path, test=False)
        for j in range(dim_0):
            for k in range(dim_1):
                time.sleep(1)
                cam.take_photo()
                if k != (dim_1-1):                
                    motor.move_MODE_P_REL(1, -step_1)
                count += 1

            if j != (dim_0-1):
                motor.move_MODE_P_REL(0, step_0)
                motor.move_MODE_P(1, init_pos[i][1], wait=True)
except KeyboardInterrupt:
    motor.move_MODE_P(0, init_x)
    motor.move_MODE_P(1, init_y)
motor.move_MODE_P(0, init_x)
motor.move_MODE_P(1, init_y)