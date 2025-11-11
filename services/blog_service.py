from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from database.models import Blog
from schemas.blog import BlogCreate, BlogUpdate
from typing import List, Optional
from datetime import datetime, timezone


class BlogService:
    @staticmethod
    def create_blog(db: Session, blog_data: BlogCreate, author_id: int) -> Blog:
        blog = Blog(
            title=blog_data.title,
            content=blog_data.content,
            category=blog_data.category,
            author_id=author_id,
        )
        db.add(blog)
        db.commit()
        db.refresh(blog)
        return blog

    @staticmethod
    def get_blog_by_id(db: Session, blog_id: int) -> Optional[Blog]:
        return db.query(Blog).filter(Blog.id == blog_id).first()

    @staticmethod
    def get_recent_blogs(db: Session, skip: int = 0, limit: int = 10) -> List[Blog]:
        return (
            db.query(Blog)
            .order_by(Blog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_blogs_by_category(
        db: Session, category: str, skip: int = 0, limit: int = 10
    ) -> List[Blog]:
        return (
            db.query(Blog)
            .filter(Blog.category == category)
            .order_by(Blog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def search_blogs(
        db: Session, query: str, skip: int = 0, limit: int = 10
    ) -> List[Blog]:
        search_pattern = f"%{query}%"

        blogs = (
            db.query(Blog)
            .filter(
                or_(
                    func.lower(Blog.title).like(func.lower(search_pattern)),
                    func.lower(Blog.content).like(func.lower(search_pattern)),
                    func.lower(Blog.category).like(func.lower(search_pattern)),
                )
            )
            .order_by(Blog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return blogs

    @staticmethod
    def update_blog(db: Session, blog: Blog, blog_data: BlogUpdate) -> Blog:
        update_data = blog_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(blog, field, value)
        blog.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(blog)
        return blog

    @staticmethod
    def delete_blog(db: Session, blog: Blog) -> None:
        db.delete(blog)
        db.commit()
