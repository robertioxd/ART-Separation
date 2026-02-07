import cv2
import numpy as np
import os
from PIL import Image
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import torch

class Upscaler:
    def __init__(self, model_path: str = None):
        # Default to x4plus model logic
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        # Note: In a real deploy, weights should be downloaded/cached. 
        # For MVP, we presume weights are present or RealESRGANer handles download.
        self.upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=self.model,
            tile=0, # 0 for no tile padding
            tile_pad=10,
            pre_pad=0,
            half=True if self.device.type == 'cuda' else False,
            device=self.device,
        )

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

            output, _ = self.upsampler.enhance(img, outscale=4)
            
            # 3. Save
            cv2.imwrite(output_path, output)
            return output_path
        except Exception as e:
            print(f"Upscaling failed: {e}")
            raise e
