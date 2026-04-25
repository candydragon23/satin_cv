import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import label, regionprops
from skimage.io import imread
from skimage.morphology import skeletonize
from scipy.ndimage import convolve
from pathlib import Path
save_path = Path(__file__).parent
def count_holes(region):
    shape = region.image.shape
    new_image = np.zeros((shape[0] + 2, shape[1] + 2))
    new_image[1:-1, 1:-1] = region.image
    new_image = np.logical_not(new_image)
    labeled = label(new_image)
    return np.max(labeled) - 1
def count_lines(region):
    shape = region.image.shape
    image = region.image
    vlines = (np.sum(image, 0) / shape[0] == 1).sum()
    hlines = (np.sum(image, 1) / shape[1] == 1).sum()
    return vlines, hlines
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
def count_diagonal_lines(region):
    image = region.image
    h, w = image.shape
    diag1 = sum(image[i, i] for i in range(min(h, w)))
    diag2 = sum(image[i, w-1-i] for i in range(min(h, w)))
    diag3 = sum(image[i, i+1] for i in range(min(h, w)-1) if i+1 < w)
    diag4 = sum(image[i+1, w-1-i] for i in range(min(h, w)-1) if i+1 < h)
    return np.array([diag1, diag2, diag3, diag4]) / min(h, w)
def extractor(region):
    cy, cx = region.centroid_local
    cy /= region.image.shape[0]
    cx /= region.image.shape[1]
    perimeter = region.perimeter / region.image.size
    holes = count_holes(region)
    vlines, hlines = count_lines(region)
    vlines /= region.image.shape[1]
    hlines /= region.image.shape[0]
    eccentricity = region.eccentricity
    aspect = region.image.shape[0] / region.image.shape[1]
    symmetrical = symmetry(region)
    transposed_symmetrical = symmetry(region, transpose = True)
    orientation = region.orientation
    diagonals = count_diagonal_lines(region)
    return np.array([holes, vlines, hlines, symmetrical, transposed_symmetrical, diagonals[0], diagonals[1], diagonals[2], diagonals[3], region.image.shape[1] / region.image.shape[0]])
def classificator(region, templates):
    features = extractor(region)
    result = ''
    min_d = 10 ** 16
    for symbol, t in templates.items():
        d = ((t - features) ** 2).sum() ** 0.5
        if d < min_d:
            result = symbol
            min_d = d
    return result
image = imread('./alphabet-small.png')[:, :, :-1]
template = image.sum(2)
binary = template != 765.
labeled = label(binary)
props = regionprops(labeled)
templates = {}
for region, symbol in zip(props, ['8', 'O', 'A', 'B', '1', 'W', 'X', '*', '/', '-']):
    templates[symbol] = extractor(region)
image = imread('./alphabet.png')[:,:,:-1]
binary_alphabet = image.mean(2) > 0
labeled_alphabet = label(binary_alphabet)
aprops = regionprops(labeled_alphabet)
result = {}
save_path = Path(__file__).parent
image_path = save_path / "out"
image_path.mkdir(exist_ok = True)
plt.ion()
plt.figure(figsize = (5, 7))
for region in aprops:
    symbol = classificator(region, templates)
    if symbol not in result:
        result[symbol] = 0
    result[symbol] += 1
    plt.cla()
    plt.title(f"Class - '{symbol}'")
    plt.imshow(region.image)
    plt.savefig(image_path / f"image_{region.label}.png")
print(result)
plt.imshow(binary_alphabet)
plt.show()