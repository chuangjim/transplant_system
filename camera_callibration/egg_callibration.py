import sys
sys.path.insert(0, 'D:/Desktop/莊詠竣/transplant_system/transplant_system/automation')
from mt24x import MT24X
from image import ImageProcessing
import time
import json

motor = MT24X(ratio=1.8195, acc_step=6000, dec_step=6000, vec_step=2000\
    , port='COM3', baudrate=115200)
folder_name = input('input folder name:')
image_path = f"./img/egg/egg_{folder_name}"
print(f"save images at: {image_path}")
cam = ImageProcessing(image_path)
json_path = f'./data/egg_{folder_name}.json'
print(f"save json at: {json_path}")

json_data = []
x_center = motor.get_p(0)
y_center = motor.get_p(1)
print("center:", x_center, y_center)
step = 200
count = 0
dim_x = 17
dim_y = 9  

def append_json(count, before, after):
    json_data.append({
        "name": count,
        "before": before,
        "after" : after
    })

def save_json():
    with open(json_path, 'w') as json_file:
        json.dump(json_data, json_file,indent=4, separators=(',',': '))
try:
    for i in range(dim_x):
        for j in range(dim_y):
            print("_"*30 + f"count: {count}" + "_"*30)
            x_diff = int(((count%dim_x) - (dim_x-1)/2 ) * step)
            y_diff = int((count//dim_x - (dim_y-1)/2) * step)
            print(f"count: {count}, x_diff: {x_diff}, y_diff: {y_diff}")
            motor.move_MODE_P(0, x_center + x_diff)
            motor.move_MODE_P(1, y_center + y_diff, wait = True)
            time.sleep(0.5)
            cam.take_photo()
            point_before = cam.find_center_white_plate()
            print("before:",point_before)
            motor.move_to_center(point_before[0])
            cam.take_photo()
            cam.take_photo()
            point_after = cam.find_center_white_plate()
            print("after:", point_after)
            append_json(count, point_before, point_after)
            count += 1
            
except Exception as e:
    print(e)

motor.move_MODE_P(0, x_center)
motor.move_MODE_P(1, y_center, wait = True)
save_json()