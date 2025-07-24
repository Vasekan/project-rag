from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from backend.utils.log import log_interaction
from backend.api.ai_realization.main import main # подключение к реализации ассистента


bot = Bot(
    token= '7906599142:AAE4FnO01P09FYj5PD-j8vLBeDAEqbEkuCc',
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f"Выберите действие:\n"
        f"1. Загрузить документы в базу\n"
        f"2. Удалить документ по имени файла (Пример: 2 example.txt)\n"
        f"3. Удалить вектор по ID (Пример: 3 123456)\n"
        f"4. Посмотреть загруженные документы\n"
        f"5. Задать вопрос (Пример: 5 Как дела?)\n"
        f"6. Проверить, загружен ли документ с именем 'Имя' (Пример: 6 example.txt)"
    )

@router.message()
async def handle_message(message: types.Message):
    user_message = message.text
    reply = main(user_message) # Тут вызов ассистента
    log_interaction(source="telegram", question=user_message, answer=reply)
    await message.answer(reply)

dp.include_router(router)
