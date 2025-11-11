from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from database.connection import get_db
from database.models import User
from schemas.blog import BlogCreate, BlogUpdate, BlogResponse
from services.blog_service import BlogService
from auth.dependencies import get_current_user

router = APIRouter(prefix="/api/blogs", tags=["Blogs"])

SKIP_DESCRIPTION = "Number of records to skip"
LIMIT_DESCRIPTION = "Number of records to return"
BLOG_NOT_FOUND_MSG = "Blog post not found"


@router.post("", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
async def create_blog(
    blog_data: BlogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    blog = BlogService.create_blog(db, blog_data, current_user.id)
    return blog


@router.get("/search", response_model=List[BlogResponse])
async def search_blogs(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description=SKIP_DESCRIPTION),
    limit: int = Query(10, ge=1, le=100, description=LIMIT_DESCRIPTION),
    db: Session = Depends(get_db),
):
    blogs = BlogService.search_blogs(db, q, skip, limit)
    return blogs


@router.get("", response_model=List[BlogResponse])
async def list_blogs(
    skip: int = Query(0, ge=0, description=SKIP_DESCRIPTION),
    limit: int = Query(10, ge=1, le=100, description=LIMIT_DESCRIPTION),
    db: Session = Depends(get_db),
):
    blogs = BlogService.get_recent_blogs(db, skip, limit)
    return blogs


@router.get("/category/{category}", response_model=List[BlogResponse])
async def list_blogs_by_category(
    category: str,
    skip: int = Query(0, ge=0, description=SKIP_DESCRIPTION),
    limit: int = Query(10, ge=1, le=100, description=LIMIT_DESCRIPTION),
    db: Session = Depends(get_db),
):
    blogs = BlogService.get_blogs_by_category(db, category, skip, limit)
    return blogs


@router.get("/{blog_id}", response_model=BlogResponse)
async def get_blog(blog_id: int, db: Session = Depends(get_db)):
    """Get a specific blog post"""
    blog = BlogService.get_blog_by_id(db, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BLOG_NOT_FOUND_MSG,
        )
    return blog


@router.put("/{blog_id}", response_model=BlogResponse)
async def update_blog(
    blog_id: int,
    blog_data: BlogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    blog = BlogService.get_blog_by_id(db, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BLOG_NOT_FOUND_MSG,
        )

    if blog.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this blog post",
        )

    updated_blog = BlogService.update_blog(db, blog, blog_data)
    return updated_blog


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
    blog_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    blog = BlogService.get_blog_by_id(db, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BLOG_NOT_FOUND_MSG,
        )

    if blog.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this blog post",
        )
    BlogService.delete_blog(db, blog)
    return None
