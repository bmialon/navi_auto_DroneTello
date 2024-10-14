import math
from djitellopy import Tello
from threading import Thread
import keyboard

def calculate_rotation_angle(x_current, y_current, x_next, y_next, current_angle):
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
        if keyboard.is_pressed('esc'):  # If Escape key is pressed
            print("Emergency Stop! Landing...")
            tello.land()
            tello.end()
            quit()


tello = Tello()
tello.connect()

emergency_thread = Thread(target=emergency_stop)
emergency_thread.daemon = True
emergency_thread.start()

tello.takeoff()

# rotation_angle = calculate_rotation_angle(x_current, y_current, x_next, y_next, current_angle)
# distance = calculate_distance(x_current, y_current, x_next, y_next)
#
# if rotation_angle < 0:
#     tello.rotate_counter_clockwise(abs(rotation_angle))
# else:
#     tello.rotate_clockwise(rotation_angle)
# tello.move_forward(int(distance))
