import json
import machine
import time
from typing import Callable, Dict, Any

class FW:
    """
    Base class that:
     - sets up USB serial communication
     - provides an RPC method registration system
     - exposes a .method() decorator
     - runs the message loop
    """

    def __init__(self, uart_id: int = 0, tx_pin: int = 0, rx_pin: int = 1, baudrate: int = 115200):
        self.uart = machine.UART(uart_id, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))
        self.methods: Dict[str, Callable] = {}

    def method(self, name: str):
        """
        Decorator for registering an RPC method.
        Usage:
            @self.method('set_led')
            def set_led(rgb): ...
        """
        def decorator(handler):
            self.methods[name] = handler
            return handler
        return decorator

    def _handle_message(self, message: str) -> Dict[str, Any]:
        """Handle an incoming RPC call"""
        try:
            call = json.loads(message)
            method = call.get('method')
            params = call.get('params', {})
            
            if method not in self.methods:
                return {"error": f"No such method: {method}"}
                
            try:
                result = self.methods[method](**params)
                return {"result": result}
            except Exception as e:
                return {"error": str(e)}
                
        except Exception as e:
            return {"error": f"Invalid message format: {str(e)}"}

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
