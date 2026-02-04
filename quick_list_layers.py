from psd_tools import PSDImage

PSD_PATH = r"C:\Users\ROY\Desktop\python-photoshop\psdFiles\mug.psd"
psd = PSDImage.open(PSD_PATH)

print("Listing all layers using psd-tools:")
for layer in psd.descendants():
    print(f"Name: '{layer.name}' | Kind: {layer.kind}")
