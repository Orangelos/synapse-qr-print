from synapse_qr_print.printing import print_png
import pytest
def test_print_png_printer():
    with pytest.raises(Exception):
        print_png(b"Hello, def test print printer", "123456789?")