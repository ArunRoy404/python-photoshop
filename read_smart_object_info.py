from psd_tools import PSDImage
import json

psd = PSDImage.open(r"C:\Users\ROY\Desktop\python-photoshop\psdFiles\mug.psd")

# Find the smart object layer
smart_layer = None
for layer in psd.descendants():
    if layer.name == 'front_surface' and hasattr(layer, 'smart_object'):
        smart_layer = layer
        break

if smart_layer:
    print(f"=== Smart Object Analysis ===")
    print(f"Name: {smart_layer.name}")
    print(f"Size: {smart_layer.width}x{smart_layer.height}")
    print(f"Position: (left={smart_layer.left}, top={smart_layer.top})")
    print(f"Visible: {smart_layer.visible}")
    
    # Check if it has transformation data
    print(f"\n=== Checking for Transform/Warp Data ===")
    
    # Look for transform matrix
    if hasattr(smart_layer, 'matrix'):
        print(f"Transform Matrix: {smart_layer.matrix}")
    
    # Look for warp data (this is where the custom style might be stored)
    if hasattr(smart_layer, 'warp'):
        print(f"Warp data found: {smart_layer.warp}")
        if smart_layer.warp:
            print(f"Warp style: {smart_layer.warp.style}")
            print(f"Warp bounds: {smart_layer.warp.bounds}")
            print(f"Warp mesh: {smart_layer.warp.mesh}")
    else:
        print("No warp data found in psd-tools extraction.")
    
    # Check embedded smart object
    print(f"\n=== Smart Object Content ===")
    if smart_layer.smart_object and hasattr(smart_layer.smart_object, 'image'):
        embedded = smart_layer.smart_object.image
        print(f"Embedded image size: {embedded.width}x{embedded.height}")
        print(f"Embedded mode: {embedded.mode}")
        
        # You could save/replace this embedded image
        # embedded.save('extracted_smart_content.png')
    else:
        print("Could not extract embedded image content")
        
    print(f"\n=== What can psd-tools see? ===")
    print("Available attributes:", [attr for attr in dir(smart_layer) if not attr.startswith('_')])
    
else:
    print("Smart object layer not found!")