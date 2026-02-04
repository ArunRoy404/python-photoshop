# Photoshop Automation Server

This is a simple FastAPI server that provides two endpoints: one for listing products and another for processing images using local Photoshop automation.

## Setup

1.  **Dependencies**:
    Ensure you have Python installed. Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Photoshop**:
    Ensure Adobe Photoshop is installed and running on your machine.

3.  **Run the Server**:
    From the `server` directory, run:
    ```bash
    python app.py
    ```
    The server will start at `http://localhost:8000`.

## API Endpoints

### 1. GET `/products`
Returns a list of demo products.

**Example Request**:
```bash
curl http://localhost:8000/products
```

### 2. POST `/process`
Uploads an image, replaces it in the Photoshop PSD template, and returns the result as a PNG.

**Example Request (using cURL)**:
```bash
curl -X POST -F "file=@your_image.jpg" http://localhost:8000/process --output result.png
```

## Global Access (ngrok)

To make this server accessible globally from the internet:

1.  [Download and install ngrok](https://ngrok.com/download).
2.  In a new terminal, run:
    ```bash
    ngrok http 8000
    ```
3.  Copy the "Forwarding" URL (e.g., `https://xyz.ngrok-free.app`). This URL can now be used from anywhere in the world to access your local Photoshop server!

## Notes

- The server uses `win32com` to control Photoshop, so it **must** run on Windows.
- Make sure the PSD file path in `app.py` is correct. Current path: `psdFiles/mug.psd`.
