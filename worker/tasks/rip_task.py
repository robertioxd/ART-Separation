from worker.celery_app import celery_app
from backend.core.ripping import RIPEngine
from backend.core.upscaler import Upscaler
import os
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="worker.tasks.rip_task.rip_separation")
def rip_separation(job_id: str, input_path: str, lpi: int, angle: float, dot_shape: str, gain: float = 0.0):
    """
    Celery task to generate a 1-bit halftone bitmap.
    """
    logger.info(f"Starting RIP for Job {job_id}: LPI={lpi}, Angle={angle}, Shape={dot_shape}, Gain={gain}")
    
    output_dir = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    
    # Naming convention: {name}_{lpi}lpi_{angle}deg_{shape}.png
    output_filename = f"{name}_{lpi}lpi_{int(angle)}deg_{dot_shape}.png"
    output_path = os.path.join(output_dir, output_filename)

    engine = RIPEngine()
    try:
        # 1. Apply Gain Compensation (if any)
        # Note: Ideally this creates a temp intermediate file or processes in memory.
        # For MVP, we might modify in place or create a temp file.
        temp_gained_path = os.path.join(output_dir, f"{name}_gained.png") 
        if gain > 0:
            engine.apply_dot_gain(input_path, temp_gained_path, gain)
            source_path = temp_gained_path
        else:
            source_path = input_path

        # 2. Generate Halftone
        final_path = engine.generate_halftone(source_path, output_path, lpi, angle, dot_shape)
        
        # Cleanup temp
        if gain > 0 and os.path.exists(temp_gained_path):
            os.remove(temp_gained_path)

        return {
            "status": "success", 
            "job_id": job_id, 
            "output_path": final_path,
            "metadata": {"lpi": lpi, "angle": angle, "shape": dot_shape}
        }
    except Exception as e:
        logger.error(f"RIP failed: {e}")
        return {"status": "failed", "job_id": job_id, "error": str(e)}
