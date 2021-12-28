import cv2
import mediapipe as mp
import numpy as np
import time
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandTrackingModule as htm

cap = cv2.VideoCapture(1)

pTime = 0
cTime = 0

detector = htm.handDetector()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volumeRange = volume.GetVolumeRange()

# Uncomment if u want to set the default system volume
# Range -65 (0%) to 0 (100%)
volume.SetMasterVolumeLevel(0, None)

minVolume = volumeRange[0]
maxVolume = volumeRange[1]


while True:
    _, img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        p1 = (lmList[4][1], lmList[4][2])
        p2 = (lmList[8][1], lmList[8][2])
        px = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)

        cv2.circle(img, p1, 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, p2, 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, p1, p2, (0, 255, 0), 2, 2)

        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        # print(length)

        # Hand range 50 - 300

        # Volume Range -65 - 0
        vol = np.interp(length, [25, 150], [minVolume, maxVolume])
        volume.SetMasterVolumeLevel(vol, None)
        print(length, ' ', vol)

        if length < 50:
            cv2.circle(img, px, 10, (0, 255, 0), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, 'FPS: ' + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

    cv2.imshow('image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
