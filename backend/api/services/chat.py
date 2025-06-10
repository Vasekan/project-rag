from backend.api.schemas.chat import ChatBaseSchema
from backend.utils.log import log_interaction
from backend.api.ai_realization.task_assist import get_relevant_chunks, generate_answer_from_context


COLLECTION_NAME = "documents"

async def get_answer(chat: ChatBaseSchema):
    results = get_relevant_chunks(chat.message, COLLECTION_NAME)
    if not results:
        return "Ничего не найдено."
    output = ["+" * 100]
    for result in results:
        output.append(f"Релевантность: {result.score:.3f}")
        output.append(f"Документ: {result.payload.get('doc_name')}")
        output.append(f"Текст чанка: {result.payload.get('text')[:100]}...") 
        output.append("+" * 100)

    message = generate_answer_from_context(chat.message, results) # Тут вызов ассистента
    log_interaction(chat.source, chat.message, message)

    return {"message": f"{message}"}