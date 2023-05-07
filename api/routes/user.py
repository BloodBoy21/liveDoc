from fastapi import APIRouter, Depends

from models.user import UserOut
from services.user_service import UserService
from utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=list[UserOut])
def get_users(user_service: UserService = Depends()):
    """
    Get all users.
    """
    return user_service.get_users()


