from __future__ import annotations

import numpy as np
import pytest

from qoi_python.encode import encode


@pytest.mark.parametrize(
    'test_data, expected_out', [
        ('', ''),
    ],
)
def test_encode(test_data, expected_out):
    rgb = np.random.randint(low=0, high=255, size=(224, 244, 3)).astype(np.uint8)
    encode('./test.qoi', rgb)
    assert True
