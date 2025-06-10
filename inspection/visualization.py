import cv2
import numpy as np

def get_contour_orientation(contour):
    """
    Returns (angle_deg, direction_vector) where:
      - angle_deg: orientation of main axis (in degrees, 0 = right, +CCW)
      - direction_vector: np.array([dx, dy]), normalized main axis direction
    """
    if contour is None or len(contour) < 5:
        return 0.0, np.array([1.0, 0.0])
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return 0.0, np.array([1.0, 0.0])
    mu20 = M["mu20"] / M["m00"]
    mu02 = M["mu02"] / M["m00"]
    mu11 = M["mu11"] / M["m00"]
    angle_rad = 0.5 * np.arctan2(2 * mu11, mu20 - mu02)
    angle_deg = np.degrees(angle_rad)
    direction = np.array([np.cos(angle_rad), np.sin(angle_rad)])
    return angle_deg, direction
