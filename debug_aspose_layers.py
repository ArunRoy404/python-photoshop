import os
print("Importing Aspose...")
try:
    from aspose.psd import Image
    from aspose.psd.imageloadoptions import PsdLoadOptions
    from aspose.psd.fileformats.psd import PsdImage
    from aspose.psd.fileformats.psd.layers.smartobjects import SmartObjectLayer
    from aspose.pycore import cast
    print("Imports successful.")
except Exception as e:
    print(f"Import Error: {e}")
    exit(1)

PSD_PATH = r"C:\Users\ROY\Desktop\python-photoshop\psdFiles\mug.psd"

def debug_layers(layers, level=0):
    for layer in layers:
        try:
            name = getattr(layer, 'display_name', 'No Display Name')
            print("  " * level + f"Layer: '{name}' | Type: {type(layer)}")
            
            if isinstance(layer, SmartObjectLayer):
                 print("  " * level + "  -> THIS IS A SMART OBJECT")

            if hasattr(layer, "layers"):
                debug_layers(layer.layers, level + 1)
        except Exception as e:
            print("  " * level + f"Error reading layer info: {e}")

print(f"Loading PSD: {PSD_PATH}")
load_options = PsdLoadOptions()
# load_options.allow_warp_repaint = False  # Faster loading for debug
load_options.load_effects_resource = False # Faster loading for debug

try:
    with Image.load(PSD_PATH, load_options) as img:
        print("PSD Loaded successfully. Analyzing layers...")
        psd = cast(PsdImage, img)
        debug_layers(psd.layers)
except Exception as e:
    print(f"Error during load/analyze: {e}")
