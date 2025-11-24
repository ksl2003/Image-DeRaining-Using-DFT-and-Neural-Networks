from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
from PIL import Image
import tensorflow as tf
import cv2
import io
import base64
from model_utils import build_derain_model, to_frequency_domain, from_frequency_domain, sharpen_image
import os

app = FastAPI(title="Image De-raining API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
model = None

def load_model():
    """Load the de-raining model"""
    global model
    if model is None:
        model = build_derain_model()
        # Try to load weights if they exist
        weights_path = "model_weights.h5"
        if os.path.exists(weights_path):
            model.load_weights(weights_path)
            print("✅ Model weights loaded")
        else:
            print("⚠️ No weights file found. Using untrained model.")
    return model

@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    load_model()
    print("🚀 FastAPI server started and model loaded")

@app.get("/")
async def root():
    return {"message": "Image De-raining API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/api/derain")
async def derain_image(file: UploadFile = File(...)):
    """
    Process a rainy image and return the de-rained version
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # Resize to 256x256
        image = image.resize((256, 256))
        rainy_np = np.array(image) / 255.0
        rainy_tf = tf.convert_to_tensor(rainy_np, dtype=tf.float32)
        
        # Get model
        model = load_model()
        
        # Frequency domain conversion
        x_freq = to_frequency_domain(rainy_tf, mode='real_imag')
        x_freq = tf.transpose(x_freq, perm=[1, 2, 0, 3])
        x_freq = tf.reshape(x_freq, [1, 256, 256, 6])
        
        # Model prediction
        rain_map = model(x_freq, training=False)[0]
        freq_reshaped = tf.reshape(x_freq[0], [256, 256, 3, 2])
        rainy_reconstructed = from_frequency_domain(freq_reshaped)
        
        # Generate clean image
        clean_pred = tf.clip_by_value(rainy_reconstructed - rain_map, 0.0, 1.0)
        clean_pred = sharpen_image(clean_pred.numpy())
        
        # Convert to PIL Image
        clean_img = (clean_pred * 255).astype(np.uint8)
        clean_pil = Image.fromarray(clean_img)
        
        # Convert to base64
        buffer = io.BytesIO()
        clean_pil.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Also encode original for comparison
        buffer_orig = io.BytesIO()
        image.save(buffer_orig, format='PNG')
        orig_base64 = base64.b64encode(buffer_orig.getvalue()).decode('utf-8')
        
        return JSONResponse({
            "success": True,
            "original_image": f"data:image/png;base64,{orig_base64}",
            "derained_image": f"data:image/png;base64,{img_base64}",
            "message": "Image processed successfully"
        })
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

