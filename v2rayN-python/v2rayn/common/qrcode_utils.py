"""QR Code utility functions.

Ported from ServiceLib/Common/QRCodeUtils.cs.
Uses qrcode and Pillow libraries.
"""

from __future__ import annotations

import io

from v2rayn.common.extensions import is_null_or_empty


def gen_qr_code(url: str | None) -> bytes | None:
    """Generate a QR code image as PNG bytes.

    Args:
        url: URL or text to encode

    Returns:
        PNG image bytes or None
    """
    if is_null_or_empty(url):
        return None

    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q

        levels = [ERROR_CORRECT_H, ERROR_CORRECT_Q, ERROR_CORRECT_M, ERROR_CORRECT_L]
        last_error = None

        for level in levels:
            try:
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=level,
                    box_size=20,
                    border=4,
                )
                qr.add_data(url)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                return buffer.getvalue()
            except Exception as ex:
                last_error = ex
                continue

        if last_error:
            raise last_error
    except ImportError:
        pass

    return None


def parse_barcode_from_file(file_name: str | None) -> str | None:
    """Parse a QR code from an image file.

    Args:
        file_name: Path to image file

    Returns:
        Decoded text or None
    """
    import os

    if file_name is None or not os.path.exists(file_name):
        return None

    try:
        from PIL import Image
        from pyzbar.pyzbar import decode

        img = Image.open(file_name)
        results = decode(img)
        if results:
            return results[0].data.decode("utf-8")

        # Try flipped image
        flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
        results = decode(flipped)
        if results:
            return results[0].data.decode("utf-8")
    except ImportError:
        # pyzbar not available, try alternative
        try:
            from PIL import Image

            img = Image.open(file_name)
            return _decode_qr_with_qreader(img)
        except ImportError:
            pass
    except Exception:
        pass

    return None


def parse_barcode_from_bytes(data: bytes | None) -> str | None:
    """Parse a QR code from image bytes.

    Args:
        data: Image bytes

    Returns:
        Decoded text or None
    """
    if data is None:
        return None

    try:
        from PIL import Image
        from pyzbar.pyzbar import decode

        img = Image.open(io.BytesIO(data))
        results = decode(img)
        if results:
            return results[0].data.decode("utf-8")

        # Try flipped
        flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
        results = decode(flipped)
        if results:
            return results[0].data.decode("utf-8")
    except ImportError:
        pass
    except Exception:
        pass

    return None


def _decode_qr_with_qreader(img: object) -> str | None:
    """Alternative QR code reader using qreader library."""
    try:
        import numpy as np
        from qreader import QReader

        reader = QReader()
        img_array = np.array(img)
        results = reader.detect_and_decode(image=img_array)
        if results:
            return results[0]
    except ImportError:
        pass
    return None
