from bson import ObjectId
from models.mongo.doc import DocIn, DOC_COLLECTION, doc_helper, DocModel
from models.user import UserOut
from fastapi import HTTPException


async def create_document(doc: DocIn, user: UserOut):
    doc_with_user = DocModel(**doc.dict(), user_id=user.user_id)
    new_doc = await DOC_COLLECTION.insert_one(doc_with_user.dict())
    return doc_helper(await DOC_COLLECTION.find_one({"_id": new_doc.inserted_id}))


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
    return {"shared_with": doc["shared_with"], "succeed": True}


# TODO: return updated doc
async def add_editor(doc: dict, writer: str):
    if writer in doc["can_edit"]:
        raise HTTPException(status_code=400, detail="User already has write access")
    doc_updated = await DOC_COLLECTION.find_one_and_update(
        {"_id": ObjectId(doc["id"])},
        {"$push": {"shared_with": writer, "can_edit": writer}},
    )
    doc_updated = doc_helper(doc_updated)
    return {
        "shared_with": doc_updated["shared_with"],
        "can_edit": doc_updated["can_edit"],
        "succeed": True,
    }


async def update_doc_guest(doc, options: dict):
    doc_id = doc["id"]
    await DOC_COLLECTION.update_one({"_id": ObjectId(doc_id)}, {"$set": options})
    return {"id": doc_id, **options, "succeed": True}
