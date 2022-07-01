from mt24x import MT24X
from image import ImageProcessing
import time
acc_step, dec_step, vec_step = 36000, 36000, 12000

motor = MT24X(acc_step,  dec_step, vec_step, 'COM3', 115200)

folder_name = input('input folder name:')
image_path = f"./img/take_picture/{folder_name}"
print(f"save images at: {image_path}")
cam = ImageProcessing(image_path)
dim_0 = 8
dim_1 = 12
step_0 = ((55550-43100)/dim_0-1)
step_1 = ((46100-26200)/dim_1-1)
count = 0

# init_0 = motor.get_p(0)
# init_1 = motor.get_p(1)
init_0 = 43100
init_1 = 46300
motor.move_MODE_P(0, init_0)
motor.move_MODE_P(1, init_1, wait=True)
print(f"initial position: {init_0}, {init_1}")
try: 
    for i in range(dim_0+1):
        for j in range(dim_1):
            time.sleep(0.1)
            img = cam.take_photo()
            step_1_int = int(step_1*(j+1)-int(step_1*j))
            motor.move_MODE_P_REL(1, -step_1_int)
            count += 1
        img = cam.take_photo()
        step_0_int = int(step_0*(i+1)-int(step_0*i))
        print(f"step0: {step_0_int}")
        motor.move_MODE_P_REL(0, step_0_int)
        motor.move_MODE_P(1, init_1, wait=True)
except KeyboardInterrupt:
    motor.move_MODE_P(0, init_0)
    motor.move_MODE_P(1, init_1)
motor.move_MODE_P(0, init_0)
motor.move_MODE_P(1, init_1)