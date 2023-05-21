from fastapi import Request
from fastapi.exceptions import HTTPException
from bson.objectid import ObjectId
from models.mongo.doc import DOC_COLLECTION, doc_helper
from utils.auth import auth_user
from models.user import UserOut


async def is_same_user(user_id: str, user: UserOut, **kwargs):
    if user_id != user.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
