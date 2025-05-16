from hilbox import Box
from typing import Sequence, Dict

class CameraBox(Box):
    """
    HIL client for camera‐specific endpoints.
    """

    def __init__(self, port: str):
        """
        Parameters
        ----------
        port : str
            Serial port (e.g. '/dev/ttyUSB0' or 'COM3')
        """
        super().__init__(port=port)

    def set_color(self, r: int, g: int, b: int) -> Dict:
        """
        Set the RGB LED color.

        Parameters
        ----------
        r : int
            Red value (0-255)
        g : int
            Green value (0-255)
        b : int
            Blue value (0-255)
        """
        if not all(0 <= x <= 255 for x in (r, g, b)):
            raise ValueError("color values must be 0–255")
        return self._call('set_led', r=r, g=g, b=b)
