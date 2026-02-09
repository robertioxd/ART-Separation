from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.jobs import router as jobs_router

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="ChromaScreen AI")

# Ensure temp dir exists
if not os.path.exists("./temp_jobs"):
    os.makedirs("./temp_jobs")

app.mount("/files", StaticFiles(directory="./temp_jobs"), name="files")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)

@app.get("/")
def read_root():
    return {"status": "ChromaScreen AI Backend Online"}
