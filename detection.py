# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 13:59:58 2025

@author: blafont846
"""

import cv2
import numpy as np
from djitellopy import Tello
import time
import mediapipe as mp

# Initialisation du drone
tello1 = Tello()
tello1.connect()
print('Niveau de batterie :', tello1.get_battery())
tello1.streamon()
tello1.send_rc_control(0, 0, 0, 0)
time.sleep(2.2)

# Paramètres vidéo et PID
w, h = 640, 480  # Résolution plus légère
fbRange = [6200, 6800]
pid = [0.4, 0.4, 0]
pError = 0
cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

# Initialisation de MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Configuration du détecteur de visages
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.2)

def findFace(img):
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_detection.process(imgRGB)

    myFaceListC = []
    myFaceListArea = []

    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = img.shape
            x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cx = x + w // 2
            cy = y + h // 2
            area = w * h
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
            myFaceListC.append([cx, cy])
            myFaceListArea.append(area)

    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]


# Fonction de suivi de visage avec ajustement dynamique des PID
def trackFace(info, w, pid, pError):
    area = info[1]
    x, y = info[0]
    fb = 0
    error = x - w // 2
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -100, 100))
    
    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -20
    elif area < fbRange[0] and area != 0:
        fb = 20

    if x == 0:
        speed = 0
        error = 0

    tello1.send_rc_control(0, fb, 0, speed)
    return error

# Fonction principale pour démarrer le suivi de visage
def start_tracking():
    cap = cv2.VideoCapture(0)

    global pError
    while True:
        img = tello1.get_frame_read().frame
        img = cv2.resize(img, (w, h))
        
        img, info = findFace(img)
        pError = trackFace(info, w, pid, pError)
        
        cv2.imshow('Output', img)

        # Quitter avec 'q' ou atterrir automatiquement
        if cv2.waitKey(1) & 0xFF == ord('q'):
            tello1.land()
            break

    cap.release()
    cv2.destroyAllWindows()

# Démarrer le suivi
start_tracking()
