from pydantic import BaseModel, Field
from database.mongo import database
from datetime import datetime

DOC_COLLECTION = database.get_collection("docs")


class DocModel(BaseModel):
    title: str = Field(default="Untitled")
    content: str = Field(default="")
    user_id: str
    shared_with: list = []
    can_edit: list = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


def doc_helper(doc: DocModel) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "content": doc["content"],
        "user_id": doc["user_id"],
        "created_at": doc["created_at"],
        "updated_at": doc["updated_at"],
        "shared_with": doc["shared_with"],
        "can_edit": doc["can_edit"],
    }


class DocIn(BaseModel):
    title: str = Field(default="Untitled")
    content: str = Field(default="")


class DocCache(BaseModel):
    content: str = Field(default="")
    user_id: str = Field()
    updated_at: str = datetime.now().isoformat()
    doc_id: str = Field()
    version: int = Field(default=0)
