# inspection/video_stream.py

import cv2

def get_usb_camera_index(max_index=5):
    """Find an available USB camera index, returns -1 if not found."""
    for idx in range(max_index):
        cap = cv2.VideoCapture(idx)
        if cap is not None and cap.isOpened():
            cap.release()
            return idx
    return -1

def open_camera(camera_index=None, width=1280, height=720):
    """Open a USB camera by index, or find the first available one."""
    if camera_index is None:
        camera_index = get_usb_camera_index()
    if camera_index == -1:
        raise RuntimeError("No USB camera found.")
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {camera_index}")
    # Optionally set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap

def check_camera_ready(camera_index=None):
    try:
        cap = open_camera(camera_index)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return False, "Camera opened, but failed to read frame."
        return True, f"Camera {camera_index if camera_index is not None else 0} ready. Frame shape: {frame.shape}"
    except Exception as e:
        return False, str(e)

def get_camera_index_and_resolution():
    idx = get_usb_camera_index()
    if idx == -1:
        return None, None
    cap = cv2.VideoCapture(idx)
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        return idx, None
    h, w = frame.shape[:2]
    return idx, (w, h)


def get_usb_camera_index(max_index=5):
    """Find an available USB camera index, returns -1 if not found."""
    for idx in range(max_index):
        cap = cv2.VideoCapture(idx)
        if cap is not None and cap.isOpened():
            cap.release()
            return idx
    return -1

def open_camera(camera_index=None, width=1280, height=720):
    """Open a USB camera by index, or find the first available one."""
    if camera_index is None:
        camera_index = get_usb_camera_index()
    if camera_index == -1:
        raise RuntimeError("No USB camera found.")
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {camera_index}")
    # Optionally set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap

def check_camera_ready(camera_index=None):
    try:
        cap = open_camera(camera_index)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return False, "Camera opened, but failed to read frame."
        return True, f"Camera {camera_index if camera_index is not None else 0} ready. Frame shape: {frame.shape}"
    except Exception as e:
        return False, str(e)

def get_camera_index_and_resolution():
    idx = get_usb_camera_index()
    if idx == -1:
        return None, None
    cap = cv2.VideoCapture(idx)
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        return idx, None
    h, w = frame.shape[:2]
    return idx, (w, h)
