import numpy as np
import cv2
import pyautogui
import time
import keyboard
from math import dist
from skimage.measure import label, regionprops
from skimage.morphology import closing
from mss import MSS

# Остановка программы при нажатии на 'q'
running = True
def stop_program():
    global running
    print(curr_time - prev_time)
    running = False

# Прыжок
def hold_key(key, duration=1, interval=0.01):
    start_time = time.time()
    while time.time() - start_time < duration:
        pyautogui.press(key)
        time.sleep(interval)

def symmetry(region, transpose = False):
    image = region.image
    if transpose:
        image = image.T
    shape = image.shape
    top = image[:shape[0] // 2]
    if shape[0] % 2 != 0:
        bottom = image[shape[0] // 2 + 1:]
    else:
        bottom = image[shape[0] // 2:]
    bottom = bottom[::-1]
    result = bottom == top
    return result.sum() / result.size

# Сворачивает vs code и запускает игру (должно быть открыто окно с игрой)
keyboard.add_hotkey('q', stop_program)
pyautogui.moveTo(1800, 10)
pyautogui.click()
time.sleep(1)
pyautogui.moveTo(960, 400)
pyautogui.press('home')
time.sleep(0.2)
pyautogui.click()
pyautogui.press('space')
time.sleep(1)

prev_time = time.time() # Для контроля скорости
action_distance = 137 # Максимальное расстояние для прыжка
sleep_time = 0.4 # Время пригибания
t = 20 # Для контроля скорости
sleep_time_decrease = 0 # Уменьшение времени пригибания на высоких скоростях

with MSS() as sct:
    while running:
        curr_time = time.time()
        time_difference = curr_time - prev_time
        if t <= 150: # Контроль скорости динозавра
            if time_difference // t > 0 and t < 50:
                action_distance += 15
                t += 15
            elif time_difference // t > 0 and t < 100:
                action_distance += 25
                t += 15
            elif time_difference // t > 0 and t <= 150:
                action_distance += 20
                t += 25
                sleep_time = 0.4 - sleep_time_decrease
                sleep_time_decrease += 0.03
        monitor = {"top": 260, "left": 600, "width": 800, "height": 140} # Настраивание захватываемой области здесь
        output = "screen.png".format(**monitor)
        sct_img = sct.grab(monitor) # Взятие экрана
        image = np.array(sct_img)[:, :, :3]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        closed = closing(binary, footprint = np.ones((3, 3)))
        inverted = cv2.bitwise_not(closed)
        labeled = label(inverted)
        props = regionprops(labeled)
        props_centroids = [prop.centroid for prop in props]
        sorted_props = sorted(props, key = lambda x: x.centroid[1])
        sorted_centroids = sorted(props_centroids, key = lambda x: x[1]) # Ищет центроиды всех препятствий на экране и сортирует их
        if len(sorted_centroids) > 9: # Перезапуск игры
            action_distance = 137
            sleep_time = 0.4
            t = 20
            sleep_time_decrease = 0
            print(curr_time - prev_time)
            prev_time = curr_time
            pyautogui.moveTo(960, 400)
            pyautogui.press('home')
            time.sleep(0.4)
            pyautogui.click()
        if len(sorted_centroids) > 1 and sorted_centroids[0][0] >= 80 : # Игнорирует птеродактелей под которыми можно просто пробежать
            dino = sorted_centroids[0]
            closest_obstacle = sorted_centroids[1]
            symm = symmetry(sorted_props[1], True)
            if len(sorted_centroids) > 2: # Поиск самого дальнего кактуса из куч по 2-4 кактуса
                i = 2
                obstacle_1 = closest_obstacle
                obstacle_2 = sorted_centroids[i]
                furthest_obstacle = []
                while dist(obstacle_1, obstacle_2) < 50:
                    furthest_obstacle = obstacle_2
                    obstacle_1 = obstacle_2
                    i += 1
                    try:  
                        obstacle_2 = sorted_centroids[i]
                    except IndexError:
                        break
                if len(furthest_obstacle) > 0:
                    closest_obstacle = furthest_obstacle
            distance = dist(dino, closest_obstacle) # Поиск расстояния между динозавром и ближайшим препятствием
            if closest_obstacle[0] >= 65: # Игнорирует птеродактелей под которыми можно просто пробежать
                if distance < action_distance and closest_obstacle[0] < 110: # Пригибается под птеродактелями
                    pyautogui.keyDown('down')
                    time.sleep(sleep_time)
                    pyautogui.keyUp('down')
                elif distance < action_distance: # Прыгает через препятствия
                    if symm < 0.6 and distance > action_distance / 1.5:
                        time.sleep(0.05)
                    hold_key('space', 0.2, 0.02)
                    pyautogui.keyDown('down')
                    time.sleep(0.03)
                    pyautogui.keyUp('down')