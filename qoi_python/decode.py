from __future__ import annotations

from struct import unpack
from typing import Any
from typing import Generator

import numpy as np

from utils import index_position, LIST_MAX_SIZE




def QOI_OP_RGBA(chunk: int, pixel_list: list[list[int]], prev_pixel: list[int], data_gen: Generator[int, int, str]) -> tuple[int, int, int, int, int]:
    return (next(data_gen), next(data_gen), next(data_gen), next(data_gen), 1)


def QOI_OP_RGB(chunk: int, pixel_list: list[list[int]], prev_pixel: list[int], data_gen: Generator[int, int, str]) -> tuple[int, int, int, int, int]:
    return (next(data_gen), next(data_gen), next(data_gen), prev_pixel[3], 1)


def QOI_OP_INDEX(chunk: int, pixel_list: list[list[int]], prev_pixel: list[int], data_gen: Generator[int, int, str]) -> tuple[int, int, int, int, int]:
    pixel = pixel_list[chunk]
    return (pixel[0], pixel[1], pixel[2], pixel[3], 1)


def QOI_OP_DIFF(chunk: int, pixel_list: list[list[int]], prev_pixel: list[int], data_gen: Generator[int, int, str]) -> tuple[int, int, int, int, int]:
    return ((prev_pixel[0] + ((chunk >> 4) & 0x03) - 2), (prev_pixel[1] + ((chunk >> 2) & 0x03) - 2), (prev_pixel[2] + (chunk & 0x03) - 2), prev_pixel[3], 1)


def QOI_OP_LUMA(chunk: int, pixel_list: list[list[int]], prev_pixel: list[int], data_gen: Generator[int, int, str]) -> tuple[int, int, int, int, int]:
    dg = (chunk & 0x3f) - 32
    chunk = next(data_gen)
    return (prev_pixel[0] + ((chunk >> 4) & 0x0f) - 8 + dg, prev_pixel[1] + dg, prev_pixel[2] + (chunk & 0x0f) - 8 + dg, prev_pixel[3], 1)


def QOI_OP_RUN(chunk: int, pixel_list: list[list[int]], prev_pixel: list[int], data_gen: Generator[int, int, str]) -> tuple[int, int, int, int, int]:
    return (prev_pixel[0], prev_pixel[1], prev_pixel[2], prev_pixel[3], (chunk & 0x3f) + 1)


def data_gen_func(data: Any) -> Generator[int, int, str]:
    yield from data
    return 'Done'


def is_valid_format(data: bytes) -> bool:
    magic_bytes = data[:4]  # Get the magic bytes
    end_bytes = data[-8:]  # Get the end bytes

    return magic_bytes == b'qoif' and end_bytes == b'\x00\x00\x00\x00\x00\x00\x00\x01'


def decode(path: str) -> np.ndarray:
    with open(path, 'rb') as f:
        data = f.read()

    if not is_valid_format(data):
        raise TypeError('Invalid end bytes')

    width, height, channels, colorspace = unpack('>IIBB', data[4:14])
    print(f'{width}:{height}:{channels}:{colorspace}')

    prev_pixel = [0, 0, 0, 255]  # rgba
    data = data[14:-8]
    data_gen = data_gen_func(data)
    pixel_list = [[0, 0, 0, 0]] * LIST_MAX_SIZE
    img_array = np.zeros([height, width, 4], dtype=np.uint8)
    height_cnt = 0
    width_cnt = 0

    func_dict = {
        0xff: QOI_OP_RGBA,
        0xfe: QOI_OP_RGB,
        0x00: QOI_OP_INDEX,
        0x01: QOI_OP_DIFF,
        0x02: QOI_OP_LUMA,
        0x03: QOI_OP_RUN,
    }

    while True:
        try:
            chunk = next(data_gen)
        except StopIteration:
            break

        func = func_dict[chunk] if chunk == 0xff or chunk == 0xfe else func_dict[(chunk & 0b11000000) >> 6]
        (*prev_pixel, run) = func(chunk, pixel_list, prev_pixel, data_gen)

        pixel_list[index_position(prev_pixel)] = prev_pixel
        for _ in range(run):
            img_array[height_cnt][width_cnt] = prev_pixel
            width_cnt += 1
            if width_cnt == width:
                width_cnt = 0
                height_cnt += 1
    return img_array


if __name__ == '__main__':
    img_array = decode('/home/essamgouda97/Desktop/Projects/qoi-python/data/testcard_rgba.qoi')
    from PIL import Image
    img = Image.fromarray(img_array, 'RGBA')
    img.save('t.png')
