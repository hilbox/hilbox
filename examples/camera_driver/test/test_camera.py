import time
import numpy as np
import pytest
from camera import Webcam
from camera_box import CameraBox

# Configuration
SERIAL_PORT = "/dev/ttyUSB0"  # Change this to match your system
LED_DELAY   = 0.3             # seconds to wait after setting colour
TOLERANCE   = 40              # per-channel tolerance for "dominant"

# fixtures
@pytest.fixture(scope="module")
def box() -> CameraBox:
    """Create one CameraBox for all tests."""
    box = CameraBox(SERIAL_PORT)
    yield box
    box.close()  # Ensure connection is closed after tests

@pytest.fixture(scope="module")
def cam() -> Webcam:
    with Webcam(size=(640, 480)) as w:
        yield w

# helpers
def capture_mean(cam: Webcam) -> np.ndarray:
    """Return mean BGR values of a single webcam frame."""
    frame = cam.read()
    return frame.reshape(-1, 3).mean(axis=0)    # shape => (B, G, R)

def assert_dominant(channel_means, dom_idx):
    """
    Assert channel dom_idx is at least TOLERANCE higher than the others.
    dom_idx: 0=B, 1=G, 2=R
    """
    dom_val = channel_means[dom_idx]
    others  = np.delete(channel_means, dom_idx)
    assert np.all(dom_val - others > TOLERANCE), (
        f"Dominant channel not clear enough: {channel_means}"
    )

# tests
def test_led_red(box, cam):
    """LED set to red should yield red-dominant capture."""
    box.set_color([255, 0, 0])
    time.sleep(LED_DELAY)
    mean = capture_mean(cam)           # (B, G, R)
    assert_dominant(mean, dom_idx=2)   # red channel

def test_led_green(box, cam):
    """LED set to green should yield green-dominant capture."""
    box.set_color([0, 255, 0])
    time.sleep(LED_DELAY)
    mean = capture_mean(cam)
    assert_dominant(mean, dom_idx=1)   # green channel

def test_led_off(box, cam):
    """LED off should produce a dark frame."""
    box.set_color([0, 0, 0])
    time.sleep(LED_DELAY)
    mean = capture_mean(cam)
    assert np.all(mean < 30), f"Frame not dark: {mean}"