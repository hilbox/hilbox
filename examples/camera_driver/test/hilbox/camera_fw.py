import secrets
from uhilbox import FW
from machine import Pin
from neopixel import NeoPixel

class CameraFW(FW):
    def __init__(self):
        super().__init__()
        self.px = neopixel.NeoPixel(machine.Pin(48), 1)

        @self.rpc           # decorator from FW
        def ping(): return {"pong":True}

        @self.rpc
        def set_color(c):
            if isinstance(c,list) and len(c)==3:
                self.px[0]=tuple(int(x) for x in c); self.px.write()
                return {"ok":True}
            return {"err":"bad color"}

        @self.rpc
        def capture():
            # stub – return dummy data
            return {"img":"<jpeg bytes…>"}

CameraFW().serve()
