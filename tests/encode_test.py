from qoi_python.encode import encode
import pytest

@pytest.mark.parametrize("test_data, expected_out", [
    ("", ""),
])
def test_encode(test_data, expected_out):
    assert True