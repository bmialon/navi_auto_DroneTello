from djitellopy import TelloSwarm, Tello
import math
from threading import Thread
import keyboard
import pygame


# ________________________________________________________ DRONE ________________________________________________________
def is_swarm_connected():
    try:
        return swarm
    except:
        return False


def connect_drones():
    global swarm, tellos, drone_index_position, drone_paths, drone_angles, selected_drone
    drone_index_position = {}
    drone_paths = {}  # Store path points for each drone separately
    drone_angles = {}  # Store each drone's current angle separately
    selected_drone = None

    while not is_swarm_connected():
        try:
            swarm = TelloSwarm.fromIps([
                "192.168.137.139",
                "192.168.137.115"
            ])
            swarm.connect()
            tellos = swarm.tellos

            # Initialize positions, paths, and angles for each drone
            for tello in tellos:
                drone_index_position[tello] = 0
                drone_paths[tello] = []
                drone_angles[tello] = 0
                Thread(target=move_drone, args=(tello,), daemon=True).start()

            print("All drones connected!")
            break
        except:
            print("Failed to connect, retrying...")


def emergency_stop():
    while True:
        if keyboard.is_pressed('esc'):
            print("Emergency Stop! Landing...")
            swarm.land()


def takeoff_or_land():
    global isFlying
    if is_swarm_connected():
        if isFlying:
            swarm.land()
            isFlying = False
        else:
            swarm.takeoff()
            isFlying = True


def move_drone(tello):
    while True:
        if is_swarm_connected() and len(drone_paths[tello]) >= 2 and isFlying and drone_index_position[tello]+1 <= len(drone_paths[tello]):
            x_current, y_current = drone_paths[tello][drone_index_position[tello]]
            x_target, y_target = drone_paths[tello][drone_index_position[tello]+1]

            new_angle = calculate_rotation_angle(x_current, y_current, x_target, y_target, drone_angles[tello])
            distance = calculate_distance(x_current, y_current, x_target, y_target)

            if new_angle < 0:
                tello.rotate_counter_clockwise(abs(new_angle))
            else:
                tello.rotate_clockwise(new_angle)
            tello.move_forward(int(distance))

            drone_angles[tello] = drone_angles[tello] + new_angle
            drone_index_position[tello]+=1

def calculate_rotation_angle(x_current, y_current, x_next, y_next, current_angle):
    delta_x = x_next - x_current
    delta_y = y_next - y_current
    target_angle = math.atan2(delta_y, delta_x)
    target_angle_degrees = math.degrees(target_angle)
    rotation_angle = target_angle_degrees - current_angle
    rotation_angle = (rotation_angle + 180) % 360 - 90
    return int(rotation_angle)


def calculate_distance(x_current, y_current, x_next, y_next):
    return math.sqrt((x_next - x_current) ** 2 + (y_next - y_current) ** 2)


# ________________________________________________________ DRAW _________________________________________________________
def draw_room():
    pygame.draw.rect(win, BLACK, room_rect, 5)


def draw_points():
    for tello, path in drone_paths.items():
        for i, point in enumerate(path):
            pygame.draw.circle(win, BLACK, point, 5)
            text_surface = font.render(str(i), True, BLACK)
            win.blit(text_surface, (point[0] + 5, point[1] - 10))


def draw_drones():
    for tello in tellos:
        (x,y) = drone_paths[tello][drone_index_position[tello]]
        win.blit(drone_image, (x, y))


def draw_ui():
    state_led_color = GREEN if is_swarm_connected() else RED
    state_led_text = "Connected" if is_swarm_connected() else "Not Connected"
    pygame.draw.rect(win, state_led_color, state_led_rect, border_radius=5)
    state_text = font.render(state_led_text, True, WHITE)
    win.blit(state_text, (state_led_rect[0] + 12, state_led_rect[1] + state_text.get_height() / 2))

    # Draw drone selection buttons
    for i, tello in enumerate(tellos):
        button_rect = (WIDTH - 150, 100 + i * 60, 100, 50)
        pygame.draw.rect(win, GREEN if selected_drone == tello else BLACK, button_rect)
        button_text = font.render(f"Drone {i + 1}", True, WHITE)
        win.blit(button_text, (button_rect[0] + 15, button_rect[1] + 15))

    # Draw Takeoff/Land button
    pygame.draw.rect(win, BLACK, land_button_rect)
    button_text = font.render("Land" if isFlying else "Take Off", True, WHITE)
    win.blit(button_text, (land_button_rect[0] + 18, land_button_rect[1] + 18))


def handle_ui_click(x, y):
    global selected_drone
    # Check if a drone button is clicked
    for i, tello in enumerate(tellos):
        button_rect = (WIDTH - 150, 100 + i * 60, 100, 50)
        if button_rect[0] <= x <= button_rect[0] + button_rect[2] and button_rect[1] <= y <= button_rect[1] + \
                button_rect[3]:
            selected_drone = tello
            return

    # Check if the takeoff/land button is clicked
    if land_button_rect[0] <= x <= land_button_rect[0] + land_button_rect[2] and land_button_rect[1] <= y <= \
            land_button_rect[1] + land_button_rect[3]:
        takeoff_or_land()

    # If inside room, add point to selected drone
    if selected_drone and room_rect[0] <= x <= room_rect[0] + room_rect[2] and room_rect[1] <= y <= room_rect[1] + room_rect[3]:
        path = drone_paths[selected_drone]
        if len(path) >= 1:
            x_last = path[len(path)-1][0]
            y_last = path[len(path)-1][1]
            if calculate_distance(x_last, y_last, x, y) < 40:
                return

        drone_paths[selected_drone].append((x, y))


def update_interface():
    win.fill(WHITE)
    draw_room()
    draw_points()
    draw_ui()
    pygame.display.update()


# ________________________________________________________ MAIN ________________________________________________________
WIDTH, HEIGHT = 800, 600

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone Control")
font = pygame.font.SysFont(None, 24)

WHITE, BLACK, RED, GREEN = (255, 255, 255), (0, 0, 0), (200, 0, 0), (0, 200, 0)
room_rect, state_led_rect, land_button_rect = (50, 50, WIDTH - 100, HEIGHT - 100), (50, 10, 140, 30), (
WIDTH - 150, HEIGHT - 100, 100, 50)
drone_image = pygame.transform.scale(pygame.image.load('images/drone.png'), (40, 40))

tellos, isFlying, selected_drone, drone_index_position, drone_paths, drone_angles = [], False, None, {}, {}, {}
Thread(target=emergency_stop, daemon=True).start()
Thread(target=connect_drones, daemon=True).start()

while True:
    pygame.time.delay(50)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if isFlying:
                takeoff_or_land()
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_ui_click(*pygame.mouse.get_pos())
    update_interface()
