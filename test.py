# 3d fig
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json
import math
  
# Opening JSON file
f = open("../findcenter_callibration.json")
data = json.load(f)
x = []
y = []
diff = []
colors = []


for i in data:
    diff_x = i['before'][0][0]-960
    diff_y = i['before'][0][1]-540
    if diff_x > 0:
        if diff_y > 0:  # 第一象限
            colors.append('red')
        else:  # 第四象限
            colors.append('blue')
    else:
        if diff_y > 0:  # 第二象限
            colors.append('yellow')
        else:  # 第三象限
            colors.append('green')

    diff_after = math.sqrt((i['after'][0][0]-960)**2+(i['after'][0][1]-540)**2)
    x.append(diff_x)
    y.append(diff_y)
    diff.append(diff_after)

#  将数据点分成三部分画，在颜色上有区分度
# ax.scatter(x, y, diff, c=diff, cmap="hot_r")  # 绘制数据点
ax = plt.subplot(111, projection='3d')  # 创建一个三维的绘图工程
ax.scatter(x, y, diff, c=colors)  # 绘制数据点
# X,Y = np.meshgrid(np.array(x),np.array(y))
# ax.plot_surface(X, Y, np.array(diff), rstride=1,cstride=1,cmap=plt.get_cmap('rainbow'))  # 绘制数据点
ax.plot(x, y, 'k.', zdir='z')
# ax.scatter(x[10:20], y[10:20], z[10:20], c='r')
# ax.scatter(x[30:40], y[30:40], z[30:40], c='g')

ax.set_zlabel('error')  # 坐标轴
ax.set_ylabel('Y')
ax.set_xlabel('X')
plt.show()
