from backend.api.schemas.chat import ChatBaseSchema
from backend.utils.log import log_interaction
from backend.api.ai_realization.task_assist import get_relevant_chunks, generate_answer_from_context
from backend.api.ai_realization.qdrant_manager import list_documents


COLLECTION_NAME = "documents"

async def get_answer(chat: ChatBaseSchema, current_user):
    results = get_relevant_chunks(chat.message, current_user.id, COLLECTION_NAME)
    if not results:
        return {"message": "Ничего не найдено."}
    output = ["+" * 100]
    for result in results:
        output.append(f"Релевантность: {result.score:.3f}")
        output.append(f"Документ: {result.payload.get('doc_name')}")
        output.append(f"Текст чанка: {result.payload.get('text')[:100]}...") 
        output.append("+" * 100)

    message = generate_answer_from_context(chat.message, results) # Тут вызов ассистента
    # message = list_documents(current_user.id)
    log_interaction(chat.source, chat.message, message)

    return {"message": f"{message}"}