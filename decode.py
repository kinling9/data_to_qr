#!/usr/bin/env python3
from __future__ import print_function
import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import argparse


def decode(im):
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)

    # Print results
    # for obj in decodedObjects:
    #     print("Type : ", obj.type)
    #     print("Data : ", obj.data, "\n")

    return decodedObjects


# Display barcode and QR code location
def display(im, decodedObjects):

    # Loop over all decoded objects
    for decodedObject in decodedObjects:
        points = decodedObject.polygon

        # If the points do not form a quad, find convex hull
        if len(points) > 4:
            hull = cv2.convexHull(
                np.array([point for point in points], dtype=np.float32)
            )
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = points

        # Number of points in the convex hull
        n = len(hull)

        # Draw the convext hull
        for j in range(0, n):
            cv2.line(im, hull[j], hull[(j + 1) % n], (255, 0, 0), 3)

    # Display results
    cv2.imshow("Results", im)
    cv2.waitKey(0)


def decompress_binary_to_string(binary_data):
    # Convert binary string to bytes
    compressed_data = bytes(
        int(binary_data[i : i + 8], 2) for i in range(0, len(binary_data), 8)
    )

    # Decompress the data
    decompressed_bytes = zlib.decompress(compressed_data)

    # Convert bytes back to string
    original_string = decompressed_bytes.decode("utf-8")

    return original_string


# Main
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Decompress data from QR code")
    parser.add_argument("file", type=str, help="QR code image file")
    args = parser.parse_args()

    # Read image
    im = cv2.imread(args.file)

    decodedObjects = decode(im)
    import zlib

    # print(zlib.decompress(decodedObjects[0].data))
    print(decompress_binary_to_string(decodedObjects[0].data))

    # display(im, decodedObjects)
