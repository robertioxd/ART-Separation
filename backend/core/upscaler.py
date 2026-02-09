import cv2
import numpy as np
import os
from PIL import Image
from basicsr.archs.rrdbnet_arch import RRDBNet
try:
    from realesrgan import RealESRGANer
    HAS_REALESRGAN = True
except ImportError:
    RealESRGANer = None
    HAS_REALESRGAN = False
    print("RealESRGAN not found. Upscaling will be disabled.")

import torch

# Default Real-ESRGAN model URL (official release)
DEFAULT_MODEL_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"

class Upscaler:
    def __init__(self, model_path: str = None):
        self.enabled = HAS_REALESRGAN
        self.upsampler = None
        
        if not self.enabled:
            print("[Upscaler] RealESRGAN not available. Upscaling disabled.")
            return
        
        # 1. GRACEFUL FALLBACK: If model_path is None or empty, use default URL
        if not model_path:
            model_path = DEFAULT_MODEL_URL
            print(f"[Upscaler] No model_path provided. Using default: {model_path}")
        
        # 2. DEVICE SETUP
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"[Upscaler] Using device: {self.device}")
        
        self.model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        
        # 3. FAIL-SAFE INITIALIZATION (Backend Specialist Rule)
        try:
            self.upsampler = RealESRGANer(
                scale=4,
                model_path=model_path,
                model=self.model,
                tile=400,  # Process in 400x400 tiles to prevent OOM on large images
                tile_pad=10,
                pre_pad=0,
                half=True if self.device.type == 'cuda' else False,
                device=self.device,
            )
            print("[Upscaler] RealESRGANer initialized successfully.")
        except Exception as e:
            print(f"[Upscaler] CRITICAL: Failed to initialize RealESRGANer: {e}")
            self.enabled = False  # Graceful degradation

    def process(self, image_path: str, output_path: str) -> str:
        """
        Upscales the image if DPI < 300.
        Returns the path to the high-res image.
        """
        # 1. Check DPI
        try:
            with Image.open(image_path) as img:
                dpi = img.info.get('dpi', (72, 72))
                avg_dpi = sum(dpi) / 2
                if avg_dpi >= 300:
                    print(f"Image {image_path} is already {avg_dpi} DPI. Skipping upscale.")
                    return image_path
        except Exception as e:
            print(f"Error reading DPI: {e}. Proceeding with upscale check.")

        # 2. Upscale
        try:
            img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")

            if not self.enabled:
                print("Upscaling disabled. Returning original image.")
                return image_path

            output, _ = self.upsampler.enhance(img, outscale=4)
            
            # 3. Save
            cv2.imwrite(output_path, output)
            return output_path
        except Exception as e:
            print(f"Upscaling failed: {e}")
            raise e
