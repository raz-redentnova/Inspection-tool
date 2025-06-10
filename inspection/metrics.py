import cv2
import numpy as np
from .sift_similarity import sift_similarity_score

def clamp01(x):
    return max(0.0, min(1.0, x))

def get_rotation_angle(contour):
    """Returns the orientation angle (degrees) of the contour's major axis."""
    if contour is None or len(contour) < 5:
        return 0.0
    (center, axes, angle) = cv2.fitEllipse(contour)
    return angle

def rotate_contour(contour, angle_deg, center=None):
    """Rotate contour by angle (deg) around centroid or supplied center."""
    if contour is None or len(contour) == 0:
        return contour
    if center is None:
        M = cv2.moments(contour)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])) if M["m00"] != 0 else (0, 0)
    contour = contour.squeeze()
    angle_rad = np.deg2rad(angle_deg)
    R = np.array([[np.cos(angle_rad), -np.sin(angle_rad)],
                  [np.sin(angle_rad),  np.cos(angle_rad)]])
    contour_rot = ((contour - center) @ R.T) + center
    return contour_rot.reshape(-1, 1, 2).astype(np.int32)

def rotation_invariant_moments(contour):
    """Return rotation-normalized (mirroring-sensitive) central moments, scale-normalized."""
    if contour is None or len(contour) < 5:
        return np.zeros(7)
    angle = get_rotation_angle(contour)
    M = cv2.moments(contour)
    center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])) if M["m00"] != 0 else (0, 0)
    contour_rot = rotate_contour(contour, -angle, center=center)
    M_rot = cv2.moments(contour_rot)
    vec = np.array([
        M_rot["mu20"], M_rot["mu11"], M_rot["mu02"],
        M_rot["mu30"], M_rot["mu21"], M_rot["mu12"], M_rot["mu03"]
    ])
    norm = np.linalg.norm(vec) + 1e-8
    return vec / norm

def rotation_invariant_moment_distance(contour, reference_moments):
    if contour is None or len(contour) < 5 or reference_moments is None:
        return None
    vec = rotation_invariant_moments(contour)
    # Scaled L2 distance to force [0, 1] range
    return float(np.linalg.norm(vec - reference_moments) / 4)


def compute_fourier_descriptor(contour, degree=32, rotation_align=True):
    """Return normalized, truncated Fourier descriptor for a contour (optionally with rotation alignment)."""
    if contour is None or len(contour) == 0:
        return np.zeros(degree)
    pts = contour.squeeze()
    if len(pts.shape) < 2 or pts.shape[0] < degree:
        return np.zeros(degree)
    # Align to major axis (rotation invariance)
    if rotation_align and len(contour) >= 5:
        angle = get_rotation_angle(contour)
        M = cv2.moments(contour)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])) if M["m00"] != 0 else (0, 0)
        pts = rotate_contour(contour, -angle, center=center).squeeze()
    pts_complex = pts[:, 0] + 1j * pts[:, 1]
    fd = np.fft.fft(pts_complex)
    fd = np.abs(fd)[:degree]
    fd /= (fd[1] + 1e-8)
    fd /= (np.linalg.norm(fd) + 1e-8)
    return fd

def fourier_distance(contour, reference_fd):
    fd = compute_fourier_descriptor(contour)
    if reference_fd is None or fd.shape != reference_fd.shape:
        return None
    return float(np.linalg.norm(fd - reference_fd))

def compute_metrics(contour, roi, reference_contour=None, reference_moments=None, reference_fd=None, reference_roi=None):

    sift_score = None
    if roi is not None and reference_roi is not None:
        try:
            sift_score = sift_similarity_score(roi, reference_roi)
        except Exception as e:
            sift_score = None

    if contour is None or len(contour) == 0:
        return {
            "shape_score": None,
            "rotinv_moment_dist": None,
            "fourier_dist": None,
            "centroid": (0, 0),
            "orientation": None,
            "raw_moments": {},
            "sift_score": sift_score
        }
    M = cv2.moments(contour)
    cx = int(M["m10"] / M["m00"]) if M["m00"] != 0 else 0
    cy = int(M["m01"] / M["m00"]) if M["m00"] != 0 else 0
    angle = get_rotation_angle(contour) if len(contour) >= 5 else None
    shape_score = None
    if reference_contour is not None and len(reference_contour) > 0:
        shape_score = cv2.matchShapes(contour, reference_contour, cv2.CONTOURS_MATCH_I1, 0)
    rotinv_moment_dist = rotation_invariant_moment_distance(contour, reference_moments) if reference_moments is not None else None
    fourier_dist = fourier_distance(contour, reference_fd) if reference_fd is not None else None
    return {
        "shape_score": shape_score,
        "rotinv_moment_dist": rotinv_moment_dist,
        "fourier_dist": fourier_dist,
        "centroid": (cx, cy),
        "orientation": angle,
        "raw_moments": {k: M[k] for k in M},
        "sift_score": sift_score
    }

def classify_alignment(metrics, selected_metrics, thresholds):
    status_list = []
    for m in selected_metrics:
        v = metrics.get(m)
        if v is None:
            continue
        ok = thresholds[m]['ok']
        nok = thresholds[m]['nok']
        # All these metrics: lower is better
        if v <= ok:
            status_list.append('OK')
        elif v > nok:
            status_list.append('NOK')
        else:
            status_list.append('Suspicious')
    if "NOK" in status_list:
        return "NOK"
    elif "Suspicious" in status_list:
        return "Suspicious"
    else:
        return "OK"

def sift_similarity_score(img1, img2):
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY), None)
    kp2, des2 = sift.detectAndCompute(cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY), None)
    if des1 is None or des2 is None:
        return None
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good = [m for m, n in matches if m.distance < 0.75 * n.distance]
    score = 1.0 - min(len(good) / max(len(kp1), 1), 1.0)
    return round(score, 3)

def is_mirrored_direction(test_direction, ref_direction):
    """
    Returns True if test direction is mirrored relative to reference.
    """
    return np.dot(test_direction, ref_direction) < 0

