import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import label, regionprops
from skimage.io import imread
from pathlib import Path
save_path = Path(__file__).par
def extractor(region):
    return np.rray([region.area / region.image.size])
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
template = imread('./alphabet-small.png')[:, :, :-1]
print(template.shape)
template = template.sum(2)
binary = template != 765.
labeled = label(binary)
props = regionprops(labeled)
templates = {}
for region, symbol in zip(props, ['8', 'O', 'A', 'B', '1', 'W', 'X', '*', '/', '-']):
    templates[symbol] = extractor(region)
print(templates)
print(classificator(props[0], templates))
image = imread('./alphabet.png')
binary_alphabet = image.mean(2) > 0
labeled_alphabet = labeled(binary_alphabet)
print(np.max(labeled_alphabet))
aprops = regionprops(labeled_alphabet)
result = {}
for region in aprops:
    symbol = classificator(region, templates)
    if symbol not in result:
        result[symbol] = 0
    result[symbol] += 1
print(result)
plt.imshow(binary_alphabet)
plt.show()