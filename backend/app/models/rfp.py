from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RFPBase(BaseModel):
    title: str
    description: Optional[str] = None

class RFPCreate(RFPBase):
    pass

class RFPResponse(RFPBase):
    id: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProcessingStatus(BaseModel):
    job_id: str
    status: str
    stage: Optional[str] = None
    progress: int
    message: Optional[str] = None
