#!/usr/bin/env python3
import zlib
import argparse
import qrcode


def compress_data_with_limit(data, limit):
    compressed_data = []
    start_index = 0
    while start_index < len(data):
        left, right = 1, len(data) - start_index
        while left <= right:
            mid = (left + right) // 2
            compressed_chunk = zlib.compress(data[start_index : start_index + mid])
            binary_data = "".join(format(byte, "08b") for byte in compressed_chunk)
            if len(binary_data) > limit:
                right = mid - 1
            else:
                left = mid + 1

        # Compress data with the optimal chunk size
        chunk = data[start_index : start_index + right]
        compressed_chunk = zlib.compress(chunk)
        binary_data = "".join(format(byte, "08b") for byte in compressed_chunk)
        compressed_data.append(binary_data)
        start_index += right

    return compressed_data


def generate_qr_code(data, name):
    qr = qrcode.QRCode(
        version=40,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress data and generate QR code")
    parser.add_argument("file", type=str, help="file to compress and encode in QR code")
    args = parser.parse_args()

    with open(args.file, "r") as f:
        data = f.read()
        compressed_data = compress_data_with_limit(data.encode("utf-8"), 7093)
        for i, chunk in enumerate(compressed_data):
            generate_qr_code(chunk, f"qr_code_{i}.png")
