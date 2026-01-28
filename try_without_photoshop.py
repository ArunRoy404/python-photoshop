import win32com.client
import os
import glob
from pathlib import Path

# Configuration
# PSD_PATH = r"C:\Users\ROY\Desktop\cap-mockup\psdFiles\cap.psd"
PSD_PATH = r"C:\Users\ROY\Desktop\cap-mockup\psdFiles\mug.psd"
IMAGES_DIR = r"C:\Users\ROY\Desktop\cap-mockup\images"
OUTPUT_DIR = r"C:\Users\ROY\Desktop\cap-mockup\output"
LAYER_NAME = "front_surface"  # The Smart Object layer name

def replace_smart_object_content(psd_path, image_path, output_path, layer_name):
    """
    Opens a PSD, finds a smart object layer by name, replaces its content with a new image,
    and saves the result. Preserves warp and other transformations.
    """
    try:
        # Initialize Photoshop application
        ps_app = win32com.client.Dispatch("Photoshop.Application")
    except Exception as e:
        print("Error: Photoshop is not installed or could not be opened.")
        print(f"Details: {e}")
        return False

    # Ensure paths are absolute and use forward slashes for JavaScript
    psd_path = os.path.abspath(psd_path)
    image_path = os.path.abspath(image_path)
    output_path = os.path.abspath(output_path)
    
    # Photoshop might be busy, but dispatch usually waits. 
    # We open the document
    try:
        doc = ps_app.Open(psd_path)
    except Exception as e:
        print(f"Error opening PSD: {e}")
        return False

    try:
        # Set the target layer as the active layer
        # Note: If the layer is inside a group, this might need recursion.
        # However, if it's top-level or uniquely named, this usually works.
        target_layer = None
        
        # Searching for the layer by name
        for layer in doc.Layers:
            if layer.Name == layer_name:
                target_layer = layer
                break
        
        if not target_layer:
            # Try ArtLayers if not found in top-level Layers
            try:
                target_layer = doc.ArtLayers.Item(layer_name)
            except:
                pass
        
        if not target_layer:
            print(f"Error: Layer '{layer_name}' not found.")
            doc.Close(2)  # 2 = psDoNotSaveChanges

        # Get original bounds of the smart object layer
        # This gives us (left, top, right, bottom)
        orig_bounds = target_layer.Bounds
        orig_width = orig_bounds[2] - orig_bounds[0]
        orig_height = orig_bounds[3] - orig_bounds[1]
        
        ps_app.ActiveDocument.ActiveLayer = target_layer

        # JavaScript to:
        # 1. Replace the content
        # 2. Automatically scale the layer back to the original boundaries
        # This handles the "resolution difference" problem.
        js_code = f"""
        var idplacedLayerReplaceContents = stringIDToTypeID("placedLayerReplaceContents");
        var desc = new ActionDescriptor();
        var idnull = charIDToTypeID("null");
        desc.putPath(idnull, new File("{image_path.replace('\\', '/')}"));
        var idPgNm = charIDToTypeID("PgNm");
        desc.putInteger(idPgNm, 1);
        executeAction(idplacedLayerReplaceContents, desc, DialogModes.NO);

        // Resize the layer to match original dimensions
        var doc = app.activeDocument;
        var layer = doc.activeLayer;
        
        // Calculate scale factors
        var currentBounds = layer.bounds;
        var currentWidth = currentBounds[2] - currentBounds[0];
        var currentHeight = currentBounds[3] - currentBounds[1];
        
        var widthPercent = ({orig_width} / currentWidth) * 100;
        var heightPercent = ({orig_height} / currentHeight) * 100;
        
        // We use the smaller of the two to fit but maintain aspect ratio? 
        // Or do you want it to EXACTLY match the original area?
        // Let's go with exact matching for width/height as requested.
        layer.resize(widthPercent, heightPercent, AnchorPosition.MIDDLECENTER);
        """
        
        ps_app.DoJavaScript(js_code)
        print(f"Successfully replaced and resized content: {os.path.basename(image_path)}")

        # Save the result as PNG
        png_options = win32com.client.Dispatch("Photoshop.PNGSaveOptions")
        doc.SaveAs(output_path, png_options, True) # True = Save as copy
    except Exception as e:
        print(f"An error occurred during processing: {e}")
    finally:
        # Always close the document without saving changes to the original template
        doc.Close(2) 
    
    return True

def main():
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

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
        output_path = os.path.join(OUTPUT_DIR, f"result_{img_name}.png")
        
        print(f"Processing: {img_name}...")
        success = replace_smart_object_content(PSD_PATH, img_path, output_path, LAYER_NAME)
        
        if success:
            print(f"Saved to: {output_path}")
        else:
            print(f"Failed to process: {img_name}")

if __name__ == "__main__":
    # Requirements: 
    # 1. Adobe Photoshop installed on Windows.
    # 2. 'pip install pywin32'
    main()
