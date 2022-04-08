from __future__ import annotations

import numpy as np


def encode_numpy(path: str, data: np.ndarray) -> None:
    pass


if __name__ == '__main__':
    rgb = np.random.randint(low=0, high=255, size=(224, 244, 3)).astype(np.uint8)
    encode_numpy('./test.qoi', rgb)
