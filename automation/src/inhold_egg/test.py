import cv2
import time 
# 選擇第二隻攝影機
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print(cap)
while(True):
    # 從攝影機擷取一張影像
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
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 釋放攝影機
cap.release()

# 關閉所有 OpenCV 視窗
cv2.destroyAllWindows()