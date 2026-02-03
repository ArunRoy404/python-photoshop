# analyze_warp.py
import cv2
import numpy as np
from PIL import Image

def analyze_distortion(original_grid, photoshopped_output):
    """Compare original grid with warped result to calculate transformation"""
    # Convert to grayscale
    orig_gray = cv2.cvtColor(np.array(original_grid), cv2.COLOR_RGB2GRAY)
    warp_gray = cv2.cvtColor(np.array(photoshopped_output), cv2.COLOR_RGB2GRAY)
    
    # Find grid intersection points in original
    # Using corner detection
    corners = cv2.goodFeaturesToTrack(orig_gray, 100, 0.01, 10)
    
    # Find same points in warped image (optical flow)
    # This gives us displacement vectors
    
    # Fit a transformation model
    # Options: affine, perspective, polynomial
    
    return transformation_model
    

# Once you have the model, apply it to any new image
analyze_distortion("images/calibration_grid.png", "output/calibration_grid.png")