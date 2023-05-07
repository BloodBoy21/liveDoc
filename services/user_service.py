from models.user import UserIn, UserOut, User, UserLogin, user_helper
from utils.security import (
    get_password_hash,
    generate_token,
    check_password_hash,
    password_length,
)
from database.db import get_db
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()
db = get_db()


class UserWithToken(UserOut):
    token: str

    @staticmethod
    def from_orm(user: User) -> "UserWithToken":
        return UserWithToken(
            user_id=user.user_id,
            email=user.email,
            token=generate_token(user.user_id),
            username=user.username,
            profile_picture=user.profile_picture,
        )


def user_exists(user: UserIn) -> bool:
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        return True
    return False


def create_user(user: UserIn) -> UserWithToken:
    if user_exists(user):
        raise HTTPException(status_code=400, detail="User already exists")
    if not password_length(user.password):
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters"
        )
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password.decode("utf-8")
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserWithToken.from_orm(db_user)


def db_user(user: UserLogin) -> UserWithToken:
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not check_password_hash(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return UserWithToken.from_orm(db_user)


def get_user_by_id(user_id: str) -> UserOut:
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(db_user)


def get_users() -> list[UserOut]:
    all_users = db.query(User).all()
    return [user_helper(user) for user in all_users]
