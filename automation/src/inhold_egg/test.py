import cv2
import time 
# 選擇第二隻攝影機
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
i=0
print(cap)
while(True):
    # 從攝影機擷取一張影像
    # cap.set(3,1920)
    # cap.set(4, 1080)
    ret, frame = cap.read()
    if ret:
        # 顯示圖片
        cv2.imshow('frame', frame)
    else:
        print(f'{time.asctime()}:failed to read camera')
        try:
            # 釋放攝影機
            cap.release()

            # 關閉所有 OpenCV 視窗
            cv2.destroyAllWindows()
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            print('try to reconnect')
        except:
            pass
    # 若按下 q 鍵則離開迴圈
    k = cv2.waitKey(1)
    if k==27:
        print('exit')
        break
    elif k==ord('s'):
        cv2.imwrite('./test/'+str(i)+'.jpg', frame) 
        print(f'save image {i}.jpg')
        i+=1

    elif k==ord('r'):
                    # 釋放攝影機
        cap.release()
        # 關閉所有 OpenCV 視窗
        cv2.destroyAllWindows()
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        print('try to reconnect')

# 釋放攝影機
cap.release()

# 關閉所有 OpenCV 視窗
cv2.destroyAllWindows()