from backend.api.schemas.chat import ChatBaseSchema
from backend.utils.log import log_interaction
from backend.api.ai_realization.main import main # подключение к реализации ассистента


async def get_answer(chat: ChatBaseSchema):
    message = main(chat.message) # Тут вызов ассистента
    log_interaction(chat.source, chat.message, message)

    return {"message": f"{message}"}