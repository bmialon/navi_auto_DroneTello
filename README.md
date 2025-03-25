Projet de Contrôle de Drones Tello
Ce projet regroupe plusieurs scripts Python permettant de contrôler un ou plusieurs drones DJI Tello, pour :
- du suivi de visage
- du contrôle de trajectoire
- la gestion d’un essaim de drones, synchronisé ou non


detectionmediapipe.py -> Le drone détecte et suit un visage en temps réel avec MediaPipe.
trajectory.py -> Interface graphique pour dessiner une trajectoire et faire suivre un drone.
essaim_sync.py -> Tous les drones suivent le même chemin de manière synchronisée.
essaim_unsync.py -> Chaque drone suit sa propre trajectoire, de façon indépendante.

installer.bat -> Contient toutes les bibliothèques à installer.
