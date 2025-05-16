import json
import serial
from typing import Any, Dict

class Box:
    """
    Generic USB serial client for any HIL box.
    """

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 5.0):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send JSON payload over USB serial and return parsed JSON response.
        The path is ignored in USB mode since we're using direct serial communication.
        """
        # Send the payload as a JSON string followed by newline
        message = json.dumps(payload) + '\n'
        self.serial.write(message.encode())
        
        # Read response until newline
        response = self.serial.readline().decode().strip()
        return json.loads(response)

    def close(self):
        """Close the serial connection"""
        self.serial.close()
