import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import os
from services.user_service import get_user_by_id

JWT_SECRET = os.getenv("JWT_SECRET")


async def auth_user(auth: str = Depends(HTTPBearer())) -> str:
    try:
        payload = jwt.decode(auth.credentials, JWT_SECRET, algorithms=["HS256"])
        return get_user_by_id(payload["user_id"])
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token",
        )
    except jwt.exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
