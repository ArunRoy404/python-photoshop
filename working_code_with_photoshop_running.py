import win32com.client
import os
import glob
from pathlib import Path

# Configuration
PSD_PATH = r"C:\Users\ROY\Desktop\python photoshop\psdFiles\mug.psd"
IMAGES_DIR = r"C:\Users\ROY\Desktop\python photoshop\images"
OUTPUT_DIR = r"C:\Users\ROY\Desktop\python photoshop\output"
LAYER_NAME = "front_surface"  # The Smart Object layer name

def find_layer_recursive(layers, layer_name):
    """Recursively search for a layer by name in groups and sets."""
    for layer in layers:
        if layer.Name == layer_name:
            return layer
        # Check if it's a layer set (folder) to recurse
        if layer.Typename == "LayerSet":
            found = find_layer_recursive(layer.Layers, layer_name)
            if found:
                return found
    return None

def replace_smart_object_content(psd_path, image_path, output_path, layer_name):
    """
    Opens a PSD, finds a smart object, replaces content, and scales to original bounds.
    """
    try:
        ps_app = win32com.client.Dispatch("Photoshop.Application")
    except Exception as e:
        print(f"Error: Could not connect to Photoshop. {e}")
        return False

    psd_path = os.path.abspath(psd_path)
    image_path = os.path.abspath(image_path)
    output_path = os.path.abspath(output_path)
    
    # Pre-format the path for JavaScript to avoid f-string backslash errors
    js_image_path = image_path.replace('\\', '/')

    try:
        doc = ps_app.Open(psd_path)
    except Exception as e:
        print(f"Error opening PSD: {e}")
        return False

    try:
        # Search for the layer
        target_layer = find_layer_recursive(doc.Layers, layer_name)
        
        if not target_layer:
            print(f"Error: Layer '{layer_name}' not found.")
            doc.Close(2) # psDoNotSaveChanges
            return False

        # Get original bounds to calculate scaling later
        orig_bounds = target_layer.Bounds
        orig_width = orig_bounds[2] - orig_bounds[0]
        orig_height = orig_bounds[3] - orig_bounds[1]
        
        # Select the layer
        doc.ActiveLayer = target_layer

        # JavaScript execution for Smart Object replacement
        # We use the pre-cleaned 'js_image_path' variable here
        js_code = f"""
        var idplacedLayerReplaceContents = stringIDToTypeID("placedLayerReplaceContents");
        var desc = new ActionDescriptor();
        var idnull = charIDToTypeID("null");
        desc.putPath(idnull, new File("{js_image_path}"));
        var idPgNm = charIDToTypeID("PgNm");
        desc.putInteger(idPgNm, 1);
        executeAction(idplacedLayerReplaceContents, desc, DialogModes.NO);

        var layer = app.activeDocument.activeLayer;
        var currentBounds = layer.bounds;
        var currentWidth = currentBounds[2] - currentBounds[0];
        var currentHeight = currentBounds[3] - currentBounds[1];
        
        var widthPercent = ({orig_width} / currentWidth) * 100;
        var heightPercent = ({orig_height} / currentHeight) * 100;
        
        layer.resize(widthPercent, heightPercent, AnchorPosition.MIDDLECENTER);
        """
        
        ps_app.DoJavaScript(js_code)
        print(f"Processed: {os.path.basename(image_path)}")

        # Save as PNG
        png_options = win32com.client.Dispatch("Photoshop.ExportOptionsSaveForWeb")
        png_options.Format = 13 # PNG-24
        png_options.PNG8 = False
        
        # Using SaveAs for simplicity as in your original snippet
        save_options = win32com.client.Dispatch("Photoshop.PNGSaveOptions")
        doc.SaveAs(output_path, save_options, True) 

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        doc.Close(2) # Always close without saving template changes
    
    return True

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp']
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(IMAGES_DIR, ext)))

    if not image_files:
        print(f"No images found in {IMAGES_DIR}")
        return

    print(f"Found {len(image_files)} images. Starting automation...")

    for img_path in image_files:
        img_name = Path(img_path).stem
        output_file = os.path.join(OUTPUT_DIR, f"result_{img_name}.png")
        
        success = replace_smart_object_content(PSD_PATH, img_path, output_file, LAYER_NAME)
        if not success:
            print(f"--- Failed to process: {img_name} ---")

    print("\nBatch processing complete.")

if __name__ == "__main__":
    main()