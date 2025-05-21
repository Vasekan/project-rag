from backend.api.schemas.chat import ChatBaseSchema
from backend.utils.log import log_interaction
from backend.api.ai_realization import main # подключение к реализации ассистента


async def get_answer(chat: ChatBaseSchema):
    log_interaction(chat.source, chat.message, chat.message)
    message = main() # Тут вызов ассистента

    return {"message": f"{message}"}