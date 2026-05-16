import cv2
import numpy as np
import json
from pathlib import Path
import random
import os
save_path = Path(__file__).parent
cv2.namedWindow("Image", cv2.WINDOW_GUI_NORMAL)
cv2.namedWindow("Mask", cv2.WINDOW_GUI_NORMAL)
position = [0, 0]
clicked = False
flag = True
lower1 = lower2 = lower3 = lower4 = upper1 = upper2 = upper3 = upper4 = None
lowers = []
uppers = []
color_combination = []
save_state = 0
config_path = save_path / "config.json"
positions = []
def on_click(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at {x}, {y}")
        global position
        global clicked
        position = [x, y]
        clicked = True
cv2.setMouseCallback("Image", on_click)
capture = cv2.VideoCapture(0+cv2.CAP_DSHOW)
while True:
    ret, frame = capture.read()
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    key = cv2.waitKey(50) & 0xFF
    if key == ord("q"):
        break
    if key == ord("1"): # Запись 1го цвета
        save_state = 1
    if key == ord("2"): # Запись 2го цвета
        save_state = 2
    if key == ord("3"): # Запись 3го цвета
        save_state = 3
    if key == ord("4"): # Запись 4го цвета
        save_state = 4
    if key == ord("s"): # Сохранение цветов в файл
        with (save_path / "config.json").open("w") as f:
            json.dump([
                {"lower": None if lower1 is None else lower1.tolist(), "upper": None if upper1 is None else upper1.tolist(), "id": 1},
                {"lower": None if lower2 is None else lower2.tolist(), "upper": None if upper2 is None else upper2.tolist(), "id": 2},
                {"lower": None if lower3 is None else lower3.tolist(), "upper": None if upper3 is None else upper3.tolist(), "id": 3},
                {"lower": None if lower4 is None else lower4.tolist(), "upper": None if upper4 is None else upper4.tolist(), "id": 4}
            ], f)
    if key == ord("l"): # Создание комбинации и загрузка данных о цветах из файла
        if config_path.exists() and os.path.getsize(config_path) != 0:
            with config_path.open("r") as f:
                data = json.load(f)
            lowers = []
            uppers = []
            ids = []
            for entry in data:
                if entry['lower'] is not None and entry['upper'] is not None:
                    lowers.append(np.array(entry['lower'], dtype=np.uint8))
                    uppers.append(np.array(entry['upper'], dtype=np.uint8))
                    ids.append(entry['id'])
            if len(ids) == 4:
                color_combination = ids.copy()
                random.shuffle(color_combination)
    if clicked:
        clicked = False
        color = hsv[position[1], position[0]]
        lower = np.clip(color * 0.9, 0, 255).astype("uint8")
        upper = np.clip(color * 1.1, 0, 255).astype("uint8")
        upper[1] = 255
        upper[2] = 255
        if save_state == 1:
            lower1 = lower
            upper1 = upper
        if save_state == 2:
            lower2 = lower
            upper2 = upper
        if save_state == 3:
            lower3 = lower
            upper3 = upper 
        if save_state == 4:
            lower4 = lower
            upper4 = upper
    detected_objects = []
    if len(lowers) > 0:
        color_ranges = []
        for id in ids:
            color_ranges.append([lowers[id - 1], uppers[id - 1], id]) 
        for low, up, color_id in color_ranges:
                low = np.array(low, dtype=np.uint8)
                up = np.array(up, dtype=np.uint8)
                inr = cv2.inRange(hsv, low, up)
                mask = cv2.morphologyEx(inr, cv2.MORPH_CLOSE, np.ones((5, 5), dtype="u1"))
                cv2.imshow("Mask", mask)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    (x, y), radius = cv2.minEnclosingCircle(contour)
                    if radius > 10:
                        center = (int(x), int(y))
                        cv2.circle(frame, center, int(radius), (0, 255, 255), 4)
                        cv2.circle(frame, center, 5, (0, 0, 255), -1)
                        positions.append(center)
                        if len(positions) > 20:
                            positions.pop(0)
                        for i, position in enumerate(positions[:-1]):
                            cv2.circle(frame, position, i * 2, (0, 0, 100 + 155 / len(positions) * i), -1)
                        detected_objects.append((color_id, center, radius))
    detected_objects.sort(key = lambda x: (x[1][0], x[1][1]))
    detected_sequence = [color_id for color_id, _, _ in detected_objects]
    if len(detected_sequence) == len(color_combination) and len(color_combination) == 4:
        if detected_sequence == color_combination:
            cv2.rectangle(frame, (5, 5), (frame.shape[1] - 5, frame.shape[0] - 5), (0, 255, 0), 5) # Зеленый прямоугольник если правильная комбинация
        else:
            cv2.rectangle(frame, (5, 5), (frame.shape[1] - 5, frame.shape[0] - 5), (0, 0, 255), 5) # Красный прямоугольник если неправильная комбинация
    cv2.imshow("Image", frame)
    if flag and len(color_combination) == 4: # Вывод сгенерированной комбинации
        print(color_combination)
        flag = False
capture.release()
cv2.destroyAllWindows()