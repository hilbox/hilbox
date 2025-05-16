import json
import machine
import time
from typing import Callable, Dict, Any

class FW:
    """
    Base class that:
     - sets up USB serial communication
     - provides a message handler system
     - exposes a .post() decorator
     - runs the message loop
    """

    def __init__(self, uart_id: int = 0, tx_pin: int = 0, rx_pin: int = 1, baudrate: int = 115200):
        self.uart = machine.UART(uart_id, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))
        self.handlers: Dict[str, Callable] = {}

    def post(self, path: str):
        """
        Decorator for a message handler.
        Usage:
            @self.post('/foo')
            def foo_handler(payload): ...
        """
        def decorator(handler):
            self.handlers[path] = handler
            return handler
        return decorator

    def _handle_message(self, message: str) -> Dict[str, Any]:
        """Handle an incoming JSON message"""
        try:
            payload = json.loads(message)
            # In USB mode, we'll use the first key as the path
            path = next(iter(payload))
            if path in self.handlers:
                response = self.handlers[path](payload[path])
                return response
            return {"error": f"No handler for path: {path}"}
        except Exception as e:
            return {"error": str(e)}

    def run(self):
        """Run the message loop"""
        buffer = ""
        while True:
            if self.uart.any():
                char = self.uart.read(1).decode()
                if char == '\n':
                    # Process complete message
                    response = self._handle_message(buffer)
                    # Send response
                    self.uart.write(json.dumps(response).encode() + b'\n')
                    buffer = ""
                else:
                    buffer += char
            time.sleep_ms(10)  # Small delay to prevent busy waiting
