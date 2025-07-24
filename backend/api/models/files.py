from sqlalchemy import Column, Integer, String, Boolean

from backend.api.models.base import Base

class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(50))
    is_load = Column(Boolean, default=False)
