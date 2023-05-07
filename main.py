from fastapi import FastAPI
from database.db import engine, db
from services.user_service import UserWithToken, db_user, create_user
from models.user import UserIn, UserLogin

app = FastAPI()


@app.on_event("startup")
def startup():
    print("Starting up")
    db.metadata.create_all(bind=engine, checkfirst=True)


@app.post("/login", response_model=UserWithToken)
async def login(user: UserLogin):
    return db_user(user)


@app.post("/register", response_model=UserWithToken)
async def register(user: UserIn):
    return create_user(user)
