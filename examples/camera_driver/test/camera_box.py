from hilbox import Box
from typing import Sequence, Dict

class CameraBox(Box):
    """
    HIL client for camera‐specific endpoints.
    """

    def set_color(self, c: Sequence[int]) -> Dict:
        if len(c) != 3 or any(not (0 <= x <= 255) for x in c):
            raise ValueError("color must be three ints 0–255")
        return self.post('/display/color', {'c': list(c)})
