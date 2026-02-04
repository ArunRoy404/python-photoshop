from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import win32com.client
import os
import uuid
import shutil
import json
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configuration (Relative to workspace root or absolute)
BASE_DIR = Path(__file__).resolve().parent.parent
PSD_DIR = str(BASE_DIR / "psdFiles")
OUTPUT_DIR = str(BASE_DIR / "server" / "temp_output")
UPLOAD_DIR = str(BASE_DIR / "server" / "uploads")
PRODUCTS_FILE = str(BASE_DIR / "server" / "products.json")
LAYER_NAME = "front_surface"

# Ensure directories exist
THUMBNAILS_DIR = str(BASE_DIR / "server" / "thumbnails")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)

# Mount static files
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/thumbnails", StaticFiles(directory=THUMBNAILS_DIR), name="thumbnails")

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

def process_photoshop_image(image_path, output_path, psd_filename):
    """
    Opens a PSD, finds a smart object, replaces content, and scales to original bounds.
    """
    try:
        # We need to dispatch Photoshop inside the request or use a global instance
        # For simplicity and reliability in a local dev server, we'll dispatch here.
        ps_app = win32com.client.Dispatch("Photoshop.Application")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not connect to Photoshop: {e}")

    abs_psd_path = os.path.abspath(os.path.join(PSD_DIR, psd_filename))
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
async def get_products(request: Request):
    """Returns a list of products from the JSON file with absolute URLs."""
    base_url = str(request.base_url).rstrip("/")
    try:
        with open(PRODUCTS_FILE, "r") as f:
            products = json.load(f)
            # Make thumbnail URLs absolute
            for product in products:
                if "thumbnail" in product and product["thumbnail"].startswith("/"):
                    product["thumbnail"] = f"{base_url}{product['thumbnail']}"
            return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading products: {e}")

@app.post("/process")
async def process_image(request: Request, product_id: str = Form(None), file: UploadFile = File(None)):
    """Upload an image, process it for all PSDs of a product, and return result URLs."""
    base_url = str(request.base_url).rstrip("/")
    
    # 1. Basic presence validation
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
        
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No image file provided")

    # 2. Image type validation
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File type not supported. Allowed: {list(allowed_extensions)}")

    # Generate unique base ID for this request
    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")

    try:
        # 3. Product existence validation
        if not os.path.exists(PRODUCTS_FILE):
             raise HTTPException(status_code=500, detail="Products database not found")

        with open(PRODUCTS_FILE, "r") as f:
            products = json.load(f)
        
        product = next((p for p in products if p["id"] == product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found")

        # 4. PSD files validation
        psd_files = product.get("psdFiles", [])
        if not psd_files:
            raise HTTPException(status_code=400, detail="This product has no PSD templates associated with it")

        for psd_name in psd_files:
            if not os.path.exists(os.path.join(PSD_DIR, psd_name)):
                raise HTTPException(status_code=500, detail=f"PSD template '{psd_name}' missing on server")

        # Save the uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result_urls = []
        # Process each PSD file associated with the product
        for psd_name in psd_files:
            output_filename = f"result_{file_id}_{psd_name.replace('.psd', '')}.png"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            process_photoshop_image(input_path, output_path, psd_name)
            result_urls.append(f"{base_url}/outputs/{output_filename}")

        # Return the list of result images for this specific request
        return JSONResponse(content={"results": result_urls})

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    # Note: In a production environment, you should clean up temp files later.

if __name__ == "__main__":
    import uvicorn
    # Optional: Clear temp folders on startup to keep things clean
    for folder in [OUTPUT_DIR, UPLOAD_DIR]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
                
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
