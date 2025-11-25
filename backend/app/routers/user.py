from fastapi import APIRouter, HTTPException, Depends, Body
from app.models.schemas import User, UserCreate, Bookmark, BookmarkCreate
from app.core.security import verify_signature, generate_nonce
from app.core.config import settings
from supabase import create_client
from eth_account.messages import encode_defunct
from eth_account import Account
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/user", tags=["user"])
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Request Models
class AuthRequest(BaseModel):
    wallet_address: str

class VerifyRequest(BaseModel):
    wallet_address: str
    signature: str

@router.post("/auth/nonce")
async def get_nonce(request: AuthRequest):
    address = request.wallet_address.lower()
    
    # 1. Check if user exists
    user = supabase.table("users").select("*").eq("wallet_address", address).execute()
    
    nonce = str(uuid.uuid4())
    
    if not user.data:
        # Create new user
        supabase.table("users").insert({
            "wallet_address": address,
            "nonce": nonce
        }).execute()
    else:
        # Update nonce
        supabase.table("users").update({"nonce": nonce}).eq("wallet_address", address).execute()
        
    return {"nonce": nonce}

@router.post("/auth/verify")
async def verify_signature(request: VerifyRequest):
    address = request.wallet_address.lower()
    
    # 1. Get user and nonce from DB
    user_response = supabase.table("users").select("nonce").eq("wallet_address", address).execute()
    
    if not user_response.data:
        raise HTTPException(status_code=400, detail="User not found")
        
    stored_nonce = user_response.data[0]['nonce']
    
    # 2. Reconstruct the EXACT message the frontend signed
    # MUST MATCH FRONTEND EXACTLY (Spaces, punctuation, everything)
    message_text = f"Login to Lexi. Nonce: {stored_nonce}"
    
    try:
        # 3. Verify Signature
        # Encode as EIP-191 (Ethereum standard)
        encoded_msg = encode_defunct(text=message_text)
        recovered_address = Account.recover_message(encoded_msg, signature=request.signature)
        
        if recovered_address.lower() == address:
            # Success! Generate a session token or just return success
            # Ideally, clear the nonce here to prevent replay attacks
            new_nonce = str(uuid.uuid4())
            supabase.table("users").update({"nonce": new_nonce}).eq("wallet_address", address).execute()
            
            return {
                "authenticated": True, 
                "user": {"address": address}
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid signature")
            
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Signature verification failed")

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