from models.user import (
    UserIn,
    UserOut,
    User,
    UserLogin,
    user_helper,
    UserUpdate,
    ValidateUserUpdate,
)
from models.user_config import UserConfig, user_config_helper
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


class ParseUserConfig:
    def __init__(self, user_config: UserConfig, user: UserOut):
        self.user_config = user_config
        self.user = user

    def add_email(self):
        if not self.user_config.show_email:
            self.user.email = ""
        return self


def user_exists(user: UserIn) -> bool:
    db_user = db.query(User).filter(User.email == user.email).first()
    db_username = db.query(User).filter(User.username == user.username).first()
    if db_user or db_username:
        return True
    return False


def create_user_config(user_id: str):
    db_user_config = UserConfig(user_id=user_id)
    db.add(db_user_config)
    db.commit()
    db.refresh(db_user_config)
    return db_user_config


def create_user(user: UserIn) -> UserWithToken:
    if user_exists(user):
        raise HTTPException(status_code=400, detail="User already exists")
    if not password_length(user.password):
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters"
        )
    hashed_password = get_password_hash(user.password)
    user.password = hashed_password
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    create_user_config(db_user.user_id)
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


def user_plubic(user: UserOut):
    user_config = (
        db.query(UserConfig).filter(UserConfig.user_id == user.user_id).first()
    ) or UserConfig(user_id=user.user_id)
    parser = ParseUserConfig(user_config, user)
    return parser.add_email().user


def update_user_config(user_id: str, config: dict):
    db_user_config = db.query(UserConfig).filter(UserConfig.user_id == user_id).first()
    if not db_user_config:
        raise HTTPException(status_code=404, detail="User config not found")
    for key, value in config.items():
        setattr(db_user_config, key, value)
    db.commit()
    db.refresh(db_user_config)
    return user_config_helper(db_user_config)


def update_user(user: UserOut, properties: UserUpdate) -> UserOut:
    db_user = db.query(User).filter(User.user_id == user.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    update_user = ValidateUserUpdate(user=db_user, properties=properties, db=db)
    update_user.check_fields().update_user()
    return user_helper(db_user)
