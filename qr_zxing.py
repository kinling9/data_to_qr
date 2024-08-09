#!/usr/bin/env python3
import gzip
import argparse
import base64
import sys
import logging
import glob
import argparse
from pyzxing import BarCodeReader

reader = BarCodeReader()

logging.getLogger().setLevel(logging.INFO)


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

for image_name in matched_files:
    logging.info(f"Parsing Imamge: {image_name}")
    # if image.mode == 'RGBA':
    #     white_bg = Image.new('RGBA', image.size, (255, 255, 255))
    #     image = Image.alpha_composite(white_bg, image)
    # image = image.convert('L') # L = greyscale
    # pix = numpy.array(image)
    reader = BarCodeReader()
    result = reader.decode(image_name)
    print(result)
    result = result[0]["raw"]
    trunk = result.split(b"\n")
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
        raw_data = base64.a85decode(raw_data)
        print(v["compressed"])
        if v["compressed"] == 1:
            data = gzip.decompress(raw_data)
        else:
            data = raw_data
        with open(filename, "wb") as f:
            f.write(data)
        logging.info(f"Writed file: {filename}")
