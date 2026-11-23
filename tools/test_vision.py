"""===== test_vision.py - DEBIX Model A vision debugging utility =====
***Display and interactively tune the camera-based track-detection pipeline.***

Hardware:
    Camera connected to the system (default OpenCV camera index 0).

Example :
    python test_vision.py
    Use q to quit, + / - to adjust the threshold, and s to save a capture.
"""

import cv2
from vision import (preprocess, threshold, clean, compute_error,
                    analyze_row, RATIOS, CENTER_OFFSET)

# Select the OpenCV camera device and lower-frame region used for detection.
CAM_INDEX = 0
ROI_RATIO = 0.5
THRESH = 110

# Debug colors map each track-detection state to an overlay color.
STATE_COLORS = {
    "ok": (0, 255, 0),          # Green: both track edges detected.
    "left": (0, 165, 255),    # Orange: the right edge is estimated.
    "right": (0, 165, 255),    # Orange: the left edge is estimated.
    "rejected": (0, 0, 255),      # Red: detected width is inconsistent.
    "off_track": (255, 0, 255),
    "none": (0, 0, 255),
}

def draw_debug(mask):
    """Render the detection rows, estimated track centers, and state labels on a mask."""
    h, w = mask.shape
    vis = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    cv2.line(vis, (w // 2, 0), (w // 2, h), (255, 0, 0), 1)

    for r in RATIOS:
        y = int(h * r)
        left_edge, right_edge, center, state = analyze_row(mask, r)
        c = STATE_COLORS[state]
        cv2.line(vis, (0, y), (w, y), (0, 255, 255), 1)
        if left_edge is not None:
            cv2.circle(vis, (left_edge, y), 5, (255, 255, 0), -1)
        if right_edge is not None:
            cv2.circle(vis, (right_edge, y), 5, (255, 255, 0), -1)
        if center is not None:
            cv2.circle(vis, (int(center), y), 6, c, -1)
        cv2.putText(vis, state, (10, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, c, 1)
    return vis

def main():
    """Open the camera and run the interactive vision-debugging loop."""
    # Acquire the camera and stop early if it cannot be opened.
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        print("Error: camera unavailable")
        return

    threshold_value = THRESH
    print("q = quit | + / - = threshold | s = save")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # Build the cleaned binary mask and estimate lateral track error.
        roi = preprocess(frame, ROI_RATIO)
        mask = clean(threshold(roi, threshold_value))
        error = compute_error(mask)
        vis = draw_debug(mask)

        if error is None:
            text, c = "Error: UNDETERMINED", (0, 0, 255)
        else:
            direction = "right" if error > 0 else "left"
            text, c = f"Error: {error:+.1f} px ({direction})", (0, 255, 0)
        cv2.putText(vis, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, c, 2)
        cv2.putText(vis, f"Threshold: {threshold_value}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        full = frame.copy()
        y0 = int(frame.shape[0] * ROI_RATIO)
        cv2.rectangle(full, (0, y0), (frame.shape[1] - 1, frame.shape[0] - 1), (0, 255, 0), 2)

        cv2.imshow("Camera", full)
        cv2.imshow("Mask + debug", vis)

        # Handle quit, threshold adjustment, and capture-save commands.
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key in (ord('+'), ord('=')):
            threshold_value = min(255, threshold_value + 5)
        elif key == ord('-'):
            threshold_value = max(0, threshold_value - 5)
        elif key == ord('s'):
            cv2.imwrite("capture_frame.png", frame)
            cv2.imwrite("capture_mask.png", mask)
            print(f"Saved (error = {error}, threshold = {threshold_value})")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()