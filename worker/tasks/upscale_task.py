from worker.celery_app import celery_app
from backend.core.upscaler import Upscaler
import os

@celery_app.task(name="worker.tasks.upscale_task.upscale_image")
def upscale_image(job_id: str, input_path: str):
    """
    Celery task to upscale an image for a specific job.
    """
    print(f"Starting upscale for Job {job_id}")
    
    output_dir = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    output_path = os.path.join(output_dir, f"{name}_upscaled{ext}")

    upscaler = Upscaler()
    try:
        result_path = upscaler.process(input_path, output_path)
        return {"status": "success", "job_id": job_id, "output_path": result_path}
    except Exception as e:
        return {"status": "failed", "job_id": job_id, "error": str(e)}
