from psd_tools import PSDImage

PSD_PATH = r"C:\Users\ROY\Desktop\python-photoshop\psdFiles\mug.psd"
IMAGES_DIR = r"C:\Users\ROY\Desktop\python-photoshop\images"
OUTPUT_DIR = r"C:\Users\ROY\Desktop\python-photoshop\output"
LAYER_NAME = "front_surface"  # The Smart Object layer name

psd = PSDImage.open(PSD_PATH)
for layer in psd.descendants():
    if layer.name == 'front_surface' and layer.kind == 'smartobject':
        print(f"Found smart object: {layer}")
        # Layer has .smart_object attribute
        # You can replace its embedded image maybe
        # But warp info is lost here