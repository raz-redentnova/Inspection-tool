import cv2
import numpy as np

def sift_similarity_score(img1, img2):
    """
    Compute SIFT-based similarity score between two images (lower = more similar).
    Returns None if no descriptors are found.
    """
    sift = cv2.SIFT_create()
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    kp1, des1 = sift.detectAndCompute(gray1, None)
    kp2, des2 = sift.detectAndCompute(gray2, None)

    if des1 is None or des2 is None or len(kp1) == 0:
        return None

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    good_matches = [m for m, n in matches if m.distance < 0.75 * n.distance]
    score = 1.0 - min(len(good_matches) / max(len(kp1), 1), 1.0)
    return round(score/4, 3)