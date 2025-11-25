from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArticleBase(BaseModel):
    id: str
    title: str
    url: str
    summary: Optional[str] = None
    source: Optional[str] = None
    ecosystem_tag: Optional[str] = None
    legitimacy_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    created_at: datetime
    published_at: Optional[datetime] = None

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    wallet_address: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    last_login: datetime
    reputation_level: int = 1
    
    class Config:
        from_attributes = True

class BookmarkBase(BaseModel):
    user_address: str
    article_id: str

class BookmarkCreate(BookmarkBase):
    pass

class Bookmark(BookmarkBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True