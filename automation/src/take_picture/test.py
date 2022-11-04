from datetime import datetime
now = datetime.now()
now_str = now.strftime('%Y%m%d_%H%M%S')
now_str += f'_{1}'
# print(now_str)
init_pos = {
    1:[10000,10000],
    2:[10000,10000],
    3:[10000,10000],
    
}
for i in range(1,4):
    print(init_pos[i][1])
import os
import sys
print(os.path.dirname(sys.executable))