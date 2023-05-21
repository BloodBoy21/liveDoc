from database.db import db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, constr
import uuid
from typing import Optional
from fastapi import HTTPException
from utils.security import get_password_hash, check_password_hash
from sqlalchemy.orm import Session


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
    config = relationship("UserConfig", back_populates="user")


class UserIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8)
    email: str = Field(..., regex=r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+$")


class UserOut(BaseModel):
    username: str
    email: str
    profile_picture: str = None
    user_id: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[
        constr(regex=r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+$")
    ] = None
    password: Optional[constr(min_length=8)] = None
    profile_picture: Optional[str] = None


class ValidateUserUpdate:
    def __init__(self, user: UserOut, db: Session, properties: UserUpdate):
        self.db = db
        self.userFields = properties
        self.user = user

    def check_fields(self):
        if not self.userFields.dict(exclude_unset=True):
            raise HTTPException(status_code=400, detail="No fields provided")
        self.check_username().check_email().check_password().encode_password()
        return self

    def check_username(self):
        if self.user.username == self.userFields.username:
            self.userFields.username = None
            return self
        db_user = (
            self.db.query(User)
            .filter(User.username == self.userFields.username)
            .first()
        )
        if db_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        return self

    def check_email(self):
        if self.user.email == self.userFields.email:
            self.userFields.email = None
            return self
        db_user = (
            self.db.query(User).filter(User.email == self.userFields.email).first()
        )
        if db_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        return self

    def check_password(self):
        if self.userFields.password:
            if len(self.userFields.password) < 8:
                raise HTTPException(status_code=400, detail="Password too short")
            self.__is_old_password()
        return self

    def __is_old_password(self):
        _user = self.db.query(User).filter(User.user_id == self.user.user_id).first()
        is_same_password = check_password_hash(self.userFields.password, _user.password)
        if is_same_password:
            raise HTTPException(status_code=400, detail="You can't use old password")

    def encode_password(self):
        if self.userFields.password:
            self.userFields.password = get_password_hash(self.userFields.password)
        return self

    def get_data(self):
        return {k: v for k, v in self.userFields.dict().items() if v is not None}

    def update_user(self):
        for key, value in self.get_data().items():
            setattr(self.user, key, value)
        self.db.commit()
        self.db.refresh(self.user)
        return self.user


def user_helper(user: User) -> UserOut:
    return UserOut(
        username=user.username,
        email=user.email,
        profile_picture=user.profile_picture,
        user_id=user.user_id,
    )
