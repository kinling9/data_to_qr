#!/usr/bin/env python3
import gzip
import argparse
import base64
import logging
import math
import hashlib
import os
from aztec_code_generator import AztecCode

logging.getLogger().setLevel(logging.INFO)


def get_md5(object):
    md = hashlib.md5()
    if type(object) == str:
        bytes = object.encode("ascii")
    else:
        bytes = object
    md.update(bytes)
    return md.hexdigest()


MAX_TRUNK_CHARS = 2500
MAX_TRUNK_CHARS = 2412
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Compress data and generate QR code")
    parser.add_argument("file", type=str, help="file to compress and encode in QR code")
    args = parser.parse_args()

    # origin_md5 = ''
    with open(args.file, "rb") as f:
        data = f.read()
        # data = bytes(range(256))*20
        # origin_md5 = get_md5(data)
        data_compressed = gzip.compress(data, compresslevel=9)
        logging.info(
            f"After compress: {len(data_compressed)} / {len(data)} ({float(len(data_compressed))/ len(data)})"
        )
        if len(data_compressed) >= (len(data)):
            logging.info("Use Uncompressed Data")
            compressed = 0
        else:
            data = data_compressed
            compressed = 1

        data = base64.b32encode(data).decode("ascii")
        num_trunks = math.ceil(len(data) / MAX_TRUNK_CHARS)
        for i in range(num_trunks):
            logging.info(f"Encoding QrCode.... {i+1} / {num_trunks}")
            payload = data[i * MAX_TRUNK_CHARS : (i + 1) * MAX_TRUNK_CHARS]
            header = f"{args.file} {i} {num_trunks} {compressed} "
            img = AztecCode(header + payload, size=151, compact=False)
            img.save(os.path.join(f"{args.file}-{i}.png"), border=4, module_size=4)
