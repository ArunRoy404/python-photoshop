from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import win32com.client
import os
import uuid
import shutil
from pathlib import Path

app = FastAPI()

# Configuration (Relative to workspace root or absolute)
BASE_DIR = Path(__file__).resolve().parent.parent
PSD_PATH = str(BASE_DIR / "psdFiles" / "mug.psd")
OUTPUT_DIR = str(BASE_DIR / "server" / "temp_output")
UPLOAD_DIR = str(BASE_DIR / "server" / "uploads")
LAYER_NAME = "front_surface"

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

def find_layer_recursive(layers, layer_name):
    """Recursively search for a layer by name in groups and sets."""
    for layer in layers:
        if layer.Name == layer_name:
            return layer
        if layer.Typename == "LayerSet":
            found = find_layer_recursive(layer.Layers, layer_name)
            if found:
                return found
    return None

def process_photoshop_image(image_path, output_path):
    """
    Opens a PSD, finds a smart object, replaces content, and scales to original bounds.
    """
    try:
        # We need to dispatch Photoshop inside the request or use a global instance
        # For simplicity and reliability in a local dev server, we'll dispatch here.
        ps_app = win32com.client.Dispatch("Photoshop.Application")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not connect to Photoshop: {e}")

    abs_psd_path = os.path.abspath(PSD_PATH)
    abs_image_path = os.path.abspath(image_path)
    abs_output_path = os.path.abspath(output_path)
    
    js_image_path = abs_image_path.replace('\\', '/')

    try:
        doc = ps_app.Open(abs_psd_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error opening PSD: {e}")

    try:
        target_layer = find_layer_recursive(doc.Layers, LAYER_NAME)
        
        if not target_layer:
            doc.Close(2) # psDoNotSaveChanges
            raise HTTPException(status_code=404, detail=f"Layer '{LAYER_NAME}' not found in PSD.")

        orig_bounds = target_layer.Bounds
        orig_width = orig_bounds[2] - orig_bounds[0]
        orig_height = orig_bounds[3] - orig_bounds[1]
        
        doc.ActiveLayer = target_layer

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

        # Save as PNG
        save_options = win32com.client.Dispatch("Photoshop.PNGSaveOptions")
        doc.SaveAs(abs_output_path, save_options, True) 

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Photoshop processing error: {e}")
    finally:
        doc.Close(2) # Always close without saving template changes

@app.get("/products")
async def get_products():
    """Returns a list of demo products."""
    return [
        {
            "id": "mug_001",
            "name": "Premium Ceramic Mug",
            "thumbnail": "https://images.unsplash.com/photo-1514228742587-6b1558fbed20?w=200",
            "width": 2000,
            "height": 2000
        },
        {
            "id": "tshirt_001",
            "name": "Cotton Unisex T-Shirt",
            "thumbnail": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=200",
            "width": 1500,
            "height": 1800
        }
    ]

@app.post("/process")
async def process_image(file: UploadFile = File(...)):
    """Upload an image, process it in Photoshop, and return the result."""
    # Generate unique filenames to avoid collision
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    output_path = os.path.join(OUTPUT_DIR, f"result_{file_id}.png")

    try:
        # Save the uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the image
        process_photoshop_image(input_path, output_path)

        # Return the resulting image
        return FileResponse(output_path, media_type="image/png")

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    # Note: In a production environment, you should clean up temp files later.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
