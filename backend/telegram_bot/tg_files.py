import os

from sqlalchemy import select, and_, delete, update

from backend.db import AsyncSessionLocal
from backend.api.models.files import File
from backend.api.ai_realization.qdrant_manager import delete_by_doc_name
from backend.api.ai_realization.embedder import get_vector_size
from backend.api.ai_realization.qdrant_manager import upload_documents
from backend.api.ai_realization.document_loader import load_all_documents

async def get_files(user_id):
    return os.listdir(f"./documents/{user_id}")

async def upload_files(file, user_id, filename):
    import os

    allowed_extensions = ['.pdf', '.docx', '.txt']
    file_extension = os.path.splitext(filename)[1].lower()

    if file_extension not in allowed_extensions:
        return "Разрешены только файлы PDF, DOCX и TXT."

    upload_directory = f"./documents/{user_id}"
    file_location = f"{upload_directory}/{filename}"

    if os.path.exists(file_location):
        return f"Файл с именем '{filename}' уже существует."

    os.makedirs(upload_directory, exist_ok=True)

    if hasattr(file, 'read'):
        content = file.read()
    else:
        content = file 

    with open(file_location, 'wb') as buffer:
        buffer.write(content)

    async with AsyncSessionLocal() as session:
        file_model = File(name=filename, user_id=user_id)
        session.add(file_model)
        await session.commit()
        await session.refresh(file_model)

    return {"message": f"{filename} сохранено в {file_location}"}


async def delete_files(filename, user_id):
    filepath = os.path.join(f"./documents/{user_id}", filename)
    if not os.path.exists(filepath):
        return "Файл не найден"
    os.remove(filepath)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(File.is_load).where(and_(File.name == filename, File.user_id == user_id))
        )
        if result == True:
            delete_by_doc_name(filename, user_id=user_id)

        stmt = delete(File).where(and_(File.name == filename, File.user_id == user_id))
        await session.execute(stmt)
        await session.commit()
    return "Файл успешно удалён"

async def upload_chunks(filename, user_id):
    async with AsyncSessionLocal() as session:
        stmt = update(File).where(File.name == filename).values(is_load=True)
        await session.execute(stmt)
        await session.commit()

    chunks = load_all_documents(filename=filename, user_id=user_id)
    vector_size = get_vector_size()
    return upload_documents(chunks, vector_size, user_id)

async def delete_chunks(filename, user_id):
    delete_by_doc_name(filename, user_id=user_id)

    async with AsyncSessionLocal() as session:
        stmt = update(File).where(File.name == filename).values(is_load=False)
        await session.execute(stmt)
        await session.commit()
    return "Файл успешно удалён из ИИ"