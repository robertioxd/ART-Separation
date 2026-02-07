from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.jobs import router as jobs_router

app = FastAPI(title="ChromaScreen AI")

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
