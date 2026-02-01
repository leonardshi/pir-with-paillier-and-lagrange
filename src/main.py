from phe import paillier
from scipy.interpolate import lagrange
import numpy as np


def main(target):
    # rawDataset = [(1, 69), (2, 100), (3, 55), (4, 79), (5, 84), (6, 95), (7, 92), (8, 79), (9, 64), (10, 55)]
    rawDataset = [(80, 69), (81, 100), (82, 55), (90, 79), (100, 2378), (1001, 6239), (323105324, 32324)]

    precision = 100000  # 定点高精度因子，可调

    keys = np.array([k for k, _ in rawDataset])
    keys_min, keys_max = keys.min(), keys.max()
    keys_norm = (keys - keys_min) / (keys_max - keys_min)
    msgs = np.array([int(m * precision) for _, m in rawDataset])

    dataSetPoly = lagrange(keys_norm, msgs)
    markerPoly = np.poly1d(np.poly(keys_norm))
    
    pubKey, privKey = paillier.generate_paillier_keypair(n_length=2048)

    target_norm = (target - keys_min) / (keys_max - keys_min)

    encryptedKeys = []
    for k in range(len(rawDataset)):
        encryptedKeys.append(pubKey.encrypt(target_norm**k))
    
    encryptedResult = sum([c * k for c, k in zip(dataSetPoly.coef[::-1], encryptedKeys)])
    
    encryptedMarkers = []
    for k in range(len(markerPoly.coef)):
        encryptedMarkers.append(pubKey.encrypt(target_norm**k))
    zipedList = [c * k for c, k in zip(markerPoly.coef[::-1], encryptedMarkers)]
    encryptedMarkerResult = sum(zipedList)

    result = privKey.decrypt(encryptedResult)
    marker = privKey.decrypt(encryptedMarkerResult)

    # 高精度定点还原
    result = round(result / precision)
    marker = marker / precision

    print(f"target: {target} marker: {marker} result: {result}")


def get_dataset_poly(raw_dataset):
    keys = np.array([k for k, _ in raw_dataset])
    msgs = np.array([m for _, m in raw_dataset])

    poly = lagrange(keys, msgs)

    return poly


def get_marker_poly(rawDataset):
    keys = np.array([k for k, _ in rawDataset])

    coeffs = np.poly(keys)

    return np.poly1d(coeffs)


if __name__ == "__main__":
    while True:
        arg = input('input target or "end" to quit:')

        if arg == 'end':
            break
        else:
            main(int(arg))
