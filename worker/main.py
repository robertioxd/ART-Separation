from worker.celery_app import celery_app
from worker.tasks.upscale_task import upscale_image
from worker.tasks.rip_task import rip_separation
import os
import json

@celery_app.task(name="worker.main.pipeline_task")
def pipeline_task(job_id: str, input_path: str):
    """
    Orchestrates the full processing pipeline.
    1. Upscale
    2. Separation (Mock for now)
    3. RIP
    """
    print(f"Pipeline started for Job {job_id}")

    # Step 1: Upscale
    upscale_result = upscale_image(job_id, input_path)
    if upscale_result.get("status") == "failed":
        return {"status": "failed", "error": "Upscaling failed"}
    
    high_res_path = upscale_result["output_path"]
    
    # Step 2: Separation (Real K-Means)
    from backend.core.separation import Separator
    separator = Separator()
    separations = separator.separate(high_res_path, max_colors=6)
    
    # Step 3: RIP
    rip_results = []
    for sep in separations:
        rip_res = rip_separation(
            job_id, 
            sep["path"], 
            sep["lpi"], 
            sep["angle"], 
            sep["shape"], 
            gain=0.15 # 15% Gain Assumption
        )
        rip_results.append(rip_res)
        
    # Step 4: Generate Manifest
    output_dir = os.path.dirname(input_path)
    manifest = {
        "job_id": job_id,
        "status": "completed",
        "separations": rip_results
    }
    
    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        
    return {"status": "completed", "manifest": manifest}
