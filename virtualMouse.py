import cv2
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui

wCam = 640
hCam = 480
frameR = 100
smooth = 5
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
cTime = 0

cnt_frame = 0

detector = htm.handDetector(maxHands=1)

wScr, hScr = pyautogui.size()
print((wScr, hScr))

cnt = 0
frame_cnt = 0

while True:
    # 1. Find hand's landmark
    _, img = cap.read()
    cnt_frame += 1
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # 2. Get finger index
    if len(lmList) != 0:

        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # 3. Check which fingers are up
        fingers = detector.fingersUp()
        print(fingers)

        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (0, 255, 255), 2)

        # 4. Only index finger: Moving mode
        if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:

            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # 6. Smoothen value
            clocX = plocX + (x3 - clocX) / smooth
            clocY = plocY + (y3 - clocY) / smooth

            # 7. Move mouse
            if cnt_frame >= 10:
                pyautogui.moveTo(wScr - clocX, clocY, _pause=False)
                print(x1, y1)
                print(int(wScr - clocX), int(clocY))
                cv2.circle(img, (int(wScr - clocX), int(clocY)), 15, (255, 0, 255), cv2.FILLED)

            plocX = clocX
            plocY = clocY

        # 8. Both middle finger and index finger are up: Click Mouse
        if fingers[1] == 1 and fingers[2] == 1:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 40:
                cnt += 1
                if cnt > 10:
                    cnt = 0
                    pyautogui.click()

    # 11. Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, 'FPS: ' + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # 12. Display
    cv2.imshow('image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
