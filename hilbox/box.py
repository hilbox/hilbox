import json
import serial
from typing import Any, Dict

class Box:
    """
    Generic RPC client for any HIL box over USB serial.
    """

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 5.0):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)

    def _call(self, method: str, **params) -> Dict[str, Any]:
        """
        Internal method to make RPC calls.
        """
        message = {
            'method': method,
            'params': params
        }
        self.serial.write((json.dumps(message) + '\n').encode())
        
        response = self.serial.readline().decode().strip()
        return json.loads(response)

    def close(self):
        """Close the serial connection"""
        self.serial.close()
