from sqlalchemy.orm import Session

from core import get_password_hash
from models.user import User
from schemas import user_schema
from schemas.user_schema import UserCreate


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
