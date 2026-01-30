from aspose.psd import Image
from aspose.psd.fileformats.psd import PsdImage
from aspose.pycore import cast

PSD_PATH = r"C:\Users\ROY\Desktop\python-photoshop\psdFiles\mug.psd"

def print_layers(layers, level=0):
    for layer in layers:
        print("  " * level + f"- {layer.display_name} | {type(layer)}")
        if hasattr(layer, "layers"):  # Group layer
            print_layers(layer.layers, level + 1)

with Image.load(PSD_PATH) as img:
    psd = cast(PsdImage, img)
    print_layers(psd.layers)

