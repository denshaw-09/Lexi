from fastapi import APIRouter, HTTPException, Query
from app.core.config import settings
from app.models.schemas import Article
from typing import List
from supabase import create_client

router = APIRouter(prefix="/feed", tags=["feed"])
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

@router.get("/", response_model=List[Article])
async def get_feed(
    ecosystem: str = Query(None, description="Filter by ecosystem"),
    limit: int = Query(30, description="Number of articles to return")
):
    try:
        query = supabase.table("articles").select("*").order("published_at", desc=True).limit(limit)
        
        if ecosystem and ecosystem.lower() != "all":
            query = query.eq("ecosystem_tag", ecosystem.lower())
        
        response = query.execute()
        return response.data
    except Exception as e:
        print(f"Feed Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching feed: {str(e)}")

@router.get("/search")
async def search_articles(q: str = Query(..., description="Search query")):
    try:
        response = supabase.table("articles")\
            .select("*")\
            .or_(f"title.ilike.%{q}%,summary.ilike.%{q}%")\
            .order("published_at", desc=True)\
            .execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching articles: {str(e)}")