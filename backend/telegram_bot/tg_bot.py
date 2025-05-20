from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from backend.utils.log import log_interaction


bot = Bot(
    token= '7357247017:AAGzqgnyQry_NnfKRvrQ_Pw2jZdX1_a7c3Q',
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Напиши мне вопрос — я постараюсь ответить.")

@router.message()
async def handle_message(message: types.Message):
    user_message = message.text
    reply = user_message  # Тут вызов ассистента
    log_interaction(source="telegram", question=user_message, answer=reply)
    await message.answer(reply)

dp.include_router(router)
