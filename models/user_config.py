from database.db import db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel


class UserConfig(db):
    __tablename__ = "user_config"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(8), ForeignKey("users.user_id"), unique=True, nullable=False
    )
    user = relationship("User", back_populates="config")
    show_email = Column(Boolean, default=False)
    show_full_name = Column(Boolean, default=False)
