import cv2
import numpy as np
from PIL import Image

def open_camera(device_id=0):
    cam = cv2.VideoCapture(device_id)
    return cam

def get_frame(cam):
    ret, frame = cam.read()
    if not ret:
        raise RuntimeError("Failed to capture image from camera.")
    return frame

def load_image_from_file(uploaded_file):
    """Loads a Streamlit-uploaded file as a BGR OpenCV image."""
    uploaded_file.seek(0)
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return img
