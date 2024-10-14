import math
from djitellopy import Tello
from threading import Thread
import keyboard
import pygame


def calculate_rotation_angle(x_current, y_current, x_next, y_next):
    delta_x = x_next - x_current
    delta_y = y_next - y_current

    target_angle = math.atan2(delta_y, delta_x)
    target_angle_degrees = math.degrees(target_angle)

    rotation_angle = target_angle_degrees - current_angle
    rotation_angle = (rotation_angle + 180) % 360 - 180

    return int(rotation_angle)


def calculate_distance(x_current, y_current, x_next, y_next):
    distance = math.sqrt((x_next - x_current) ** 2 + (y_next - y_current) ** 2)
    return distance


def emergency_stop():
    while True:
        if keyboard.is_pressed('esc'):
            print("Emergency Stop! Landing...")
            tello.land()
            pygame.quit()
            quit()

def takeoff_drone():
    global isFlying
    tello.takeoff()
    isFlying = True

def move_drone():
    global current_point_index, current_angle

    while True:
        if len(points) >= 2 and current_point_index < len(points) and isFlying:
            x_current, y_current = points[current_point_index - 1]
            x_target, y_target = points[current_point_index]

            new_angle = calculate_rotation_angle(x_current, y_current, x_target, y_target)
            distance = calculate_distance(x_current, y_current, x_target, y_target)

            # Rotate the drone
            if new_angle < 0:
                tello.rotate_counter_clockwise(abs(new_angle))
            else:
                tello.rotate_clockwise(new_angle)

            current_angle += new_angle

            tello.move_forward(int(distance))

            current_point_index += 1


def draw_point_numbers():
    for i, point in enumerate(points):
        number_text = font.render(str(i + 1), True, BLACK)
        win.blit(number_text, (point[0] + 10, point[1] - 10))



#######################################################################################################################
# Tello init
tello = Tello()
tello.connect()

isFlying = False

# Interface Init
pygame.init()

WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Contrôle du Drone avec Trajectoire Numérotée")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

drone_image = pygame.image.load('drone.jpg')
drone_width, drone_height = 30, 30
drone_image = pygame.transform.scale(drone_image, (drone_width, drone_height))

drone_x, drone_y = 0, 0
drone_speed = 2

points = []
current_angle = 0
current_point_index = 0

font = pygame.font.SysFont(None, 24)

########################################################### Open Threads

emergency_thread = Thread(target=emergency_stop)
emergency_thread.daemon = True
emergency_thread.start()

drone_movement_thread = Thread(target=move_drone)
drone_movement_thread.daemon = True
drone_movement_thread.start()

drone_takeoff_thread = Thread(target=takeoff_drone)
drone_takeoff_thread.daemon = True

print(tello.get_battery())

###################################################### Graphics
if tello.get_battery() > 10:
    while True:
        pygame.time.delay(50)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                points.append((x, y))
                if len(points) == 1:
                    drone_x, drone_y = x, y
                    drone_takeoff_thread.start()
                    current_point_index += 1
                print(points)
                print(points[current_point_index-1])

        win.fill(WHITE)
        pygame.draw.rect(win, BLACK, (50, 50, WIDTH - 100, HEIGHT - 100), 5)

        for i, point in enumerate(points):
            pygame.draw.circle(win, BLACK, point, 5)

        draw_point_numbers()

        if len(points) >= 2:
            pygame.draw.lines(win, RED, False, points, 2)

        win.blit(drone_image, (drone_x, drone_y))
        pygame.display.update()
