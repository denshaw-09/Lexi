from fastapi import APIRouter
from supabase import create_client
from app.core.config import settings

router = APIRouter(prefix="/test", tags=["test"])
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

@router.get("/db-check")
async def test_database():
    """Test database connection"""
    try:
        result = supabase.table("articles").select("count", count="exact").execute()
        return {
            "status": "success",
            "database": "connected",
            "articles_count": result.count
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }

@router.get("/routes")
async def list_routes():
    """List all available API routes"""
    return {
        "endpoints": {
            "test": [
                "GET /api/v1/test/db-check",
                "GET /api/v1/test/routes"
            ],
            "feed": [
                "GET /api/v1/feed/",
                "GET /api/v1/feed/search"
            ],
            "user": [
                "POST /api/v1/user/auth/nonce",
                "POST /api/v1/user/auth/verify",
                "POST /api/v1/user/bookmarks",
                "GET /api/v1/user/{wallet_address}/bookmarks",
                "DELETE /api/v1/user/bookmarks/{bookmark_id}"
            ],
            "agent": [
                "POST /api/v1/agent/run",
                "GET /api/v1/agent/status"
            ]
        }
    }