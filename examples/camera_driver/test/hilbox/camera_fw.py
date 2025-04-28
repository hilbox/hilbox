import secrets
from uhilbox import FW
from machine import Pin
from neopixel import NeoPixel

class CameraFW(FW):
    def __init__(self):
        super().__init__(ssid=secrets.SSID,
                         password=secrets.PASSWORD)

        # hardware setup
        self.pixels = NeoPixel(Pin(48, Pin.OUT), 1)
        self.pixels[0] = (0, 0, 0)
        self.pixels.write()

        @self.post('/display/color')
        def set_color(req):
            """
            JSON payload: {"c":[R,G,B]}
            """
            c = req.json.get('c')
            if isinstance(c, list) and len(c) == 3:
                # apply color
                self.pixels[0] = tuple(int(x) for x in c)
                self.pixels.write()
                return {'status': 'OK'}
            return {'status':'ERR', 'error':'invalid color'}, 400


if __name__ == '__main__':
    # instantiate and launch
    CameraFW().run()
