from bson import ObjectId
from models.mongo.doc import (
    DocIn,
    DOC_COLLECTION,
    doc_helper,
    DocModel,
    DocCache,
    DocUpdate,
)
from models.user import UserOut
from fastapi import HTTPException
from docx import Document
from fastapi.responses import FileResponse
import os
from cache.redis import get_redis
import json
from datetime import datetime

cache = get_redis()
decode_history = lambda history: json.loads(history.decode("utf-8"))
encode_history = lambda history: json.dumps(history).encode("utf-8")
EXP_TIME = 60 * 60 * 2  # 2 hours


async def create_document(doc: DocIn, user: UserOut):
    doc_with_user = DocModel(**doc.dict(), user_id=user.user_id)
    new_doc = await DOC_COLLECTION.insert_one(doc_with_user.dict())
    return doc_helper(await DOC_COLLECTION.find_one({"_id": new_doc.inserted_id}))


async def update_document(doc_id: str, user: UserOut, doc: DocUpdate):
    if doc.version:
        reset_from_pivot(doc_id, user, doc.version)
    original_doc = await DOC_COLLECTION.find_one({"_id": ObjectId(doc_id)})
    original_doc = doc_helper(original_doc)
    doc.content = doc.content or original_doc["content"]
    doc.title = doc.title or original_doc["title"]
    update_data = {
        "updated_at": datetime.now(),
        **doc.dict(exclude_unset=True),
    }
    await DOC_COLLECTION.update_one({"_id": ObjectId(doc_id)}, {"$set": update_data})
    if not is_not_in_cache(doc_id=doc_id, user=user, content=doc.content):
        save_in_cache(doc_id=doc_id, user=user, content=doc.content)
    doc_updated = await DOC_COLLECTION.find_one({"_id": ObjectId(doc_id)})
    doc_updated = doc_helper(doc_updated)
    return doc_updated


async def get_user_documents(user_id):
    docs = []
    async for doc in DOC_COLLECTION.find(
        {
            "$or": [
                {"user_id": user_id},
                {"shared_with": {"$in": [user_id]}},
            ]
        }
    ):
        docs.append(doc_helper(doc))
    return docs


async def delete_document(doc):
    await DOC_COLLECTION.delete_one({"_id": ObjectId(doc["id"])})
    return {"id": doc["id"], "succeed": True}


async def add_shared_user(doc: dict, shared_user: str):
    if shared_user in doc["shared_with"]:
        raise HTTPException(status_code=400, detail="User already shared")
    await DOC_COLLECTION.update_one(
        {"_id": ObjectId(doc["id"])}, {"$push": {"shared_with": shared_user}}
    )
    updated_doc = await DOC_COLLECTION.find_one({"_id": ObjectId(doc["id"])})
    return {"shared_with": updated_doc["shared_with"], "succeed": True}


async def add_editor(doc: dict, writer: str):
    if writer in doc["can_edit"]:
        raise HTTPException(status_code=400, detail="User already has write access")
    await DOC_COLLECTION.update_one(
        {"_id": ObjectId(doc["id"])},
        {"$push": {"shared_with": writer, "can_edit": writer}},
    )
    doc_updated = await DOC_COLLECTION.find_one({"_id": ObjectId(doc["id"])})
    doc_updated = doc_helper(doc_updated)
    return {
        "shared_with": doc_updated["shared_with"],
        "can_edit": doc_updated["can_edit"],
        "succeed": True,
    }


async def remove_shared_user(doc: dict, shared_user: str):
    if shared_user not in doc["shared_with"]:
        raise HTTPException(status_code=400, detail="User not shared")
    await DOC_COLLECTION.update_one(
        {"_id": ObjectId(doc["id"])}, {"$pull": {"shared_with": shared_user}}
    )
    updated_doc = await DOC_COLLECTION.find_one({"_id": ObjectId(doc["id"])})
    return {"shared_with": updated_doc["shared_with"], "succeed": True}


