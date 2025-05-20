from pydantic import BaseModel
from enum import Enum


class Source(str, Enum):
    web = "web"
    telegram = "telegram"

class ChatBaseSchema(BaseModel):
    message: str
    source: Source

