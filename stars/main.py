import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label
from skimage.morphology import closing, opening, erosion, dilation
image = np.load('./stars.npy')
struct = np.ones((3, 3))
processed = opening(image, footprint=struct)
count_total = label(image).max()
count_non_stars = label(processed).max()
print(f'amount of stars = {count_total - count_non_stars}')
plt.subplot(121)
plt.imshow(image)
plt.subplot(122)
plt.imshow(processed)
plt.show()