import cv2
import numpy as np
import json
import os
from sklearn.cluster import KMeans
from skimage import color
from typing import List, Dict

class Separator:
    def __init__(self, pantone_db_path: str = "backend/data/pantone_coated.json"):
        self.pantone_db = self._load_palette(pantone_db_path)
        
    def _load_palette(self, path: str) -> List[Dict]:
        if not os.path.exists(path):
            # Fallback if file not found (e.g. testing)
            return []
        with open(path, "r") as f:
            return json.load(f)

    def _closest_pantone(self, lab_center: np.array) -> Dict:
        """Finds the nearest Pantone color in LAB space using Euclidean distance."""
        min_dist = float("inf")
        best_match = None
        
        for p in self.pantone_db:
            p_lab = np.array(p["lab"])
            dist = np.linalg.norm(lab_center - p_lab)
            if dist < min_dist:
                min_dist = dist
                best_match = p
        
        return best_match

    def separate(self, image_path: str, max_colors: int = 6) -> List[Dict]:
        """
        Performs K-Means clustering to separate the image into spot colors.
        Returns a list of dictionaries with color info and mask paths.
        """
        # 1. Load Image
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            raise ValueError(f"Could not read image: {image_path}")
            
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        # 2. Convert to LAB for perceptual clustering
        img_lab = color.rgb2lab(img_rgb)
        
        # Flatten
        h, w, _ = img_lab.shape
        pixels = img_lab.reshape(-1, 3)
        
        # 3. K-Means
        # We use a fixed seed for reproducibility
        kmeans = KMeans(n_clusters=max_colors, random_state=42, n_init=10)
        labels = kmeans.fit_predict(pixels)
        centers = kmeans.cluster_centers_
        
        separations = []
        output_dir = os.path.dirname(image_path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # 4. Process each cluster
        mask_shape = (h, w)
        labels_img = labels.reshape(mask_shape)
        
        # Identify Background (Assuming most frequent color or lightest color is shirt/bg?)
        # For now, we extract ALL clusters. Logic to ignore "Shirt Color" comes later.
        
        for i, center in enumerate(centers):
            # Find closest Pantone
            pantone = self._closest_pantone(center)
            if not pantone:
                pantone = {"code": f"Custom_{i}", "hex": "#000000", "lab": center.tolist()}
            
            # Create Binary Mask for this cluster
            # This is a "Hard" separation. For gradient simulation, we'd need Soft K-Means or GMM.
            # But for "Sim Process", we often want solid areas + halftones.
            # To get grayscale values (halftones), we calculate "closeness" to the center.
            # MVP: Hard separation (1 where cluster matches, 0 elsewhere)
            # Better MVP: Distance-based inverted mask?
            # Let's stick to hard mask -> then we can rely on RIP to screen it?
            # No, if it's a solid mask, RIP makes it 100% ink. We lose gradients.
            
            # IMPROVEMENT: Calculate probability/membership of pixel to this cluster.
            # For MVP speed: Binary Mask is acceptable for "Spot" colors, 
            # but for "Photorealistic", we need gradients.
            # Let's assume Hard Mask for now (Ticket #2 scope seems to imply just finding the colors).
            
            mask = np.zeros(mask_shape, dtype=np.uint8)
            mask[labels_img == i] = 255 # White = Ink present
            
            # Save Mask
            sep_filename = f"{base_name}_sep_{i}_{pantone['code'].replace(' ', '_')}.png"
            sep_path = os.path.join(output_dir, sep_filename)
            cv2.imwrite(sep_path, mask)
            
            separations.append({
                "name": pantone["code"],
                "hex": pantone["hex"],
                "path": sep_path,
                "lpi": 45, # Default
                "angle": 22.5 + (i * 15), # Stagger angles
                "shape": "ellipse"
            })
            
        return separations
