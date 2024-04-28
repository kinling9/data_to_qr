#!/usr/bin/env python3
import zlib

data = "TEST"
data = data * 4096


# data = "123"
def compress_string_to_binary(string):
    # Convert string to bytes
    string_bytes = string.encode("utf-8")

    # Compress the string
    compressed_data = zlib.compress(string_bytes)

    # Convert compressed data to binary
    binary_data = "".join(format(byte, "08b") for byte in compressed_data)

    return binary_data


import qrcode

qr = qrcode.QRCode(
    version=40,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(compress_string_to_binary(data))
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("bible.png")
