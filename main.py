from fastapi import FastAPI, HTTPException
from database.db import engine, db
from database.mongo import database
from services.user_service import UserWithToken, db_user, create_user
from models.user import UserIn, UserLogin
from api.init import api_router
from cache.redis import init_redis

app = FastAPI()
app.include_router(api_router)


@app.on_event("startup")
async def startup():
    print("Starting up")
    db.metadata.create_all(bind=engine, checkfirst=True)
    await database.client.start_session()
    init_redis()


@app.post("/login", response_model=UserWithToken)
async def login(user: UserLogin):
    return db_user(user)


@app.post("/register", response_model=UserWithToken)
async def register(user: UserIn):
    return create_user(user)
