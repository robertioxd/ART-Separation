import os
import subprocess
import numpy as np
from PIL import Image, ImageOps

class RIPEngine:
    def __init__(self):
        # Default Ghostscript command (Windows/Linux compatible usually, but path might vary)
        self.gs_cmd = "gs" if os.name != 'nt' else "gswin64c" 

    def apply_dot_gain(self, input_path: str, output_path: str, gain: float):
        """
        Applies a dot gain compensation curve.
        Formula: Out = In - (In * Gain)
        Input 'gain' is a decimal percentage (e.g., 0.20 for 20%).
        """
        try:
            with Image.open(input_path) as img:
                img = img.convert("L") # Ensure Grayscale
                # Convert to numpy for faster processing
                arr = np.array(img, dtype=float)
                
                # Normalize 0-1
                arr = arr / 255.0
                
                # Apply compensation: Darker pixels (lower values) gain ink.
                # In printing: 0 is white (no ink), 1 is black (full ink).
                # But in standard imaging: 0 is black, 255 is white.
                # Let's invert first to think in "Ink Density" (0=White, 1=Black)
                ink_density = 1.0 - arr
                
                # Compensation logic:
                # If we expect 20% gain, a 50% dot will look like 70% on shirt.
                # So we want the printed result to be X. Start with Target.
                # Printed = Digital + Gain
                # Digital = Printed - Gain
                # Gain is usually proportional to the dot area (simple model).
                # Simple linear reduction for MVP: Reduced = Target * (1 - Gain)
                compensated_ink = ink_density * (1.0 - gain)
                
                # Clamp
                compensated_ink = np.clip(compensated_ink, 0.0, 1.0)
                
                # Convert back to pixel values (0=Black, 1=White)
                final_arr = (1.0 - compensated_ink) * 255.0
                
                final_img = Image.fromarray(final_arr.astype(np.uint8))
                final_img.save(output_path)
                return output_path
        except Exception as e:
            print(f"Dot Gain Compensation Failed: {e}")
            raise e

    def generate_halftone(self, input_path: str, output_path: str, lpi: int, angle: float, shape: str):
        """
        Generates a 1-bit bitmap using Ghostscript for AM Halftoning.
        """
        # 1. Prepare Input: Convert to EPS/PDF to ensure GS handles it well with screening
        temp_pdf = input_path + ".pdf"
        try:
            with Image.open(input_path) as img:
                 # Ensure standard size/dpi is respected
                 img.save(temp_pdf, "PDF", resolution=300.0)
        except Exception as e:
             # Fallback: Just pass the image path if PIL fails (unlikely)
             temp_pdf = input_path

        # 2. Construct Ghostscript Command
        # Resolution: 1200 or 2400 DPI usually for RIPs. Let's use 720 or 1440 for speed/quality balance.
        resolution = 1200 
        
        # PostScript Screening Function
        # Simple Ellipse Dot Function (Euclidean)
        # Type 1 Halftone dictionary
        # We inject a PostScript command to set the screen.
        
        # Basic Ellipse Spot Function in PostScript
        # { dup mul exch dup mul add 1.0 exch sub } is a simple round dot.
        # { abs exch abs 2 copy add 1 gt { 1 sub dup mul exch 1 sub dup mul add 1 sub } { dup mul exch dup mul add 1 exch sub } ifelse } is Euclidean (Round-Square-Round)
        
        # Taking a standard Ellipse function:
        spot_func = "{ dup mul exch dup mul add 1 exch sub }" 
        if shape == "ellipse":
             # Standard euclidean dot for now. True ellipse needs eccentricity.
             spot_func = "{ abs exch abs 2 copy add 1 gt { 1 sub dup mul exch 1 sub dup mul add 1 sub } { dup mul exch dup mul add 1 exch sub } ifelse }"

        # Command construction
        # gs -dNOPAUSE -dBATCH -sDEVICE=tiffg4 -r1200 -c "<</HalftoneType 1 /Frequency 45 /Angle 22.5 /SpotFunction { ... } >> sethalftone" -f input.pdf -sOutputFile=out.tif
        
        gs_Screen_Cmd = f"<</HalftoneType 1 /Frequency {lpi} /Angle {angle} /SpotFunction {spot_func} >> sethalftone"
        
        # Note: Ghostscript requires output file to be specified appropriately.
        # pngmonod is 1-bit PNG.
        
        cmd = [
            self.gs_cmd,
            "-dNOPAUSE",
            "-dBATCH",
            "-dQUIET",
            "-sDEVICE=pngmonod",
            f"-r{resolution}",
            f"-sOutputFile={output_path}",
            "-c", gs_Screen_Cmd,
            "-f", temp_pdf
        ]
        
        try:
            print(f"Executing Ghostscript: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Cleanup temp PDF
            if os.path.exists(temp_pdf) and temp_pdf != input_path:
                os.remove(temp_pdf)
                
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Ghostscript Error: {e.stderr.decode()}")
            raise RuntimeError(f"Ghostscript failed to generate halftone: {e.stderr.decode()}")
        except FileNotFoundError:
            # Fallback if GS is not installed (e.g. dev environment)
            print("Ghostscript executable not found. Falling back to PIL generic dither (NOT AM MATRIX).")
            return self._fallback_pillow_halftone(input_path, output_path)

    def _fallback_pillow_halftone(self, input_path: str, output_path: str):
        """
        Simple error diffusion dither if GS fails. Not true AM, but functional 1-bit.
        """
        with Image.open(input_path) as img:
            img = img.convert("1") # Default dithering
            img.save(output_path)
        return output_path
