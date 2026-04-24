import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import label
from skimage.io import imread
from skimage.color import rgb2hsv
import cv2
image = imread('balls_and_rects.png')
hsv = rgb2hsv(image)
h = hsv[:, :, 0]
circles = []
rectangles = []
for color in np.unique(h):
    if color == 0:
        continue
    binary = (h == color).astype(np.uint8)
    contours, _ = cv2.findContours(binary * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter ** 2)
        if circularity > 0.85:
            circles.append(color)
        else:
            rectangles.append(color)
groups_circ = [[circles[0]]]
groups_rect = [[rectangles[0]]]
delta = 0.05
for i in range(1, len(circles)):
    if abs(circles[i - 1] - circles[i]) < delta:
        groups_circ[-1].append(circles[i]) 
    else:
        groups_circ.append([circles[i]])
for i in range(1, len(rectangles)):
    if abs(rectangles[i - 1] - rectangles[i]) < delta:
        groups_rect[-1].append(rectangles[i]) 
    else:
        groups_rect.append([rectangles[i]])
shapes_total = 0
print('Circles:')
for group in groups_circ:
    shapes_total += len(group)
    print(np.mean(group), len(group))
print('Rectangles:')
for group in groups_rect:
    shapes_total += len(group)
    print(np.mean(group), len(group))
print(f'Total amount of shapes: {shapes_total}')
plt.subplot(121)
plt.imshow(image)
plt.subplot(122)
plt.plot(np.unique(h), 'o')
plt.show()