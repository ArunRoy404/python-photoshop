# Configuration
PSD_PATH = r"C:\Users\ROY\Desktop\python-photoshop\psdFiles\cap.psd"
IMAGES_DIR = r"C:\Users\ROY\Desktop\python-photoshop\images"
OUTPUT_DIR = r"C:\Users\ROY\Desktop\python-photoshop\output"
LAYER_NAME = "front_surface"  # The Smart Object layer name

import os

from psd_tools import PSDImage

psd = PSDImage.open(PSD_PATH)

output_dir = 'smart_objects'
os.makedirs(output_dir, exist_ok=True)

for layer in psd.descendants():
    if hasattr(layer, 'smart_object'):
        so = layer.smart_object

        # Check transformation
        if so.transform_box:
            x1, y1, x2, y2, x3, y3, x4, y4 = so.transform_box
            print(f"Top-left: ({x1}, {y1})")
            print(f"Top-right: ({x2}, {y2})")
            # Use for reconstructing transformations
        
        # Check warping
        if so.warp:
            print(f"Warp applied: {so.warp}")