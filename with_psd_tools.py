import os
import glob
from pathlib import Path
import photoshopapi as psapi

# === LINUX STYLE PATHS ===
PSD_PATH = r"C:\Users\ROY\Desktop\python-photoshop\psdFiles\mug.psd"
IMAGES_DIR = r"C:\Users\ROY\Desktop\python-photoshop\images"
OUTPUT_DIR = r"C:\Users\ROY\Desktop\python-photoshop\output"
LAYER_NAME = "front_surface"  # The Smart Object layer name

def find_layer_recursive(layer_list, name):
    """Recursively search for a layer by name."""
    for layer in layer_list:
        if layer.name == name:
            return layer
        if hasattr(layer, 'layers'):
            found = find_layer_recursive(layer.layers, name)
            if found:
                return found
    return None

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get all images from the images directory
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(IMAGES_DIR, ext)))

    if not image_files:
        print(f"No images found in {IMAGES_DIR}")
        return

    print(f"Found {len(image_files)} images to process.")

    for img_path in image_files:
        img_name = Path(img_path).stem
        output_path = os.path.join(OUTPUT_DIR, f"result_{img_name}.psd")
        
        print(f"Processing: {img_name}...")

        try:
            # Read the PSD file
            layered_file = psapi.LayeredFile.read(PSD_PATH)
            
            # Find the target layer
            target_layer = find_layer_recursive(layered_file.layers, LAYER_NAME)

            if not target_layer:
                print(f"Error: Layer '{LAYER_NAME}' not found.")
                continue

            # Check if it's a Smart Object Layer to use .replace()
            if not hasattr(target_layer, 'replace'):
                print(f"Error: Layer '{LAYER_NAME}' is not a Smart Object layer.")
                continue

            # Store original dimensions
            orig_w = target_layer.width
            orig_h = target_layer.height

            # Replace the content of the smart object
            target_layer.replace(img_path)
            
            # Optional: Resize back to original bounds
            curr_w = target_layer.width
            curr_h = target_layer.height
            if curr_w > 0 and curr_h > 0:
                scale_x = orig_w / curr_w
                scale_y = orig_h / curr_h
                if abs(scale_x - 1.0) > 0.001 or abs(scale_y - 1.0) > 0.001:
                    target_layer.scale(scale_x, scale_y, target_layer.center_x, target_layer.center_y)

            # Write the result to disk
            layered_file.write(output_path)
            print(f"Successfully saved: {output_path}")

        except Exception as e:
            if "Linked Layer version 8" in str(e):
                print(f"Error: Internal PSD incompatibility (Linked Layer version 8).")
                print(f"Solution: Open {PSD_PATH} in Photoshop, right-click '{LAYER_NAME}', select 'Embed Linked', and Save.")
            else:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
