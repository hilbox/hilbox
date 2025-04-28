import cv2
from pathlib import Path
from typing import Optional, Tuple

class Webcam:
    def __init__(
        self,
        index: int = 0,
        size: Optional[Tuple[int, int]] = None,
        backend: int = cv2.CAP_ANY,
    ):
        """
        Parameters
        ----------
        index   : ID of the webcam (0 = default)
        size    : (width, height) to request, e.g. (1280, 720). None = driver default.
        backend : OpenCV backend flag; leave CAP_ANY unless you need a specific one.
        """
        self.cap = cv2.VideoCapture(index, backend)
        if not self.cap.isOpened():
            raise IOError(f"Could not open camera index {index}")

        if size:
            w, h = size
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()

    def read(self):
        """
        Grab a single frame. Returns a NumPy array in BGR order.

        Raises
        ------
        RuntimeError if a frame couldn’t be read.
        """
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("Camera read failed")
        return frame

    def save(self, path: str | Path):
        """
        Capture one frame and save it to *path* (format inferred by extension).

        Returns
        -------
        pathlib.Path of the file written.
        """
        frame = self.read()
        path = Path(path).expanduser()
        if not cv2.imwrite(str(path), frame):
            raise RuntimeError(f"Could not write image to {path}")
        return path

    def release(self):
        """Release the VideoCapture resource."""
        if self.cap.isOpened():
            self.cap.release()