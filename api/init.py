from fastapi import APIRouter

from api.routes import user, doc

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(doc.router, prefix="/docs", tags=["docs"])
