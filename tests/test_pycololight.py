import pytest

from pycololight import PyCololight  # pylint: disable=import-error


class TestPyCololight:
    def test_dummy_function(self):
        light = PyCololight()
        assert light.dummy_function() == 1
