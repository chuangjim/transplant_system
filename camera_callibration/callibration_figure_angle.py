import json
import math
import os
from  matplotlib import pyplot as plt
from scipy import stats
import numpy as np
import math


path_to_json = './data/'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('r_1.797.json')]
# json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('r_1.773.json')]

print(json_files)  # for me this prints ['foo.json']
data = []
for file in json_files:
    # Opening JSON file
    f = open(path_to_json + file)
    data += json.load(f)
print(f"numbers of data: {len(data)}")
plt.figure(figsize=(16,8))
x = [[],[],[],[]]
y = [[],[],[],[]]
x_all = []
y_all = []
colors = []


for count, i in enumerate(data):
    try:
        diff_x = diff_x = i['before'][0][0]-960
        diff_y = i['before'][0][1]-540
        angle = 360*(np.arctan2(diff_y,diff_x))/(2*np.pi)
        error = math.sqrt((i['after'][0][0]-960)**2+(i['after'][0][1]-540)**2)
        if error < 100:
            if diff_x > 0:
                if diff_y < 0:  # 第一象限
                    colors.append('red')
                    x[0].append(angle)
                    y[0].append(error)
                else:  # 第四象限
                    colors.append('blue')
                    x[3].append(angle)
                    y[3].append(error)
            else:
                if diff_y > 0:  # 第三象限
                    colors.append('yellow')
                    x[2].append(angle)
                    y[2].append(error)
                else:  # 第二象限
                    colors.append('green')
                    x[1].append(angle)
                    y[1].append(error)
            x_all.append(angle)
            y_all.append(error)
        else:
            print(f"large error: {i}")
    except:
        print(f"error: {i}")


def myfunc(x):
    return slope * x + intercept
list_color = ['red', 'blue', 'yellow', 'green']
# for i, _ in enumerate(x):
#     slope, intercept, r, p, std_err = stats.linregress(x[i], y[i])
#     print(r)
#     mymodel = list(map(myfunc, x[i]))
    # plt.plot(x[i], mymodel, label=f'{slope:.4f}x+{intercept:.4f}',c=list_color[i])
slope, intercept, r, p, std_err = stats.linregress(x_all, y_all)
print(r)
mymodel = list(map(myfunc,x_all))
# plt.scatter(x_all, y_all, c=colors, marker='.')
plt.scatter(x_all, y_all, c='k', marker='.')
plt.plot(x_all, mymodel, label=f'{slope:.4f}x+{intercept:.4f}, r={r:.2f}',c='r')
plt.xlabel('angle(degree)')
plt.ylabel('error(pixels)')
plt.title('Callibration result')
plt.xlim(-200,200)
plt.ylim(0,20)
plt.legend(loc=2)
plt.show()
