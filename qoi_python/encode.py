from __future__ import annotations

from struct import pack

import numpy as np
# from utils import index_position
# from utils import LIST_MAX_SIZE


def encode(path: str, data: np.ndarray, colorspace: int = 1) -> bool:
    bytes_array = b''
    # prev_pixel = [0, 0, 0, 255]
    # pixel_list = [[0, 0, 0, 0]] * LIST_MAX_SIZE

    bytes_array += b'qoif'  # start bytes

    width, height, channels = data.shape
    bytes_array += pack('>IIBB', width, height, channels, colorspace)

    bytes_array += b'\x00\x00\x00\x00\x00\x00\x00\x01'  # end bytes

    return True


if __name__ == '__main__':
    img_array = np.random.randint(low=0, high=255, size=(224, 244, 3)).astype(np.uint8)
    raise SystemExit(encode('./test.qoi', img_array))
