from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BlogCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Blog post title")
    content: str = Field(..., min_length=1, description="Blog post content")
    category: str = Field(..., min_length=1, max_length=50, description="Blog category")


class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, min_length=1, max_length=50)


class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
