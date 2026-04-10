import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import label, regionprops
from skimage.io import imread
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
def classificator(region):
    holes = count_holes(region)
    if holes == 2: #B, 8
        v, h = count_lines(region)
        v /= region.image.shape[1]
        h /= region.image.shape[1]
        symm_h = symmetry(region, transpose = True)
        if v > 0.2 and symm_h < 0.85:
            return 'B'
        else:
            return '8'
    elif holes == 1: #A, 0, P, D
        v_asym = symmetry(region)
        h_asym = symmetry(region, transpose = True)
        v, h = count_lines(region)
        if v_asym > 0.7:
            if v > 0 and h_asym < 0.85:
                return 'D'
            else:
                return '0'
        else:
            if v > 0:
                return 'P'
            else:
                return 'A'
    elif holes == 0: #1, W, X, *, -, /
        if region.image.sum() / region.image.size > 0.95:
            return '-'
        shape = region.image.shape
        aspect = np.min(shape) / np.max(shape)
        v_asym = symmetry(region)
        h_asym = symmetry(region, transpose = True)
        v, h = count_lines(region)
        if aspect > 0.85 and (v > 0 or h > 0):
            return '*'
        if v > 0 and v_asym > 0.75:
            return '1'
        elif v_asym > 0.85:
            return 'X'
        elif h_asym > 0.8:
            return 'W'
        else:
            return '/'
    return "?"
image = imread('./symbols.png')[:, :, :-1]
binary_alphabet = image.mean(2) > 0
labeled_alphabet = label(binary_alphabet)
aprops = regionprops(labeled_alphabet)
result = {}
save_path = Path(__file__).parent
image_path = save_path / "out_tree"
image_path.mkdir(exist_ok = True)
plt.ion()
plt.figure(figsize = (5, 7))
for region in aprops:
    symbol = classificator(region)
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