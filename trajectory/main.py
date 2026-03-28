import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage
from skimage.measure import label
files = [f"out/h_{i}.npy" for i in range(100)]
trajectories = {}
num = 0
def centroid(image):
    labeled = label(image)
    image_centroids = []
    for i in range(1, 4):
        find_mass = labeled == i
        center = ndimage.center_of_mass(find_mass)
        image_centroids.append(center)
    return image_centroids
image0 = np.load(files[0])
for center in centroid(image0):
    trajectories[num] = [center]
    num += 1
for file in files[1:]:
    used = set()
    image = np.load(file)
    for y, x in centroid(image):
        mindist = 1000
        mindistnum = None
        for num, trajectory in trajectories.items():
            if num in used:
                continue
            prev_y, prev_x = trajectory[-1]
            dist = ((y - prev_y)**2 + (x - prev_x)**2)**0.5
            if dist < mindist:
                mindist = dist
                mindistnum = num
        trajectories[mindistnum].append((y, x))
        used.add(mindistnum)
plt.figure()
for num, point in trajectories.items():
    x = [i[1] for i in point]
    y = [i[0] for i in point]
    plt.plot(x, y, marker='o', linewidth=2, markersize=4)
plt.show()