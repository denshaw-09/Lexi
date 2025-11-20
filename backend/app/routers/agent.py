from fastapi import APIRouter, HTTPException
from app.agents.runner import run_agent

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/run")
async def trigger_agent():
    """Manually trigger the content scraping agent"""
    try:
        result = await run_agent()
        return {
            "status": "success", 
            "message": "Content scraping agent executed successfully",
            "articles_stored": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@router.get("/status")
async def agent_status():
    """Get agent status"""
    return {
        "status": "running", 
        "schedule": "every_30_minutes",
        "description": "Web3 content scraping agent"
    }