import cv2
import numpy as np
from pathlib import Path

def clean_floor_plan(img, min_contour_area=400, erosion_kernel_size=5):
    """
    Takes a loaded image array, cleans it using a multi-filter (thickness and area), 
    and returns the binary result.
    """
    # 1. Binarization (Thresholding) and INVERT (walls are white)
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)

    # 2. [NEW] Create kernels for morphological operations.
    # A larger kernel for erosion (5x5 or 7x7) is more aggressive against thin lines.
    erode_kernel = np.ones((erosion_kernel_size, erosion_kernel_size), np.uint8)
    # A slightly smaller kernel for dilation (3x3) restores thickness.
    dilate_kernel = np.ones((3,3), np.uint8)

    # 3. [NEW] Filter by Thickness (Morphological Opening)
    # ERODE shrinks all white objects. Thin lines disappear completely.
    eroded_thresh = cv2.erode(thresh, erode_kernel, iterations=1)
    
    # DILATE restores the thickness of the preserved structural walls.
    opened_thresh = cv2.dilate(eroded_thresh, dilate_kernel, iterations=1)

    # 4. [REFINED] Refine Clutter Filter (by Area)
    # We now find contours in the much cleaner image.
    contours, _ = cv2.findContours(opened_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter by Large Area threshold
    clean_canvas = np.zeros_like(img)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_contour_area: 
            cv2.drawContours(clean_canvas, [cnt], -1, (255), thickness=cv2.FILLED)

    # 5. Optional Dilation to make walls extra prominent for NetLogo agents.
    final_wall_kernel = np.ones((3,3), np.uint8)
    final_walls = cv2.dilate(clean_canvas, final_wall_kernel, iterations=1)

    # 6. Invert back to normal (Black lines, White background)
    return cv2.bitwise_not(final_walls)

def process_and_stack(file_paths, output_filename, target_width=600):
    print(f"Starting upgraded processing on {len(file_paths)} files...")
    processed_floors = []

    for file_path in file_paths:
        if not file_path.exists():
            print(f"Warning: File {file_path} not found. Skipping.")
            continue
            
        print(f"Applying thickness/area filters to {file_path.name}...")
        img = cv2.imread(str(file_path), cv2.IMREAD_GRAYSCALE)
        
        # Clean the noise using the updated multi-filter function.
        clean_img = clean_floor_plan(img, min_contour_area=25, erosion_kernel_size=5)
        
        # Proportional resize for coordination.
        original_height, original_width = clean_img.shape[:2]
        aspect_ratio = original_height / original_width
        new_height = int(target_width * aspect_ratio)
        
        resized_img = cv2.resize(clean_img, (target_width, new_height), interpolation=cv2.INTER_AREA)
        
        processed_floors.append(resized_img)

    if not processed_floors:
        print("No images were processed.")
        return

    # Stack them vertically
    print("Stacking floors vertically...")
    final_stacked_image = cv2.vconcat(processed_floors)
    
    # Save the final NetLogo-ready image
    cv2.imwrite(output_filename, final_stacked_image)
    print(f"\nSuccess! Saved to {output_filename}")
    print(f"Final Image Dimensions: {target_width}px wide by {final_stacked_image.shape[0]}px high.")

# --- Execution ---

if __name__ == "__main__":
    # Base directory relative to this script
    base_dir = Path(__file__).parent
    originals_dir = base_dir / "originals"
    
    # Automatically find and sort files rzut_4, rzut_3, ...
    # We sort alphabetically in reverse to get 4, 3, 2, 1
    files = sorted(originals_dir.glob("rzut_*.png"), reverse=True)
    
    if not files:
        print(f"Error: No rzut_*.png files found in {originals_dir}")
    else:
        process_and_stack(files, "netlogo_environment.png", target_width=600)
