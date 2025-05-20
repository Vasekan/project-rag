from backend.api.schemas.chat import ChatBaseSchema
from backend.utils.log import log_interaction


async def get_answer(chat: ChatBaseSchema):
    log_interaction(chat.source, chat.message, chat.message)
    message = chat.message 
    return {"message": f"{message}"}