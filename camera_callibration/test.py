import sys
sys.path.insert(0, 'D:/Desktop/莊詠竣/transplant_system/transplant_system/automation')
from image import ImageProcessing
cam = ImageProcessing()
point_before = cam.find_center()
print("before:",point_before)
