import cv2
import mediapipe as mp
import math
from google.protobuf.json_format import MessageToDict


class handDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, 1, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        hand_label = None
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            handedness_dict = MessageToDict(self.results.multi_handedness[0])
            hand_label = handedness_dict.get('classification')[0].get('label')

            for handLandmark in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLandmark, self.mpHands.HAND_CONNECTIONS)

        return img, hand_label

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        self.lmList = []

        bbox = (0, 0, 0, 0)
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            min_x = min(xList) - 10
            min_y = min(yList) - 10
            max_x = max(xList) + 10
            max_y = max(yList) + 10
            bbox = (min_x, min_y, max_x-min_x, max_y-min_y)
            if draw:
                cv2.rectangle(img, bbox, (0, 255, 0), 2)

        return self.lmList, bbox

    def fingersUp(self):
        fingers = []

        # Thumb
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def findDistance(self, x1, x2, img, draw=True):
        p1 = (self.lmList[x1][1], self.lmList[x1][2])
        p2 = (self.lmList[x2][1], self.lmList[x2][2])
        px = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)

        if draw:
            cv2.circle(img, p1, 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, p2, 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, px, 10, (255, 0, 255), cv2.FILLED)
            cv2.line(img, p1, p2, (0, 255, 0), 2, 2)

        length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])

        return length, img, (p1, p2, px)
