import bcrypt
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET")

get_password_hash = lambda password: bcrypt.hashpw(
    password.encode("utf-8"), bcrypt.gensalt()
)


def check_password_hash(user, db_user):
    return bcrypt.checkpw(user.encode("utf-8"), db_user.encode("utf-8"))


def generate_token(user_id: int) -> str:
    payload = {"user_id": user_id}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


def password_length(password: str) -> bool:
    return len(password) >= 8
