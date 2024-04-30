# data_to_qr

This is a simple python script that converts text file to QR code(s).

## Usage

### encode

```bash
python encode.py <input_file>
```

### decode

```bash
python decode.py <QR_figure>

# or
ls <all_figures> | xargs -n 1 python decode.py >> <output_file>
```

## Requirements

zlib, qrcode, PIL, pyzbar
