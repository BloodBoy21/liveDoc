from fastapi import APIRouter, Depends

from models.mongo.doc import DocIn
import services.doc_service as DocServices
from utils.auth import auth_user
from fastapi import HTTPException
from middleware.doc_middleware import doc_owner_middleware, doc_shared
from utils.middleware_wrapper import create_middleware_wrapper

router = APIRouter()

is_doc_owner = create_middleware_wrapper(callback=doc_owner_middleware)
is_doc_shared = create_middleware_wrapper(callback=doc_shared)


@router.post("/")
async def get_users(user=Depends(auth_user), doc: DocIn = None):
    """
    Create a new document.
    """
    return await DocServices.create_document(doc, user)


@router.get("/{user_id}")
async def get_users(user=Depends(auth_user), user_id: str = None):
    """
    Get all user documents.
    """
    if user_id != user.user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await DocServices.get_user_documents(user_id)


@router.delete("/{doc_id}")
@is_doc_owner
async def delete_doc(user=Depends(auth_user), doc_id: str = None, doc: dict = None):
    """
    Delete a document.
    """
    return await DocServices.delete_document(doc)


@router.put("/{doc_id}/guest/{shared_user}")
@is_doc_owner
async def share_doc(
    user=Depends(auth_user),
    doc_id: str = None,
    shared_user: str = None,
    doc: dict = None,
    options: dict = None,
):
    """
    Share a document with a user.
    """
    return await DocServices.update_doc_guest(doc, shared_user, options)


@router.post("/{doc_id}/viewer/{shared_user}")
@is_doc_owner
def add_shared_user(
    user=Depends(auth_user),
    doc_id: str = None,
    shared_user: str = None,
    doc: dict = None,
):
    """
    Add a user to a document.
    """
    return DocServices.add_shared_user(doc, shared_user)


@router.post("/{doc_id}/editor/{writer}")
@is_doc_owner
def add_editor(
    user=Depends(auth_user),
    doc_id: str = None,
    writer: str = None,
    doc: dict = None,
):
    """
    Add a user to a document.
    """
    return DocServices.add_editor(doc, writer)
