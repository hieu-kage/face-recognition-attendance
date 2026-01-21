
import os
from typing import Optional, List
from datetime import datetime

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.models import MobileNet_V2_Weights

import cv2
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN

_model = None
_device = None
_transform = None
_mtcnn = None

IMG_SIZE = 160
EMBEDDING_DIM = 256
MODEL_PATH = "siamese_mobilenetv2_best.pth"

TEMP_SAVE_DIR = "tmp_images"
os.makedirs(TEMP_SAVE_DIR, exist_ok=True)

class EmbeddingNet(nn.Module):
    def __init__(self, embedding_dim=EMBEDDING_DIM):
        super().__init__()
        mobilenet = models.mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
        self.backbone = mobilenet.features
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(1280, embedding_dim)
        )

    def forward(self, x):
        x = self.backbone(x)
        x = self.pool(x).view(x.size(0), -1)
        x = self.fc(x)
        x = F.normalize(x, p=2, dim=1)
        return x

class SiameseNet(nn.Module):
    def __init__(self, embedding_dim=EMBEDDING_DIM):
        super().__init__()
        self.embedding = EmbeddingNet(embedding_dim)

def load_model_once():

    global _model, _device, _transform, _mtcnn
    if _model is not None:
        return

    print("Loading AI models...")
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    _model = SiameseNet(embedding_dim=EMBEDDING_DIM).to(_device)
    try:
        _model.load_state_dict(torch.load(MODEL_PATH, map_location=_device))
    except FileNotFoundError:
        print(f"Error: Model file not found at {MODEL_PATH}")
        raise

    _model.eval()

    _transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    print("Initializing MTCNN...")
    _mtcnn = MTCNN(keep_all=False, post_process=False, device=_device)

    print("AI Models ready.")

import tempfile

def save_image_temp(img: np.ndarray) -> str:
    try:
        fd, file_path = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)
        
        cv2.imwrite(file_path, img)
        return file_path
    except Exception as e:
        print(f"Error saving temp image: {e}")
        return ""

def detect_face(image: np.ndarray) -> Optional[np.ndarray]:

    if _mtcnn is None:
        load_model_once()

    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)

    face_tensor = _mtcnn(img_pil)

    if face_tensor is None:
        return None

    face_np = face_tensor.permute(1, 2, 0).cpu().numpy()

    face_np = face_np.astype(np.uint8)

    face_bgr = cv2.cvtColor(face_np, cv2.COLOR_RGB2BGR)

    save_image_temp(face_bgr)

    return face_bgr

def image_to_embedding(image: np.ndarray) -> Optional[List[float]]:

    try:
        face = detect_face(image)
        if face is None:
            return None
        if face is None:
            return None
            
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        img_tensor = _transform(face_rgb).unsqueeze(0).to(_device)
        
        with torch.no_grad():
            embedding = _model.embedding(img_tensor)

        return embedding.cpu().numpy().flatten().tolist()
    except Exception as e:
        print(f"Error in image_to_embedding: {str(e)}")
        return None