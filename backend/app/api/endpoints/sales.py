from fastapi import APIRouter
from typing import List
from app.services.sales_agent import SalesAgent

router = APIRouter()
sales_agent = SalesAgent()

@router.post("/scan")
async def scan_web_for_rfps():
    """
    Triggers the Sales Agent to scan target URLs.
    """
    opportunities = sales_agent.scan_for_rfps()
    return {
        "message": "Scanning completed successfully",
        "found_opportunities": opportunities.get("opportunities_found", 0),
        "opportunities": opportunities
    }

@router.get("/opportunities")
async def get_opportunities():
    """
    Get the list of currently identified opportunities.
    """
    return sales_agent.scan_for_rfps()
