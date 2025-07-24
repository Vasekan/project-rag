from sqlalchemy import Column, Integer, String, Boolean
from backend.api.models.base import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))
    password = Column(String)
    is_active = Column(Boolean, default=True)
