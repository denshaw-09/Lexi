from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ArticleBase(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    source: str
    ecosystem_tag: str
    legitimacy_score: float

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