#  TODO support RGB and RGBA
from __future__ import annotations

from struct import unpack
from typing import Any
from typing import Generator

import numpy as np

LIST_MAX_SIZE = 64


def QOI_OP_INDEX(chunk: int, pixel_list: list[list[int]]) -> list[int]:
    return pixel_list[chunk]


def add_diff(dr: int, dg: int, db: int, prev_pixel: list[int]) -> list[int]:
    r = (prev_pixel[0] + dr)
    g = (prev_pixel[1] + dg)
    b = (prev_pixel[2] + db)
    a = prev_pixel[3]

    return [r, g, b, a]


def QOI_OP_RUN(chunk: Any) -> int:
    return (chunk & 0x3f) + 1


def data_gen_func(data: Any) -> Generator[int, int, str]:
    yield from data
    return 'Done'


def decode(path: str) -> np.ndarray:
    with open(path, 'rb') as f:
        data = f.read()

    magic_bytes = data[:4]  # Get the header bytes
    if magic_bytes != b'qoif':
        raise TypeError('Invalid magic bytes')
    width, height, channels, colorspace = unpack('>IIBB', data[4:14])
    print(f'{width}:{height}:{channels}:{colorspace}')

    end_bytes = data[-8:]  # Get the end bytes
    if end_bytes != b'\x00\x00\x00\x00\x00\x00\x00\x01':
        raise TypeError('Invalid end bytes')

    prev_pixel = [0, 0, 0, 255]  # rgba
    data = data[14:-8]
    data_gen = data_gen_func(data)
    pixel_list = [[0, 0, 0, 0]] * LIST_MAX_SIZE
    img_array = np.zeros([height, width, 4], dtype=np.uint8)
    height_cnt = 0
    width_cnt = 0

    while True:
        try:
            chunk = next(data_gen)
        except StopIteration:
            break
        run = 1
        if chunk == 255:
            r = next(data_gen)
            g = next(data_gen)
            b = next(data_gen)
            a = next(data_gen)
        elif chunk == 254:
            r = next(data_gen)
            g = next(data_gen)
            b = next(data_gen)
            a = prev_pixel[3]
        else:
            tag = (chunk & 0b11000000) >> 6

            if tag == 0:
                r, g, b, a = QOI_OP_INDEX(chunk, pixel_list)
            elif tag == 1:
                dr = ((chunk >> 4) & 0x03) - 2
                dg = ((chunk >> 2) & 0x03) - 2
                db = (chunk & 0x03) - 2
                r, g, b, a = add_diff(dr, dg, db, prev_pixel)
            elif tag == 2:
                dg = (chunk & 0x3f) - 32
                chunk = next(data_gen)
                dr_dg = ((chunk >> 4) & 0x0f) - 8
                db_dg = (chunk & 0x0f) - 8
                dr = dr_dg + dg
                db = db_dg + dg
                r, g, b, a = add_diff(dr, dg, db, prev_pixel)
            elif tag == 3:
                run = QOI_OP_RUN(chunk)
                r, g, b, a = prev_pixel
            else:
                raise TypeError('Invalid chunk')
        prev_pixel = [r, g, b, a]
        pixel_list[index_position(prev_pixel)] = prev_pixel
        for _ in range(run):
            img_array[height_cnt][width_cnt] = [r, g, b, a]
            width_cnt += 1
            if width_cnt == width:
                width_cnt = 0
                height_cnt += 1
    return img_array


def index_position(pixel: list[int]) -> int:
    return (pixel[0] * 3 + pixel[1] * 5 + pixel[2] * 7 + pixel[3] * 11) % LIST_MAX_SIZE


if __name__ == '__main__':
    img_array = decode('/home/essamgouda97/Desktop/Projects/qoi-python/data/testcard_rgba.qoi')
    from PIL import Image
    img = Image.fromarray(img_array, 'RGBA')
    img.save('t.png')
