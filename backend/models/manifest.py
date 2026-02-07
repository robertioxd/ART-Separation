from pydantic import BaseModel
from typing import List, Dict

class SeparationFile(BaseModel):
    ripped: str
    grayscale: str
    vector: str

class SeparationSettings(BaseModel):
    lpi: int
    angle: float
    dot_shape: str

class SeparationLayer(BaseModel):
    name: str
    type: str # Underbase, TopColor, Black
    files: SeparationFile
    settings: SeparationSettings

class JobManifest(BaseModel):
    job_id: str
    print_order: List[str]
    separations: List[SeparationLayer]
