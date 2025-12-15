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
        
@router.post("/pipeline/run-auto")
async def run_full_pipeline_auto(background_tasks: BackgroundTasks):
    """
    Fulfills Requirement: 'Identifies 1 RFP... and sends this to the Main agent.'
    1. Sales Agent Scans & Selects Top 1.
    2. Main Agent (Orchestrator) triggers processing for it.
    """
    from app.services.sales_agent import SalesAgent
    sales_agent = SalesAgent()
    
    # 1. Scan & Select
    scan_result = sales_agent.scan_for_rfps()
    valid_opps = scan_result.get("opportunities", [])
    
    if not valid_opps:
        raise HTTPException(status_code=404, detail="No valid RFPs found in scan.")
        
    # 2. Identify 1 RFP (The 'Hand-off')
    best_rfp = sales_agent.select_top_opportunity(valid_opps)
    
    # 3. Simulate "Sending to Main Agent" (Triggering Processing)
    # Since we don't have the PDF for the scraped item in this demo,
    # we simulate the ingestion by creating a job with the metadata.
    # In a real app, this would download the PDF from best_rfp['url'].
    
    job_id = f"AUTO-{best_rfp['id']}"
    
    # Create a Job Entry
    jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "filename": f"{best_rfp['id']}.pdf (Auto-Selected)",
        "metadata": best_rfp
    }
    
    # Trigger Task (Mocking file content since we can't download from gov site without auth)
    # We pass a dummy bytes object to represent the file
    dummy_content = b"Simulated PDF Content"
    background_tasks.add_task(process_rfp_task, job_id, dummy_content)
    
    return {
        "message": "Auto-Selection Complete. Main Agent processing started.",
        "selected_rfp": best_rfp,
        "job_id": job_id,
        "next_step": f"Check status at /api/v1/rfp/{job_id}/result"
    }

@router.post("/pipeline/magic-run")
async def run_pipeline_sync():
    """
    MAGIC ENDPOINT: Does EVERYTHING in one go (Blocking).
    1. Scan sales.
    2. Pick best RPF.
    3. Analyze it.
    4. Price it.
    5. Return FULL RESULT.
    """
    from app.services.sales_agent import SalesAgent
    from app.services.technical_agent import TechnicalAgent
    from app.services.pricing_agent import PricingAgent
    
    # 1. Sales Scan
    sales_agent = SalesAgent()
    scan_result = sales_agent.scan_for_rfps()
    valid_opps = scan_result.get("opportunities", [])
    if not valid_opps: return {"error": "No opportunities found"}
    
    # 2. Select Best
    best_rfp = sales_agent.select_top_opportunity(valid_opps)
    
    # 3. Simulate Download & Process (Tech Agent)
    # Using dummy content since we can't auth to gov site
    dummy_content = b"Simulated PDF Content for " + best_rfp['title'].encode()
    
    tech_agent = TechnicalAgent()
    tech_result = tech_agent.process_rfp(dummy_content)
    
    # 4. Pricing
    pricing_agent = PricingAgent()
    final_result = pricing_agent.calculate_pricing(tech_result)
    
    # 5. Return EVERYTHING
    return {
        "sales_intelligence": best_rfp,
        "technical_analysis": tech_result,
        "commercial_quote": final_result
    }
