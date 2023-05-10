from fastapi import Request
from fastapi.exceptions import HTTPException
from bson.objectid import ObjectId
from models.mongo.doc import DOC_COLLECTION, doc_helper
from utils.auth import auth_user
from models.user import UserOut


async def doc_owner_middleware(doc_id: str, user: UserOut, **kwargs):
    doc = await DOC_COLLECTION.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc = doc_helper(doc)
    if doc["user_id"] != user.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"doc": doc}


async def doc_shared(doc: dict, shared_user: str, **kwargs):
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if shared_user not in doc["shared_with"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"doc": doc}


async def can_download(doc_id: str, user: UserOut, **kwargs):
    doc = await DOC_COLLECTION.find_one({"_id": ObjectId(doc_id)})
    doc = doc_helper(doc)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    is_owner = doc["user_id"] == user.user_id
    is_shared = user.user_id in doc["shared_with"]
    if not (is_owner or is_shared):
        raise HTTPException(status_code=401, detail="Unauthorized")


async def can_write(doc_id: str, user: UserOut, **kwargs):
    doc = await DOC_COLLECTION.find_one({"_id": ObjectId(doc_id)})
    doc = doc_helper(doc)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    is_owner = doc["user_id"] == user.user_id
    is_editor = user.user_id in doc["can_edit"]
    if not (is_owner or is_editor):
        raise HTTPException(status_code=401, detail="Unauthorized")
