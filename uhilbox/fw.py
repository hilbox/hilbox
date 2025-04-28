import network, time
from microdot import Microdot, Response

class FW:
    """
    Base class that:
     - brings up Wi-Fi
     - provides a Microdot app
     - exposes a .post() decorator
     - runs the server
    """

    def __init__(self, ssid: str, password: str, host: str='0.0.0.0', port: int=80):
        self.ssid     = ssid
        self.password = password
        self.host     = host
        self.port     = port

        Response.default_content_type = 'application/json'
        self.app = Microdot()

    def setup_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(self.ssid, self.password)
        while not wlan.isconnected():
            time.sleep_ms(100)
        print("Wi-Fi up:", wlan.ifconfig())

    def post(self, path: str):
        """
        Decorator for a POST route.
        Usage:
            @self.post('/foo')
            def foo_handler(req): ...
        """
        return self.app.post(path)

    def run(self):
        # 1) bring up Wi-Fi
        self.setup_wifi()
        # 2) start HTTP server
        self.app.run(host=self.host, port=self.port)
