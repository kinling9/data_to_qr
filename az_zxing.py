#!/usr/bin/env python3
import gzip
import argparse
import base64
import sys
import logging
import glob
import argparse
from pyzxing import BarCodeReader
import cv2
import numpy as np
from collections import Counter
import os

reader = BarCodeReader()

logging.getLogger().setLevel(logging.INFO)


def binary_az(image_name: str):
    image = cv2.imread(image_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 转为灰度图像

    # change to binary
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    points = np.column_stack(np.where(binary < 255))

    # hard code to fix displace when crop
    x_values = points[:, 0]
    y_values = points[:, 1]

    x_counts = Counter(x_values)
    y_counts = Counter(y_values)

    x_to_remove = {x for x, count in x_counts.items() if count < 20}
    y_to_remove = {y for y, count in y_counts.items() if count < 20}

    filtered_data = np.array(
        [
            point
            for point in points
            if point[0] not in x_to_remove and point[1] not in y_to_remove
        ]
    )
    points = filtered_data

    if points.size != 0:
        # crop the image
        x, y, w, h = cv2.boundingRect(points)

        cropped_image = gray[x : x + w, y : y + h]
        # debuga image
        cv2.imwrite("tmp/crop.png", cropped_image)
        _, binary = cv2.threshold(cropped_image, 127, 255, cv2.THRESH_BINARY)

        h, w = cropped_image.shape
        # suppose input graph using the biggest size of AztecCode, 151x151

        grid_width = w / 151
        grid_height = h / 151
        num_rows, num_cols = [151] * 2

        checkerboard_img = cropped_image.copy()
        for i in range(151):
            start_x = int(np.ceil(i * grid_width))
            cv2.line(checkerboard_img, (start_x, 0), (start_x, h), (0, 0, 0), 1)

        for i in range(151):
            start_y = int(np.ceil(i * grid_height))
            cv2.line(checkerboard_img, (0, start_y), (w, start_y), (0, 0, 0), 1)
        # debug checkerboard image
        cv2.imwrite("tmp/checkerboard_image.png", checkerboard_img)

        result_image = np.zeros((num_rows * 4, num_cols * 4), dtype=np.uint8)

        for row in range(num_rows):
            for col in range(num_cols):
                start_x = int(np.ceil(col * grid_width))
                end_x = int((col + 1) * grid_width)
                start_y = int(np.ceil(row * grid_height))
                end_y = int((row + 1) * grid_height)

                grid = binary[start_y:end_y, start_x:end_x]

                black_pixels = np.sum(grid == 0)
                total_pixels = grid.size
                black_ratio = black_pixels / total_pixels

                grid_value = 0 if black_ratio > 0.5 else 255

                start_x_4 = col * 4
                start_y_4 = row * 4
                result_image[start_y_4 : start_y_4 + 4, start_x_4 : start_x_4 + 4] = (
                    grid_value
                )
        # result images
        cv2.imwrite(f"tmp/{image_name}.png", result_image)


parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="+")
arguments = parser.parse_args()
matched_files = []
for file in arguments.files:
    if glob.escape(file) != file:
        # -> There are glob pattern chars in the string
        matched_files.extend(glob.glob(file))
    else:
        matched_files.append(file)

args = parser.parse_args()
# print(matched_files)
data = {}
os.makedirs("tmp", exist_ok=True)

for image_name in matched_files:
    logging.info(f"Parsing Imamge: {image_name}")
    binary_az(image_name)
    reader = BarCodeReader()
    result = reader.decode(f"tmp/{image_name}.png")
    result = result[0]["raw"]
    trunk = result.split(b" ")
    filename = trunk[0].decode("ascii")
    trunk_index = int(trunk[1].decode("ascii"))
    trunk_number = int(trunk[2].decode("ascii"))
    file_compressed = int(trunk[3].decode("ascii"))
    logging.info(
        f"Reading {filename} ({trunk_index} / {trunk_number}) Compressed: {file_compressed}"
    )
    trunk_payload = trunk[4]
    if not filename in data:
        data[filename] = {}
    if not "payloads" in data[filename]:
        data[filename]["payloads"] = [None] * trunk_number
    data[filename]["payloads"][trunk_index] = trunk_payload
    data[filename]["trunk_number"] = trunk_number
    data[filename]["compressed"] = file_compressed
# print(data)

for filename, v in data.items():
    logging.info(f"Restoring file: {filename}")
    if not "raw_data" in v:
        v["raw_data"] = b""
    missing_trunks = set()
    for i in range(v["trunk_number"]):
        payload = v["payloads"][i]
        if payload is None:
            logging.error(f"Missing Trunk: {filename} , trunk {i}")
            missing_trunks.add(i)
            continue
    if len(missing_trunks) == 0:
        raw_data = b"".join(v["payloads"])
        raw_data = base64.b32decode(raw_data)
        print(v["compressed"])
        if v["compressed"] == 1:
            data = gzip.decompress(raw_data)
        else:
            data = raw_data
        with open(filename, "wb") as f:
            f.write(data)
        logging.info(f"Writed file: {filename}")
