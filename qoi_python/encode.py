from __future__ import annotations

from struct import pack

import numpy as np
from utils import index_position
from utils import LIST_MAX_SIZE
from utils import QOI_MAGIC
from utils import QOI_OP_DIFF
from utils import QOI_OP_INDEX
from utils import QOI_OP_LUMA
from utils import QOI_OP_RGB
from utils import QOI_OP_RGBA
from utils import QOI_OP_RUN
from utils import QOI_PADDING
from utils import QOI_PIXELS_MAX


def encode(path: str, data: np.ndarray = None, colorspace: int = 1) -> bool:
    pixel_list = [[0, 0, 0, 0]] * LIST_MAX_SIZE
    height, width, channels = data.shape

    if data is None or width == 0 or height == 0 or channels > 4 or channels < 3 or colorspace > 1 or height >= QOI_PIXELS_MAX / width:
        raise TypeError(fr'Invalid data: {data}, {width},{height}, {channels}, {colorspace}, {QOI_PIXELS_MAX / width}')

    bytes_array = QOI_MAGIC  # start bytes
    bytes_array += pack('>IIBB', width, height, channels, colorspace)  # meta data

    run = 0
    prev_pixel = [0, 0, 0, 255]

    for y in range(height):
        for x in range(width):
            pixel = data[y, x]

            # QOI_OP_INDEX
            if (pixel == prev_pixel).all():
                run += 1
                if run == 62:
                    bytes_array += pack('>B', QOI_OP_RUN | (run - 1))
                    run = 0
            else:
                if run > 0:
                    bytes_array += pack('>B', QOI_OP_RUN | (run - 1))
                    run = 0

                index_pos = index_position(pixel)

                if (pixel_list[index_pos] == pixel).all():
                    bytes_array += pack('>B', QOI_OP_INDEX | index_pos)
                else:
                    pixel_list[index_pos] = pixel

                    if pixel[3] == prev_pixel[3]:
                        vr = pixel[0] - prev_pixel[0]
                        vg = pixel[1] - prev_pixel[1]
                        vb = pixel[2] - prev_pixel[2]

                        vg_r = vr - vg
                        vg_b = vb - vg

                        if vr > -3 and vr < 2 and vg > -3 and vg < 2 and vb > -3 and vb < 2:
                            bytes_array += pack('>B', QOI_OP_DIFF | ((vr + 2) << 4) | ((vg + 2) << 2) | (vb + 2))
                        elif vg_r > -9 and vg_r < 8 and vg > -33 and vg < 32 and vg_b > -9 and vg_b < 8:
                            bytes_array += pack('>B', QOI_OP_LUMA | (vg + 32))
                            bytes_array += pack('>B', ((vg_r + 8) << 4) | (vg_b + 8))
                        else:
                            bytes_array += pack('>B', QOI_OP_RGB)
                            bytes_array += pack('>BBB', pixel[0], pixel[1], pixel[2])
                    else:
                        bytes_array += pack('>B', QOI_OP_RGBA)
                        bytes_array += pack('>BBBB', pixel[0], pixel[1], pixel[2], pixel[3])
            prev_pixel = pixel

    bytes_array += QOI_PADDING  # end bytes

    with open(path, 'wb') as f:
        f.write(bytes_array)

    return False


if __name__ == '__main__':
    from PIL import Image
    from numpy import asarray
    img = Image.open('./t.png')
    img_array = asarray(img)
    raise SystemExit(encode('./test.qoi', img_array))
