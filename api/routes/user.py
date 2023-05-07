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
