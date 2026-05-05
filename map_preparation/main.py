import cv2
import numpy as np

# 1. Load the image directly into grayscale
image = cv2.imread('d17-lines.png', cv2.IMREAD_GRAYSCALE)

if image is None:
    print("Error: Could not load image. Check the file path.")
else:
    # 2. Blur the image slightly to smooth out noisy or fuzzy edges
    # The (5, 5) is the blur radius. Increase to (7, 7) if the edges are very rough.
    blurred = cv2.GaussianBlur(image, (1, 1), 0)

    # 3. Apply a Binary Threshold
    # This is the "edge simplification" step. It forces pixels to be pure black (0) 
    # or pure white (255). We use 127 as the middle-ground cutoff.
    # If a pixel is darker than 127, it becomes black. If lighter, it becomes white.
    _, thresholded = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)

    # 4. (Optional) Morphological Close
    # If your walls have tiny holes or sketchy lines, this step fills them in 
    # to make solid barriers for your NetLogo turtles.
    kernel = np.ones((4, 4), np.uint8)
    final_image = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)

    # 5. Save the optimized image
    cv2.imwrite('d17_optimized.png', final_image)
    print("Success! Image saved as d17_optimized.png")