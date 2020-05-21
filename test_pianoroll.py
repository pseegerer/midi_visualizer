import pytest

from pianoroll import Rect


class TestRect:
    @pytest.mark.parametrize("velocity", [
        None, 0, 63, 127
    ])
    def test_velocity_to_color(self, velocity):
        color = Rect.velocity_to_color(velocity)
        print(color)
