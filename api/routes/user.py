from fastapi import APIRouter, Depends

from models.user import UserOut
import services.user_service as UserServices
from utils.auth import auth_user

router = APIRouter()


@router.get("/", response_model=list[UserOut])
def get_users(user=Depends(auth_user)):
    """
    Get all users.
    """
    return UserServices.get_users()


@router.get("/me/{user_id}", response_model=UserOut)
async def get_user(user_id: str, user=Depends(auth_user)):
    """
    Get a specific user.
    """
    user_found = UserServices.get_user_by_id(user_id=user_id)
    if user_id != user.user_id:
        return UserServices.user_plubic(user_found)
    return user
