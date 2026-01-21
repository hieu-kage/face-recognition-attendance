"""
Face Recognition API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import cv2
from PIL import Image
import io
import base64

from face_ulti import load_model_once, image_to_embedding

app = FastAPI(title="Face Embedding Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageBase64Request(BaseModel):
    image_base64: str

class EmbeddingResponse(BaseModel):
    success: bool
    embedding: Optional[List[float]] = None
    message: Optional[str] = None

@app.on_event("startup")
async def startup():
    load_model_once()

def base64_to_image(base64_str: str) -> np.ndarray:
    try:
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]

        img_bytes = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')

        img_array = np.array(image).astype(np.uint8)

        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        return img_bgr

    except Exception as e:
        raise ValueError(f"Invalid base64 image: {str(e)}")
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/embedding", response_model=EmbeddingResponse)
async def extract_embedding_api(request: ImageBase64Request):
    try:
        try:
            img = base64_to_image(request.image_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image")

        embedding = image_to_embedding(img)
        if embedding is None:
            return EmbeddingResponse(success=False, message="No face detected")

        return EmbeddingResponse(success=True, embedding=embedding)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
