# -*- coding: utf-8 -*-
"""
Créé le 11 mars 2025
Auteur : blafont846
"""

import cv2  # OpenCV pour le traitement d'image
import numpy as np  # Numpy pour les calculs
from djitellopy import Tello  # Bibliothèque pour contrôler le drone Tello
import time  # Pour les temporisations
import mediapipe as mp  # MediaPipe pour la détection de visages

# ===== Initialisation du drone =====
tello1 = Tello()  # Création de l'objet drone
tello1.connect()  # Connexion au drone

print('Niveau de batterie :', tello1.get_battery())  # Affiche le niveau de batterie
tello1.streamon()  # Active le flux vidéo du drone
tello1.send_rc_control(0, 0, 0, 0)  # Envoie des commandes nulles au début
time.sleep(2.2)  # Petite pause pour laisser le temps au flux de démarrer

tello1.takeoff()


# ===== Paramètres vidéo et PID =====
w, h = 640, 480  # Résolution vidéo (largeur x hauteur)
fbRange = [6200, 6800]  # Plage acceptable de la taille du visage (pour juger de la distance)
pid = [0.4, 0.4, 0]  # Coefficients PID : proportionnel, dérivé, intégral
pError = 0  # Erreur précédente (pour le calcul dérivé du PID)

# ===== Initialisation de MediaPipe Face Detection =====
mp_face_detection = mp.solutions.face_detection  # Module de détection de visages
face_detection = mp_face_detection.FaceDetection(
    min_detection_confidence=0.2)  # Initialisation avec une confiance minimale


# ===== Fonction de détection de visage avec MediaPipe =====
def findFace(img):
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Conversion de BGR vers RGB (MediaPipe attend du RGB)
    results = face_detection.process(imgRGB)  # Lancement de la détection

    myFaceListC = []  # Liste des centres de visages détectés
    myFaceListArea = []  # Liste des aires des visages détectés

    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box  # Récupération de la boîte englobante
            ih, iw, _ = img.shape  # Hauteur et largeur de l'image
            x = int(bboxC.xmin * iw)
            y = int(bboxC.ymin * ih)
            w_box = int(bboxC.width * iw)
            h_box = int(bboxC.height * ih)

            # Dessin d'un rectangle autour du visage
            cv2.rectangle(img, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)

            # Calcul du centre du visage
            cx = x + w_box // 2
            cy = y + h_box // 2

            # Calcul de l'aire (utilisée pour estimer la distance)
            area = w_box * h_box

            # Dessin d'un point au centre du visage
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

            # Stockage des coordonnées et de l'aire
            myFaceListC.append([cx, cy])
            myFaceListArea.append(area)

    # Si au moins un visage détecté, retourne celui avec la plus grande aire
    if myFaceListArea:
        i = myFaceListArea.index(max(myFaceListArea))  # Sélection du visage le plus proche
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]  # Aucun visage détecté


# ===== Fonction de suivi du visage =====
def trackFace(info, w, pid, pError):
    area = info[1]  # Aire du visage
    x, y = info[0]  # Coordonnées du centre du visage
    fb = 0  # Mouvement avant/arrière
    error = x - w // 2  # Erreur de position horizontale (par rapport au centre de l'image)

    # Calcul de la vitesse de rotation du drone avec PID (proportionnel + dérivé)
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -100, 100))  # Limite la vitesse à [-100, 100]

    # Gestion de l'avance/recul selon la taille du visage (distance estimée)
    if fbRange[0] < area < fbRange[1]:
        fb = 0  # Bonne distance, ne pas avancer/reculer
    elif area > fbRange[1]:
        fb = -20  # Trop proche, reculer
    elif area < fbRange[0] and area != 0:
        fb = 20  # Trop loin, avancer

    # Si aucun visage détecté, ne pas bouger
    if x == 0:
        speed = 0
        error = 0

    # Envoie de la commande au drone : avancer/reculer et tourner
    tello1.send_rc_control(0, fb, 0, speed)

    return error  # Retourne l’erreur actuelle pour le PID


# ===== Fonction principale de suivi en boucle =====
def start_tracking():

    global pError
    while True:
        img = tello1.get_frame_read().frame  # Récupère une frame depuis la caméra du drone
        img = cv2.resize(img, (w, h))  # Redimensionne l’image

        img, info = findFace(img)  # Détection de visage
        pError = trackFace(info, w, pid, pError)  # Contrôle du drone en fonction du visage

        cv2.imshow('Output', img)  # Affiche l’image annotée

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Quitte avec la touche 'q'
            tello1.land()  # Atterrissage du drone
            break

    cap.release()  # Libère la caméra si utilisée
    cv2.destroyAllWindows()  # Ferme les fenêtres OpenCV


# ===== Lancement du programme principal =====
start_tracking()
