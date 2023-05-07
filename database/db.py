import sqlalchemy
import os
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker

environment = os.getenv("ENVIRONMENT", "development")

if environment != "production":
    load_dotenv()

DATABASE_URI = os.getenv("DATABASE_URI")
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(DATABASE_URI)
db = declarative_base()
Session = sessionmaker(bind=engine)
session = None


def get_db():
    global session
    if session is None:
        session = Session()
    return session
