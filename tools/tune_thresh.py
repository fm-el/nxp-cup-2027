"""===== tune.py - DEBIX Model A live image-tuning utility =====
***Preview camera frames and tune the vision threshold with a trackbar.***

Hardware:
    Camera selected by Camera(index=2) in the camera module.

Example :
    python tune.py
    Adjust the Threshold trackbar and press q to quit.
"""

import cv2
import vision as vs
from camera import Camera

WIN_CAM = "Camera"
WIN_GRAY = "Gray Camera"
WIN_MASK = "Mask Camera"

# Select camera 2 and prepare three windows for synchronized previews.
c = Camera(index=2)

cv2.namedWindow(WIN_CAM)
cv2.namedWindow(WIN_GRAY)
cv2.namedWindow(WIN_MASK)
                
# Expose the binary threshold as an interactive trackbar.
cv2.createTrackbar("Threshold", WIN_MASK, 100, 255, lambda x: None)

try: 
    # Start capture; always stop the camera and close windows in finally.
    c.start()
    while True:
    
        frame, ts = c.read()
        if frame is None:
            cv2.waitKey(1)
            continue

        # Apply the current threshold to the processed grayscale frame.
        thresh = cv2.getTrackbarPos("Threshold", WIN_MASK)

        gray = vs.preprocess(frame)
        mask = vs.clean(vs.threshold(gray, thresh))

        cv2.imshow(WIN_CAM, frame)
        cv2.imshow(WIN_GRAY, gray)
        cv2.imshow(WIN_MASK, mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
            
finally:
    c.stop()
    cv2.destroyAllWindows()