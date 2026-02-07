from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
from celery.result import AsyncResult
from worker.celery_app import celery_app
from backend.models.manifest import JobManifest

router = APIRouter()

TEMP_DIR = "./temp_jobs"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@router.post("/jobs")
async def create_job(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    file_path = os.path.join(job_dir, f"original_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    # Trigger Pipeline (Upscale -> Separation -> RIP)
    # For now: Just Upscale -> RIP (No Separation)
    # Ideally we use Celery 'chain' or 'chord'
    # But since separation logic isn't here yet, let's trigger a pipeline task
    
    task = celery_app.send_task("worker.main.pipeline_task", args=[job_id, file_path])
    
    return {"job_id": job_id, "status": "submitted", "task_id": task.id}

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    # This is a simplified status check. 
    # In production, we should query a DB or Redis for the job state.
    # For MVP, we can check if the output manifest exists.
    
    job_dir = os.path.join(TEMP_DIR, job_id)
    manifest_path = os.path.join(job_dir, "manifest.json")
    
    if os.path.exists(manifest_path):
        return JSONResponse(content={"status": "completed", "manifest_url": f"/jobs/{job_id}/manifest"})
    
    return {"status": "processing", "job_id": job_id}
