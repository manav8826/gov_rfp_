from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import uuid
from app.models.rfp import ProcessingStatus, RFPResponse

router = APIRouter()

# In-memory storage for MVP
jobs = {}

def process_rfp_task(job_id: str, file_content: bytes):
    jobs[job_id]["status"] = "processing"
    jobs[job_id]["progress"] = 10
    
    try:
        from app.services.technical_agent import TechnicalAgent
        from app.services.pricing_agent import PricingAgent
        
        # 1. Technical Analysis
        tech_agent = TechnicalAgent()
        tech_result = tech_agent.process_rfp(file_content)
        jobs[job_id]["progress"] = 50
        
        # 2. Pricing Calculation
        pricing_agent = PricingAgent()
        final_result = pricing_agent.calculate_pricing(tech_result)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["result"] = final_result
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = str(e)

@router.post("/upload", response_model=ProcessingStatus)
async def upload_rfp(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    job_id = str(uuid.uuid4())
    
    # Read file content (in real app, save to disk/S3)
    content = await file.read()
    
    # Initialize Job
    jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "filename": file.filename
    }
    
    # Trigger Background Task
    background_tasks.add_task(process_rfp_task, job_id, content)
    
    return ProcessingStatus(
        job_id=job_id,
        status="queued",
        progress=0,
        message="RFP uploaded and processing started"
    )

@router.get("/{job_id}/status", response_model=ProcessingStatus)
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return ProcessingStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"]
    )

@router.get("/{job_id}/result")
async def get_result(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = jobs[job_id]
    if job["status"] == "failed":
        raise HTTPException(status_code=500, detail=f"Job Failed: {job.get('message')}")
        
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Job still processing (Status: {job['status']}). Progress: {job['progress']}%")
        
    return job.get("result", {})
