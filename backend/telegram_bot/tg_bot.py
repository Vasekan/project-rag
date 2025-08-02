import os

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from sqlalchemy import select, and_, update

from backend.db import AsyncSessionLocal, get_session
from backend.utils.log import log_interaction
from backend.api.ai_realization.task_assist import get_relevant_chunks, generate_answer_from_context
from backend.api.models.user import User
from backend.api.models.files import File
from backend.api.services.auth import hashed_password, verify_password
from backend.telegram_bot.tg_files import upload_files, get_files, delete_files, upload_chunks, delete_chunks


COLLECTION_NAME = "documents"


bot = Bot(
    token= '7357247017:AAGzqgnyQry_NnfKRvrQ_Pw2jZdX1_a7c3Q',
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

class Registration(StatesGroup):
    username = State()
    first_name = State()
    last_name = State()
    password = State()

class Login(StatesGroup):
    username = State()
    password = State()

class FileUpload(StatesGroup):
    waiting_for_file = State()

dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User.username).where(User.tg_id == message.from_user.id)
        )
        username = result.scalar()

    if username:
        kb = [
            [types.KeyboardButton(text="Загрузить файл")],
            [types.KeyboardButton(text="Список файлов")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(f"Здравствуйте, {message.from_user.first_name}!\nНапишите вопрос ИИ или настройте файлы для дальнейшей работы.", reply_markup=keyboard)
    else:
        kb = [
            [types.KeyboardButton(text="Вход")],
            [types.KeyboardButton(text="Регистрация")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Вы не зарегистрированы.")
        await message.answer("Выберите действие:", reply_markup=keyboard)


@router.message(F.text.lower() == "вход")
async def login_start(message: types.Message, state: FSMContext):
    await message.answer("Введите ваш username:")
    await state.set_state(Login.username)

@router.message(Login.username)
async def login_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Введите ваш пароль:")
    await state.set_state(Login.password)

@router.message(Login.password)
async def login_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    entered_plain = message.text

    async with AsyncSessionLocal() as session:
        stmt = await session.execute(select(User).where(User.username == data["username"]))
        user = stmt.scalar_one_or_none()

        if not user or not verify_password(entered_plain, user.password):
            await message.answer("Неверный логин или пароль.")
            await state.clear()
            return
        
        stmt = update(User).where(User.username == data["username"]).values(tg_id=message.from_user.id)
        await session.execute(stmt)
        await session.commit()


    await message.answer("Вы успешно вошли!")
    await state.clear()

    kb = [
        [types.KeyboardButton(text="Загрузить файл")],
        [types.KeyboardButton(text="Список файлов")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Напишите вопрос ИИ или настройте файлы для работы.", reply_markup=keyboard)

@router.message(F.text.lower() == "регистрация")
async def registration_start(message: types.Message, state: FSMContext):
    await message.answer("Введите ваш username:")
    await state.set_state(Registration.username)

@router.message(Registration.username)
async def reg_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Введите ваше имя:")
    await state.set_state(Registration.first_name)

@router.message(Registration.first_name)
async def reg_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Введите вашу фамилию:")
    await state.set_state(Registration.last_name)

@router.message(Registration.last_name)
async def reg_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Введите пароль:")
    await state.set_state(Registration.password)

@router.message(Registration.password)
async def reg_password(message: types.Message, state: FSMContext):
    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        new_user = User(
            tg_id=message.from_user.id,
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=hashed_password(message.text)
        )
        session.add(new_user)
        await session.commit()

    await message.answer("Вы успешно зарегистрированы!")
    await state.clear()

    kb = [
            [types.KeyboardButton(text="Загрузить файл")],
            [types.KeyboardButton(text="Список файлов")]
        ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Напишите вопрос ИИ или настройте файлы для работы.", reply_markup=keyboard)


@router.message(F.text.lower() == "загрузить файл")
async def ask_for_file(message: types.Message, state: FSMContext):
    await message.answer("Отправьте документ (PDF, DOCX, TXT).")
    await state.set_state(FileUpload.waiting_for_file)

@router.message(FileUpload.waiting_for_file, F.document)
async def handle_file(message: types.Message, state: FSMContext):
    document = message.document

    file_info = await bot.get_file(document.file_id)
    file_path = file_info.file_path

    file = await bot.download_file(file_path)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.id).where(User.tg_id == message.from_user.id))
        user_id = result.scalar()

    await upload_files(file, user_id, document.file_name)
    await message.answer("Файл загружен успешно!")
    await state.clear()

@router.message(F.text.lower() == "список файлов")
async def delete_tg(message: types.Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User.id).where(User.tg_id == message.from_user.id))
        user_id = result.scalar()

    if os.path.isdir(f"./documents/{user_id}"):
        files = await get_files(user_id) 

        buttons = [
            [InlineKeyboardButton(text=file_name, callback_data=f"file_{file_name}")]
            for file_name in files
        ]
    else:
        buttons = []

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.reply("Выберите файл:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data and c.data.startswith("file_"))
async def process_file_callback(callback_query: CallbackQuery):
    file_name = callback_query.data[len("file_"):]
    await callback_query.answer()  

    async with AsyncSessionLocal() as session:
        stmt = await session.execute(select(User.id).where(User.tg_id == callback_query.from_user.id))
        user_id = stmt.scalar()

        stmt = await session.execute(
            select(File.is_load).where(and_(File.name == file_name, File.user_id == user_id))
        )
        result = stmt.scalar()

    if result == True:
        buttons = [
            [InlineKeyboardButton(text="Удалить файл", callback_data=f"delete_{file_name}")],
            [InlineKeyboardButton(text="Удалить из ИИ", callback_data=f"chunk_delete_{file_name}")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text="Удалить файл", callback_data=f"delete_{file_name}")],
            [InlineKeyboardButton(text="Загрузить в ИИ", callback_data=f"upload_chunk_{file_name}")]
        ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback_query.message.reply(f"Выберете действие с файлом: {file_name}", reply_markup=keyboard)

@router.callback_query(lambda c: c.data and c.data.startswith("delete_"))
async def process_file_callback(callback_query: CallbackQuery):
    file_name = callback_query.data[len("delete_"):]
    await callback_query.answer()  

    async with AsyncSessionLocal() as session:
        stmt = await session.execute(select(User.id).where(User.tg_id == callback_query.from_user.id))
        user_id = stmt.scalar()
    
    result = await delete_files(file_name, user_id)
    await callback_query.message.answer(result)

@router.callback_query(lambda c: c.data and c.data.startswith("upload_chunk_"))
async def process_file_callback(callback_query: CallbackQuery):
    file_name = callback_query.data[len("upload_chunk_"):]
    await callback_query.answer()  

    async with AsyncSessionLocal() as session:
        stmt = await session.execute(select(User.id).where(User.tg_id == callback_query.from_user.id))
        user_id = stmt.scalar()
    
    result = await upload_chunks(file_name, user_id)
    await callback_query.message.answer(result)

@router.callback_query(lambda c: c.data and c.data.startswith("chunk_delete_"))
async def process_file_callback(callback_query: CallbackQuery):
    file_name = callback_query.data[len("chunk_delete_"):]
    await callback_query.answer()  

    async with AsyncSessionLocal() as session:
        stmt = await session.execute(select(User.id).where(User.tg_id == callback_query.from_user.id))
        user_id = stmt.scalar()
    
    result = await delete_chunks(file_name, user_id)
    await callback_query.message.answer(result)

@router.message()
async def handle_message(message: types.Message):
    user_message = message.text

    async with AsyncSessionLocal() as session:
        stmt = await session.execute(select(User.id).where(User.tg_id == message.from_user.id))
        user_id = stmt.scalar()

    results = get_relevant_chunks(user_message, user_id, COLLECTION_NAME)
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