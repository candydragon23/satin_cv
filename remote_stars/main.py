import numpy as np
import matplotlib.pyplot as plt
import socket
from scipy import ndimage
from skimage.measure import label
host = '84.237.21.36'
port = 5152
def recvall(sock, nbytes):
    data = bytearray()
    while len(data) < nbytes:
        packet = sock.recv(nbytes - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data
def center(image):
    cx = np.mean(np.sum(image[1]))
    cy = np.mean(np.sum(image[0]))
    return (cy, cx)
plt.ion()
plt.figure()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((host, port))
    sock.send(b'124ras1')
    print(sock.recv(10))
    beat = b'nope'
    while beat != b'yep':
        sock.send(b'get')
        bts = recvall(sock, 40002)
        im = np.frombuffer(bts[2: 40002], dtype = 'uint8')
        im = im.reshape(bts[0], bts[1])
        mask = im > 0
        labeled = label(mask)
        centroids = []
        for i in range(1, 3):
            find_mass = labeled == i
            centers = ndimage.center_of_mass(find_mass)[::-1]
            centroids.append(centers)
        dist = round(((centroids[0][0] - centroids[1][0]) ** 2 + (centroids[0][1] - centroids[1][1]) ** 2) ** 0.5, 1)
        sock.send(f'{dist}'.encode())
        print(sock.recv(10))
        plt.clf()
        plt.imshow(im)
        plt.pause(2)
        sock.send(b'beat')
        beat = sock.recv(10)