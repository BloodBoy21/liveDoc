from fastapi import APIRouter, Depends

from models.user import UserOut, UserUpdate
import services.user_service as UserServices
from utils.auth import auth_user
from middleware.user_middleware import is_same_user
from utils.middleware_wrapper import create_middleware_wrapper

router = APIRouter()

is_same_user = create_middleware_wrapper(callback=is_same_user)


@router.get("/", response_model=list[UserOut])
def get_users(user: UserOut = Depends(auth_user)):
    """
    Get all users.
    """
    return UserServices.get_users()


@router.get("/me", response_model=UserOut)
async def get_user_me(user: UserOut = Depends(auth_user)):
    """
    Get a specific user.
    """
    return UserServices.get_user_by_id(user_id=user.user_id)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str, user: UserOut = Depends(auth_user)):
    """
    Get a specific user.
    """
    user_found = UserServices.get_user_by_id(user_id=user_id)
    if user_id != user.user_id:
        return UserServices.user_plubic(user_found)
    return user


@router.put("/{user_id}/config")
@is_same_user
async def update_user_config(
    user_id: str, config: dict, user: UserOut = Depends(auth_user)
) -> dict:
    """
    Update a user's configuration.
    """
    return UserServices.update_user_config(user_id=user_id, config=config)


@router.put("/{user_id}/info")
@is_same_user
async def update_user_info(
    user_id: str, properties: UserUpdate, user: UserOut = Depends(auth_user)
):
    """
    Update a user's configuration.
    """
    return UserServices.update_user(user=user, properties=properties)
