from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import User, UserCreate, Bookmark, BookmarkCreate
from app.core.security import verify_signature, generate_nonce
from app.core.config import settings
from supabase import create_client

router = APIRouter(prefix="/user", tags=["user"])
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

@router.post("/auth/nonce")
async def get_nonce(wallet_address: str):
    nonce = generate_nonce()
    # In production, store nonce with expiration
    return {"nonce": nonce, "message": f"Login to Nexus Agent. Nonce: {nonce}"}

@router.post("/auth/verify")
async def verify_wallet_signature(wallet_address: str, signature: str, message: str):
    if not verify_signature(wallet_address, signature, message):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Create or update user
    user_data = {
        "wallet_address": wallet_address.lower(),
        "last_login": "now()"
    }
    
    supabase.table("users").upsert(user_data).execute()
    
    return {"status": "success", "user": wallet_address}

@router.post("/bookmarks", response_model=Bookmark)
async def create_bookmark(bookmark: BookmarkCreate):
    try:
        # Check if article exists
        article = supabase.table("articles").select("id").eq("id", bookmark.article_id).execute()
        if not article.data:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Check if bookmark already exists
        existing = supabase.table("saved_bookmarks").select("*").eq("user_address", bookmark.user_address).eq("article_id", bookmark.article_id).execute()
        
        if existing.data:
            return existing.data[0]
        
        response = supabase.table("saved_bookmarks").insert(bookmark.dict()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating bookmark: {str(e)}")

@router.get("/{wallet_address}/bookmarks", response_model=list[Bookmark])
async def get_user_bookmarks(wallet_address: str):
    try:
        response = supabase.table("saved_bookmarks").select("*, articles(*)").eq("user_address", wallet_address).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching bookmarks: {str(e)}")

@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(bookmark_id: str, wallet_address: str):
    try:
        supabase.table("saved_bookmarks").delete().eq("id", bookmark_id).eq("user_address", wallet_address).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting bookmark: {str(e)}")