async def remove_editor(doc: dict, writer: str):
    if writer not in doc["can_edit"]:
        raise HTTPException(status_code=400, detail="User not editor")
    await DOC_COLLECTION.update_one(
        {"_id": ObjectId(doc["id"])}, {"$pull": {"can_edit": writer}}
    )
    await remove_shared_user(doc, writer)
    updated_doc = await DOC_COLLECTION.find_one({"_id": ObjectId(doc["id"])})
    return {"can_edit": updated_doc["can_edit"], "succeed": True}


async def update_doc_guest(doc, guest: str, options: dict):
    doc_id = doc["id"]
    operation = options.get("operation", None)
    type = options.get("type", None)
    if not type:
        raise HTTPException(status_code=400, detail="Type not specified")
    add_functions = {
        "viewer": add_shared_user,
        "editor": add_editor,
    }
    remove_functions = {
        "viewer": remove_shared_user,
        "editor": remove_editor,
    }
    operation_functions = {
        "add": add_functions,
        "remove": remove_functions,
    }
    if not operation:
        raise HTTPException(status_code=400, detail="Operation not specified")
    if operation not in operation_functions:
        raise HTTPException(status_code=400, detail="Invalid operation")
    if type not in operation_functions[operation]:
        raise HTTPException(status_code=400, detail="Invalid type")
    await operation_functions[operation][type](doc, guest)
    return {"id": doc_id, **options, "succeed": True}


async def download_document(doc_id) -> FileResponse:
    doc = await DOC_COLLECTION.find_one({"_id": ObjectId(doc_id)})
    doc = doc_helper(doc)
    data = doc["content"].split("\n")
    title = doc["title"].replace(" ", "_")
    title = f"{title}.docx"
    route = f"{os.getcwd()}/temp/{title}"
    document = Document()
    for paragraph in data:
        document.add_paragraph(paragraph)
    document.save(route)
    return FileResponse(
        route,
        filename=title,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def save_in_cache(doc_id: str, user: UserOut, content: str):
    key = f"{user.user_id}:{doc_id}"
    if not cache.exists(key):
        doc = DocCache(content=content, user_id=user.user_id, doc_id=doc_id)
        cache.set(key, encode_history([doc.dict()]), ex=EXP_TIME)
        return {"id": doc_id, "succeed": True}
    history = cache.get(key)
    history = decode_history(history)
    last_doc = DocCache(**history[0])
    last_version = int(last_doc.version)
    history.insert(
        0,
        DocCache(
            content=content,
            user_id=user.user_id,
            doc_id=doc_id,
            version=last_version + 1,
        ).dict(),
    )
    cache.set(key, encode_history(history), ex=EXP_TIME)
    return {"id": doc_id, "succeed": True}


def get_from_cache(doc_id: str, user: UserOut, version: int):
    key = f"{user.user_id}:{doc_id}"
    if not cache.exists(key):
        return None
    history = cache.get(key)
    history = decode_history(history)
    if version is None:
        return DocCache(**history[0])
    try:
        return DocCache(**history[version])
    except IndexError:
        return DocCache(**history[0])


def reset_cache(doc_id: str, user: UserOut):
    key = f"{user.user_id}:{doc_id}"
    cache.delete(key)
    return {"id": doc_id, "succeed": True}


def reset_from_pivot(doc_id: str, user: UserOut, version: int):
    key = f"{user.user_id}:{doc_id}"
    history = cache.get(key)
    if not history:
        return {"id": doc_id, "succeed": True}
    history = decode_history(history)
    cache.set(key, encode_history(history[version:]), ex=EXP_TIME)
    return {"id": doc_id, "succeed": True}


def is_not_in_cache(content: str, user: UserOut, doc_id: str):
    key = f"{user.user_id}:{doc_id}"
    if not cache.exists(key):
        return False
    history = cache.get(key)
    history = decode_history(history)
    last_doc = DocCache(**history[0])
    return last_doc.content == content
