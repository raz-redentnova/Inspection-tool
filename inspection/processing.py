import cv2
import numpy as np
from inspection.visualization import get_contour_orientation

def plot_roi_with_contour(
    roi,
    contour,
    status,
    moments=None,
    extra=None,
    metrics_dict=None,
    thresholds=None,
    ref_direction=None,
    show_mirror_check=False,
    upscale_factor=8,
):
    """
    Draws contour, orientation arrow (rotated 180°), metrics, status, and optional mirror warning on the upscaled ROI.
    All annotations are scaled, so they appear naturally sized.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    h, w = roi.shape[:2]
    H, W = h * upscale_factor, w * upscale_factor

    # Create upscaled overlay
    overlay = cv2.resize(roi, (W, H), interpolation=cv2.INTER_LINEAR)

    # Helper to upscale coordinates
    def up(x): return int(x * upscale_factor)

    # Draw all contours if provided (faint yellow)
    if extra and "all_contours" in extra and extra["all_contours"] is not None:
        for cnt in extra["all_contours"]:
            cnt_scaled = (cnt * upscale_factor).astype(np.int32)
            cv2.drawContours(overlay, [cnt_scaled], -1, (0, 255, 255), 1 * upscale_factor // 4)

    # Draw main contour (red)
    mirrored = False
    cx, cy = 0, 0
    direction = np.array([-1.0, 0.0])
    arrow_color = (255, 0, 0)
    mirror_warning = False

    if contour is not None and len(contour) > 0:
        contour_up = (contour * upscale_factor).astype(np.int32)
        cv2.drawContours(overlay, [contour_up], -1, (0, 0, 255), 2 * upscale_factor // 4)

        # Orientation & mirror check
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            angle, direction = get_contour_orientation(contour)

            # Mirror detection
            if show_mirror_check and ref_direction is not None:
                mirrored = np.dot(direction, ref_direction) < 0
                if mirrored:
                    direction = -direction
                    mirror_warning = True
                    arrow_color = (0, 140, 255)
            elif show_mirror_check and ref_direction is None:
                direction = np.array([-1.0, 0.0])

            # Rotate arrow by 180 deg
            direction = -direction

        up_cx, up_cy = up(cx), up(cy)
        length = int(0.2 * min(w, h) * upscale_factor)
        dx, dy = int(length * direction[0]), int(length * direction[1])
        cv2.arrowedLine(
            overlay, (up_cx, up_cy), (up_cx + dx, up_cy + dy),
            arrow_color, max(2, upscale_factor // 2), tipLength=0.15
        )
        cv2.circle(overlay, (up_cx, up_cy), max(4, upscale_factor), (0, 255, 0), -1)

    # Status box (top left)
    color = (0, 200, 0) if status == "OK" else (0, 165, 255) if status == "Suspicious" else (0, 0, 255)
    font_scale = upscale_factor / 8.0    # Scale font for upscaled image
    thickness = max(2, upscale_factor // 3)
    cv2.putText(
        overlay, f"Status: {status}", (up(5), up(5)),
        font, font_scale, color, thickness, cv2.LINE_AA
    )

    # Metrics display
    if metrics_dict and thresholds:
        y_offset = up(10)
        for m, v in metrics_dict.items():
            if v is not None and m in thresholds:
                ok = thresholds[m]["ok"]
                nok = thresholds[m]["nok"]
                m_status = "OK" if v <= ok else "NOK" if v > nok else "Suspicious"
                m_color = (0, 200, 0) if m_status == "OK" else (0, 0, 255) if m_status == "NOK" else (0, 165, 255)
                # cv2.putText(
                #     overlay, f"{m}: {v:.3f} {m_status}",
                #     (up(5), y_offset),
                #     font, font_scale * 0.8, m_color, thickness, cv2.LINE_AA
                # )
                y_offset += up(5)

    # Mirror warning
    if mirror_warning:
        cv2.putText(
            overlay, "MIRRORED - NOK", (up(15), up(h) - up(10)),
            font, font_scale, (0, 0, 255), thickness, cv2.LINE_AA
        )

    return overlay

def is_vertically_mirrored(contour, *, col_window=20, ratio_thresh=1.3):
    """
    Implements your heuristic:

    1.  Find contour points whose x-coordinate lies within
        the `col_window` left-most and right-most pixels.
    2.  For each side, compute the vertical span
        ( max(y) - min(y) ).
    3.  If  left_span / right_span  >  `ratio_thresh`
        ⇒ part is mirrored (left side much “taller”).
    """
    if contour is None or len(contour) == 0:
        return False

    pts = contour.reshape(-1, 2)
    xs  = pts[:, 0]

    left_mask  = xs <= (xs.min() + col_window)
    right_mask = xs >= (xs.max() - col_window)

    if not (left_mask.any() and right_mask.any()):
        return False                        # not enough points

    left_span  = pts[left_mask, 1].ptp()    # ptp = max-min
    right_span = pts[right_mask, 1].ptp()

    # Guard against divide-by-zero
    if right_span == 0:
        return False

    return (left_span / right_span) > ratio_thresh


def load_image_from_file(uploaded_file):
    """Reads a Streamlit-uploaded file into a numpy OpenCV image."""
    # Reset file pointer to start
    uploaded_file.seek(0)
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return img

def crop_center(img, width, height):
    h, w = img.shape[:2]
    cx, cy = w//2, h//2
    x1, y1 = max(0, cx-width//2), max(0, cy-height//2)
    roi = img[y1:y1+height, x1:x1+width]
    return roi, (x1, y1)

def restrict_region_by_contour(roi, contour, pad=40):
    """Returns the subregion of the ROI from the top down to 50 pixels below the highest point of the contour."""
    if contour is not None and len(contour) > 0:
        top_y = np.min(contour[:,0,1])
        end_y = min(top_y + pad, roi.shape[0])
        restricted = roi[0:end_y, :]
        mask = np.zeros_like(roi[:,:,0])
        mask[0:end_y, :] = 255
        return restricted, mask, end_y
    else:
        # If no contour, return the whole ROI
        return roi, np.ones_like(roi[:,:,0])*255, roi.shape[0]

def detect_contour(roi, method="canny", template=None, pad=35):
    gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    contour = None
    mask = None
    extra = {}

    # Initial detection on full ROI
    if method == "canny":
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour = max(contours, key=cv2.contourArea) if contours else np.array([])
        mask = edges
    elif method == "otsu":
        _, edges = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour = max(contours, key=cv2.contourArea) if contours else np.array([])
        mask = edges
    elif method == "template_match":
        # Template must be provided
        if template is None:
            raise ValueError("Template image required for template_match method")
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(roi_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc
        h, w = template_gray.shape
        # Mask for the template area
        mask = np.zeros_like(roi_gray)
        mask[top_left[1]:top_left[1]+h, top_left[0]:top_left[0]+w] = 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour = max(contours, key=cv2.contourArea) if contours else np.array([])
    elif method == "watershed":
        # Watershed segmentation
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.4 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        roi_ws = roi.copy()
        markers = cv2.watershed(roi_ws, markers)
        ws_mask = np.zeros_like(gray, np.uint8)
        ws_mask[markers > 1] = 255
        contours, _ = cv2.findContours(ws_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour = max(contours, key=cv2.contourArea) if contours else np.array([])
        mask = ws_mask

        # === Restrict region by contour (top X pixels, same as other methods) ===
        # Here, X can be a parameter (e.g., pad=35 or from config/UI)
        restricted_roi, restriction_mask, end_y = restrict_region_by_contour(roi, contour, pad=pad)
        gray_restricted = cv2.cvtColor(restricted_roi, cv2.COLOR_RGB2GRAY)
        # Re-run watershed just on restricted region
        _, binary = cv2.threshold(gray_restricted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.4 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        roi_ws_restricted = restricted_roi.copy()
        markers = cv2.watershed(roi_ws_restricted, markers)
        ws_mask_restricted = np.zeros_like(gray_restricted, np.uint8)
        ws_mask_restricted[markers > 1] = 255
        contours, _ = cv2.findContours(ws_mask_restricted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        restricted_contour = max(contours, key=cv2.contourArea) if contours else np.array([])

        return restricted_contour, restriction_mask, extra


    # Restrict region by the found contour (for all but template_match and watershed)
    if method not in ["template_match", "watershed"]:
        restricted_roi, restriction_mask, end_y = restrict_region_by_contour(roi, contour, pad=35)
        gray_restricted = cv2.cvtColor(restricted_roi, cv2.COLOR_RGB2GRAY)
        # Re-detect contour in the restricted region
        if method == "canny":
            edges = cv2.Canny(gray_restricted, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            restricted_contour = max(contours, key=cv2.contourArea) if contours else np.array([])
        elif method == "otsu":
            _, edges = cv2.threshold(gray_restricted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            restricted_contour = max(contours, key=cv2.contourArea) if contours else np.array([])
        else:
            restricted_contour = contour
        return restricted_contour, restriction_mask, extra
    else:
        return contour, mask, extra

