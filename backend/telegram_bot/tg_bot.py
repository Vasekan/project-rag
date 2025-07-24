from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from backend.utils.log import log_interaction
from backend.api.ai_realization.task_assist import get_relevant_chunks, generate_answer_from_context

COLLECTION_NAME = "documents"


bot = Bot(
    token= '7906599142:AAE4FnO01P09FYj5PD-j8vLBeDAEqbEkuCc',
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Задайте вопрос, и ИИ на него ответит.")

@router.message()
async def handle_message(message: types.Message):
    user_message = message.text
    results = get_relevant_chunks(user_message, COLLECTION_NAME)
    if not results:
        return "Ничего не найдено."
    output = ["+" * 100]
    for result in results:
        output.append(f"Релевантность: {result.score:.3f}")
        output.append(f"Документ: {result.payload.get('doc_name')}")
        output.append(f"Текст чанка: {result.payload.get('text')[:100]}...") 
        output.append("+" * 100)

    reply = generate_answer_from_context(user_message, results)  # Тут вызов ассистента
    log_interaction(source="telegram", question=user_message, answer=reply)
    await message.answer(reply)

dp.include_router(router)