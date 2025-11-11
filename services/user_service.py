from sqlalchemy.orm import Session
from database.models import User, TokenBlacklist
from schemas.user import UserSignup, UserProfileUpdate
from auth.password import hash_password, verify_password
from auth.jwt_handler import create_access_token, create_refresh_token
from typing import Optional, Tuple


class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserSignup) -> User:
        user = User(
            email=user_data.email, hashed_password=hash_password(user_data.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = UserService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def update_profile(
        db: Session, user: User, profile_data: UserProfileUpdate
    ) -> User:
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def generate_tokens(user_id: int) -> Tuple[str, str]:
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        return access_token, refresh_token

    @staticmethod
    def blacklist_token(db: Session, token: str, user_id: int) -> None:
        blacklist_entry = TokenBlacklist(token=token, user_id=user_id)
        db.add(blacklist_entry)
        db.commit()
