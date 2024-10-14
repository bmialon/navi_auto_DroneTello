import pygame
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Contrôle du Drone avec Trajectoire Numérotée")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Charger et redimensionner l'image du drone
drone_image = pygame.image.load('drone.png')
drone_width, drone_height = 30, 30
drone_image = pygame.transform.scale(drone_image, (drone_width, drone_height))

# Position et vitesse initiales du drone
drone_x, drone_y = WIDTH // 2, HEIGHT // 2
drone_speed = 2

# Liste pour enregistrer les points de la trajectoire
points = []
current_point_index = 0
movement_started = False  # Variable pour contrôler le début du mouvement du drone

# Police pour les numéros
font = pygame.font.SysFont(None, 24)

# Fonction pour déplacer le drone vers un point cible
def move_drone_towards(target_x, target_y):
    global drone_x, drone_y
    
    # Calculer la direction
    dx = target_x - drone_x
    dy = target_y - drone_y
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance != 0:
        # Normaliser la direction et déplacer le drone
        drone_x += drone_speed * (dx / distance)
        drone_y += drone_speed * (dy / distance)

# Fonction pour dessiner les numéros sur les points
def draw_point_numbers():
    for i, point in enumerate(points):
        number_text = font.render(str(i + 1), True, BLACK)
        win.blit(number_text, (point[0] + 10, point[1] - 10))  # Positionner le numéro près du point

# Boucle principale
running = True
while running:
    pygame.time.delay(50)
    
    # Gérer les événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not movement_started:
            # Ajouter un point à la trajectoire lorsqu'on clique avec la souris
            if len(points) < 10:  # Limiter à 10 points
                x, y = pygame.mouse.get_pos()
                points.append((x, y))
            # Commencer le mouvement si 10 points ont été ajoutés
            if len(points) == 10:
                movement_started = True
    
    # Remplir l'écran de blanc
    win.fill(WHITE)
    
    # Dessiner la salle (limites)
    pygame.draw.rect(win, BLACK, (50, 50, WIDTH-100, HEIGHT-100), 5)
    
    # Dessiner les lignes reliant les points de la trajectoire
    if len(points) > 1:
        pygame.draw.lines(win, RED, False, points, 2)
    
    # Déplacer le drone le long de la trajectoire
    if movement_started and current_point_index < len(points):
        target_x, target_y = points[current_point_index]
        move_drone_towards(target_x, target_y)
        
        # Si le drone atteint un point, passer au suivant
        if math.hypot(target_x - drone_x, target_y - drone_y) < drone_speed:
            current_point_index += 1

    # Dessiner les points de la trajectoire et les numéros
    for i, point in enumerate(points):
        pygame.draw.circle(win, BLACK, point, 5)
    
    # Afficher les numéros des points
    draw_point_numbers()

    # Dessiner le drone (image)
    win.blit(drone_image, (drone_x, drone_y))
    
    # Afficher un message si tous les points ne sont pas encore ajoutés
    if len(points) < 10:
        message = font.render("Ajoutez des points (10 nécessaires)", True, BLACK)
        win.blit(message, (WIDTH // 2 - 150, HEIGHT - 30))

    # Rafraîchir l'affichage
    pygame.display.update()

# Quitter Pygame
pygame.quit()
