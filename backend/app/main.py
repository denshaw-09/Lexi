from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.routers import feed, user, agent
from app.core.config import settings
from app.agents.runner import start_scheduler, run_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the agent scheduler
    print("🚀 Starting Lexi Agent Scheduler...")
    start_scheduler()
    
    # Start the scheduler in background
    asyncio.create_task(run_scheduler())
    
    yield  # App runs here
    
    # Shutdown: Clean up resources
    print("🛑 Shutting down Lexi Agent...")

app = FastAPI(
    title="Lexi Agent API",
    version="1.0.0",
    description="AI-powered Web3 content aggregator with retro interface",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(feed.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")
# app.include_router(test.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Lexi Agent API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "lexi-agent-api"}

@app.get("/api")
async def api_root():
    return {"message": "Lexi Agent API", "endpoints": {
        "feed": "/api/v1/feed",
        "user": "/api/v1/user",
        "agent": "/api/v1/agent",
        "test": "/api/v1/test"
    }}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )