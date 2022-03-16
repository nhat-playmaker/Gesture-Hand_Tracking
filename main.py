import cv2
import mediapipe as mp
import numpy as np
import time
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandTrackingModule as htm

cap = cv2.VideoCapture(0)

pTime = 0
cTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volumeRange = volume.GetVolumeRange()

# Uncomment if u want to set the default system volume
# Range -65 (0%) to 0 (100%)
volume.SetMasterVolumeLevel(0, None)

minVolume = volumeRange[0]
maxVolume = volumeRange[1]

# Hand range
minHandRange = 50
maxHandRange = 150

vol = 0
volBar = 400
volPercent = 100
cntFingerDownFrame = 0

while True:
    _, img = cap.read()

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)

    if len(lmList) != 0:

        # STEP 1: Filter based on size
        area = (bbox[2] * bbox[3]) // 100

        if 150 < area < 1000:

            # STEP 2: Find distance between index and thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)

            # STEP 3: Convert volume
            # Volume Range -65 - 0
            volBar = np.interp(length, [minHandRange, maxHandRange], [400, 150])
            volPercent = np.interp(length, [minHandRange, maxHandRange], [0, 100])

            # STEP 4: Reduce resolution
            smoothness = 5
            volPercent = smoothness * round(volPercent/smoothness)

            # STEP 5: Check finger up
            fingers = detector.fingersUp()
            print(fingers)

            # STEP 5.1: If pinky down then set the volume
            if not fingers[4]:
                cntFingerDownFrame += 1
                if cntFingerDownFrame >= 10:
                    volume.SetMasterVolumeLevelScalar(volPercent / 100, None)
                    cv2.circle(img, lineInfo[2], 10, (0, 255, 0), cv2.FILLED)
            else:
                cntFingerDownFrame = 0

    # Drawing
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPercent)} %', (48, 438), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, 'VolSet: ' + str(int(cVol)), (300, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # Frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, 'FPS: ' + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow('image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
