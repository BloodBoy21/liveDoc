from database.db import db
from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel
import uuid


def generate_uuid():
    return str(uuid.uuid4())[:8]


class User(db):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(8), unique=True, index=True, default=generate_uuid, nullable=False
    )
    username = Column(String(20), unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String())
    profile_picture = Column(String, default="")


class UserIn(BaseModel):
    username: str
    password: str
    email: str


class UserOut(BaseModel):
    username: str
    email: str
    profile_picture: str = None
    user_id: str


class UserLogin(BaseModel):
    email: str
    password: str


def user_helper(user: User) -> UserOut:
    return UserOut(
        username=user.username,
        email=user.email,
        profile_picture=user.profile_picture,
        user_id=user.user_id,
    )
