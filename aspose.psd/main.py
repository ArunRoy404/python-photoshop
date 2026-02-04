import os
import glob
from pathlib import Path
from aspose.psd import Image
from aspose.psd.imageloadoptions import PsdLoadOptions
from aspose.psd.fileformats.psd import PsdImage
from aspose.psd.fileformats.psd.layers.smartobjects import SmartObjectLayer
from aspose.psd.imageoptions import PngOptions
from aspose.pycore import cast

# Configuration
PSD_PATH = r"C:\Users\ROY\Desktop\python-photoshop\psdFiles\mug.psd"
IMAGES_DIR = r"C:\Users\ROY\Desktop\python-photoshop\images"
OUTPUT_DIR = r"C:\Users\ROY\Desktop\python-photoshop\output"
LAYER_NAME = "front_surface"  # The Smart Object layer name

def find_smart_object_layer(layers, layer_name, level=0):
    """Recursively search for a SmartObjectLayer in Aspose."""
    for layer in layers:
        # Debug printing to see what we are looking at
        try:
            d_name = str(getattr(layer, "display_name", ""))
            i_name = str(getattr(layer, "name", ""))
            # print(f"{'  '*level}Checking: '{d_name}' / '{i_name}'")
            
            # Check if name matches
            if layer_name.lower() in [d_name.lower(), i_name.lower()]:
                # In Aspose, SmartObjectLayer is the specific class for these
                if "SmartObjectLayer" in str(type(layer)):
                    return cast(SmartObjectLayer, layer)
                
                # Sometimes it might just be a Layer but we can try to cast it
                try:
                    return cast(SmartObjectLayer, layer)
                except:
                    pass

            # Recursion into Groups
            # In Aspose, LayerGroup has a 'layers' property
            if "LayerGroup" in str(type(layer)):
                group_layers = getattr(layer, "layers", [])
                found = find_smart_object_layer(group_layers, layer_name, level + 1)
                if found:
                    return found
        except Exception as e:
            print(f"Error checking layer: {e}")
            
    return None

def replace_smart_object_content(psd_path, image_path, output_path, layer_name):
    """
    Opens a PSD using Aspose, finds a smart object, replaces content, and saves as PNG.
    This does NOT require Photoshop to be running.
    """
    print(f"Processing: {os.path.basename(image_path)}")
    
    # Configure load options to preserve effects and warp transformations
    load_options = PsdLoadOptions()
    load_options.allow_warp_repaint = True
    load_options.load_effects_resource = True 

    try:
        # Load the PSD file
        with Image.load(psd_path, load_options) as img:
            psd_image = cast(PsdImage, img)
            
            # Search for the target Smart Object layer
            target_layer = find_smart_object_layer(psd_image.layers, layer_name)
            
            if not target_layer:
                print(f"Error: Smart Object Layer '{layer_name}' not found.")
                print("Detailed Layer Inventory:")
                def list_all(layers, prefix=""):
                    for l in layers:
                        print(f"{prefix}- '{getattr(l, 'display_name', 'Unnamed')}' Type: {type(l)}")
                        if "LayerGroup" in str(type(l)):
                            list_all(getattr(l, "layers", []), prefix + "  ")
                list_all(psd_image.layers)
                return False

            # Replace the contents of the smart object with the new image
            # Aspose automatically handles the replacement and maintains existing transformations (warp/resize)
            target_layer.replace_contents(image_path)
            
            # Save the result as PNG
            # You can also use JpegOptions, TiffOptions, etc.
            png_options = PngOptions()
            psd_image.save(output_path, png_options)
            
            print(f"Saved: {output_path}")
            return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def main():
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Get all images in the input directory
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(IMAGES_DIR, ext)))

    if not image_files:
        print(f"No images found in {IMAGES_DIR}")
        return

    print(f"Found {len(image_files)} images. Starting Aspose automation (No Photoshop required)...")

    for img_path in image_files:
        img_name = Path(img_path).stem
        output_file = os.path.join(OUTPUT_DIR, f"aspose_result_{img_name}.png")
        
        success = replace_smart_object_content(PSD_PATH, img_path, output_file, LAYER_NAME)
        if not success:
            print(f"--- Failed to process: {img_name} ---")

    print("\nBatch processing complete.")

if __name__ == "__main__":
    main()
