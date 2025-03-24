from djitellopy import TelloSwarm
import math
from threading import Thread
import keyboard
import pygame

swarm = swarm = TelloSwarm.fromIps([
    "192.168.137.40",
    "192.168.137.147"
])
swarm.connect()
swarm.takeoff()


#________________________________________________________ DRONE ________________________________________________________
def is_drone_connected():
    try:
        return swarm
    except:
        return False


def connect_drone():
    global swarm
    while not is_drone_connected():
        try:
            swarm = swarm = TelloSwarm.fromIps([
                "192.168.137.88",
                "192.168.137.190"
            ])
            swarm.connect()
            print("Drone connected!")
        except:
            print("Drone is not connected, Retry")

def emergency_stop():
    while True:
        if keyboard.is_pressed('esc'):
            print("Emergency Stop! Landing...")
            swarm.land()

def takeoff_or_land():
    global isFlying
    if is_drone_connected():
        if isFlying:
            swarm.land()
            isFlying = False
        else:
            swarm.takeoff()
            isFlying = True

def move_drone():
    global current_point_index, current_angle, drone_x, drone_y
    while True:
        if is_drone_connected() and len(points) >= 2 and current_point_index < len(points) and isFlying:
            x_current, y_current = points[current_point_index - 1]
            x_target, y_target = points[current_point_index]

            new_angle = calculate_rotation_angle(x_current, y_current, x_target, y_target)
            distance = calculate_distance(x_current, y_current, x_target, y_target)

            if new_angle < 0:
                swarm.rotate_counter_clockwise(abs(new_angle))
            else:
                swarm.rotate_clockwise(new_angle)
            current_angle += new_angle
            swarm.move_forward(int(distance))
            drone_x, drone_y = x_target, y_target
            current_point_index += 1

def calculate_rotation_angle(x_current, y_current, x_next, y_next):
    delta_x = x_next - x_current
    delta_y = y_next - y_current
    target_angle = math.atan2(delta_y, delta_x)
    target_angle_degrees = math.degrees(target_angle)
    rotation_angle = target_angle_degrees - current_angle
    rotation_angle = (rotation_angle + 180) % 360 - 90
    return int(rotation_angle)

def calculate_distance(x_current, y_current, x_next, y_next):
    return math.sqrt((x_next - x_current) ** 2 + (y_next - y_current) ** 2) / 2

def check_click(rect, x, y):
    x_rect = rect[0]
    y_rect = rect[1]
    width_rect = rect[2]
    height_rect = rect[3]
    return x_rect <= x <= (x_rect+width_rect) and y_rect <= y <= (y_rect+height_rect)

def handle_ui_click(x, y):
    if check_click(land_button_rect, x, y):
        takeoff_or_land()
    elif check_click(room_rect, x, y):
        if len(points) > 1:
            x_last = points[len(points)-1][0]
            y_last = points[len(points)-1][1]
            if calculate_distance(x_last, y_last, x, y) < 40:
                return
        points.append([x, y])


#________________________________________________________ DRAW _________________________________________________________
def draw_room():
    pygame.draw.rect(win, BLACK, room_rect, 5)

def draw_points():
    for i, point in enumerate(points):
        pygame.draw.circle(win, BLACK, point, 5)
        text_surface = font.render(str(i + 1), True, BLACK)
        win.blit(text_surface, (point[0] + 5, point[1] - 10))

    if len(points) >= 2:
        pygame.draw.lines(win, BLACK, False, points, 2)
        if current_point_index < len(points) and isFlying:
            active_line = [points[current_point_index-1] , points[current_point_index]]
            pygame.draw.lines(win, RED , False, active_line, 2)

def draw_drone():
    global drone_x, drone_y
    if len(points) == 1:
        drone_x, drone_y = points[0]

    win.blit(drone_image, (drone_x, drone_y))

def draw_ui():
    state_led_color = GREEN if is_drone_connected() else RED
    state_led_text = "Connected" if is_drone_connected() else "Not Connected"
    pygame.draw.rect(win, state_led_color, state_led_rect, border_radius=5)
    state_text = font.render(state_led_text, True, WHITE)
    win.blit(state_text, (state_led_rect[0] + 12, state_led_rect[1] + state_text.get_height()/2))

    pygame.draw.rect(win, BLACK, land_button_rect)
    button_text = font.render("Land" if isFlying else "Take Off", True, WHITE)
    win.blit(button_text, (land_button_rect[0] + 18, land_button_rect[1] + 18))

def update_interface():
    win.fill(WHITE)
    draw_room()
    draw_points()
    draw_ui()
    draw_drone()
    pygame.display.update()


# ________________________________________________________ MAIN ________________________________________________________
WIDTH, HEIGHT = 800, 600

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone Control")
font = pygame.font.SysFont(None, 24)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)

room_rect = (50, 50, WIDTH - 100, HEIGHT - 100)
land_button_rect = (WIDTH - 150, HEIGHT - 100, 100, 50)
state_led_rect = (50, 10, 140, 30)

drone_image = pygame.transform.scale(pygame.image.load('images/drone.png'), (40, 40))
drone_x, drone_y = 0, 0

swarm = None
isFlying = False

points = []
current_angle = 0
current_point_index = 1

Thread(target=emergency_stop, daemon=True).start()
Thread(target=move_drone, daemon=True).start()
Thread(target=connect_drone, daemon=True).start()

while True:
    pygame.time.delay(50)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if isFlying:
                takeoff_or_land()
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            handle_ui_click(x, y)

    update_interface()

swarm.end()