"""===== vision.py - DEBIX Model A track-vision processing =====
***Convert camera images into a track-center offset for steering control.***

Example :
    mask = clean(threshold(preprocess(frame), 110))
    error_px = compute_error(mask)
"""

import cv2
import numpy as np

# ---------------- Parameters ----------------
# Sample three rows and compare observed widths with calibration measurements.
RATIOS = (0.15, 0.35, 0.55)
# Expected track widths; recalibrate while centered on a straight section.
EXPECTED_WIDTHS = {0.15: 489, 0.35: 540, 0.55: 580}   # Re-measure while centered on a straight section.
# Accept widths within plus or minus 25% of the expected value.
TOLERANCE = 0.25                              # ±25% of the expected width.
# Measured offset when the vehicle is centered (zero for this calibration).
CENTER_OFFSET = 0                             # Measured error with the vehicle centered.
# --------------------------------------------

def preprocess(frame, roi_ratio=0.5):
    """Convert a camera frame to a blurred grayscale region of interest."""
    # Reduce color data, smooth noise, and crop away the upper part of the frame.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    h, w = blur.shape
    return blur[int(h * roi_ratio):h, 0:w]

def threshold(gray, thresh):
    """Convert grayscale pixels to a binary mask using the given threshold."""
    # Bright track pixels become white (255); dark boundaries become black (0).
    _, binary = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
    return binary

def clean(mask, ksize=3):
    """Remove small mask noise with morphological opening and closing."""
    # Opening removes small specks; closing fills small gaps in the track mask.
    kernel = np.ones((ksize, ksize), np.uint8)
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)

def find_edges(row, center):
    """Search from the center for the first dark pixel on each side."""
    left = None
    for x in range(center, -1, -1):
        if row[x] == 0:
            left = x
            break
    right = None
    for x in range(center, len(row)):
        if row[x] == 0:
            right = x
            break
    return left, right

def is_width_valid(left_edge, right_edge, expected_width, tol=TOLERANCE):
    """Check whether the detected track width falls within the configured tolerance."""
    return expected_width * (1 - tol) <= (right_edge - left_edge) <= expected_width * (1 + tol)

def analyze_row(mask, r):
    """Return (left, right, track_center, state) for one sampled row.

    State is one of 'ok', 'left', 'right', 'rejected', 'off_track', or 'none'.
    """
    h, w = mask.shape
    image_center = w // 2
    y = int(h * r)
    row = mask[y]
    expected_width = EXPECTED_WIDTHS[r]

    if row[image_center] == 0:
        return None, None, None, "off_track"

    left_edge, right_edge = find_edges(row, image_center)

    if left_edge is not None and right_edge is not None:
        if not is_width_valid(left_edge, right_edge, expected_width):
            return left_edge, right_edge, None, "rejected"
        return left_edge, right_edge, (left_edge + right_edge) / 2, "ok"
    if left_edge is not None:
        return left_edge, None, left_edge + expected_width / 2, "left"
    if right_edge is not None:
        return None, right_edge, right_edge - expected_width / 2, "right"
    return None, None, None, "none"

def compute_error(mask):
    """Average valid track-center offsets from the image reference center."""
    # Positive error means the estimated track center lies right of the reference.
    reference_center = mask.shape[1] // 2 + CENTER_OFFSET
    errors = []
    for r in RATIOS:
        _, _, track_center, _ = analyze_row(mask, r)
        if track_center is not None:
            errors.append(track_center - reference_center)
    if not errors:
        return None
    return float(np.mean(errors))