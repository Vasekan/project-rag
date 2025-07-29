import os

from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import delete, select, update, and_

from backend.db import get_session
from backend.api.models.files import File
from backend.api.ai_realization.qdrant_manager import delete_by_doc_name
from backend.api.ai_realization.document_loader import load_all_documents
from backend.api.ai_realization.embedder import get_vector_size
from backend.api.ai_realization.qdrant_manager import upload_documents


# async def get_files():
#     files = os.listdir("./documents")
#     status = [] 
#     for file in files:
#         status.append(select(File.is_load).where(File.name == file))
#     return {"files": os.listdir("./documents"), "status": status}

async def get_files(current_user, session):
    files = os.listdir(f"./documents/{current_user.id}")
    status = []

    for file in files:
        result = await session.execute(
            select(File.is_load).where(and_(File.name == file, File.user_id == current_user.id))
        )
        is_loaded = result.scalar_one_or_none()
        status.append({"file": file, "is_load": is_loaded})

    return {"files": status}

async def upload_files(file: UploadFile, current_user, session):
    allowed_extensions = ['.pdf', '.docx', '.txt']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Разрешены только файлы PDF и DOCX.")

    upload_directory = f"./documents/{current_user.id}"
    file_location = f"{upload_directory}/{file.filename}"

    if os.path.exists(file_location):
        raise HTTPException(status_code=400, detail=f"Файл с именем '{file.filename}' уже существует.")
    
    if not os.path.exists(file_location):
        os.makedirs(upload_directory, exist_ok=True)

    with open(file_location, 'wb') as buffer:
        buffer.write(await file.read())
    
    file_model = File(name=file.filename, user_id=current_user.id)
    session.add(file_model)
    await session.commit()
    await session.refresh(file_model)

    return {"message": f"{file.filename} сохранено в {file_location}"}

async def upload_chunks(filename, current_user, session):
    stmt = update(File).where(File.name == filename).values(is_load=True)
    await session.execute(stmt)
    await session.commit()

    chunks = load_all_documents(filename=filename, user_id=current_user.id)
    vector_size = get_vector_size()
    return upload_documents(chunks, vector_size, current_user.id)

async def delete_files(filename: str, current_user, session):
    filepath = os.path.join(f"./documents/{current_user.id}", filename)
    if not os.path.exists(filepath):
        return JSONResponse(status_code=404, content={"error": "Файл не найден"})
    os.remove(filepath)

    result = await session.execute(
        select(File.is_load).where(and_(File.name == filename, File.user_id == current_user.id))
    )
    if result == True:
        delete_by_doc_name(filename, user_id=current_user.id)

    stmt = delete(File).where(and_(File.name == filename, File.user_id == current_user.id))
    await session.execute(stmt)
    await session.commit()
    return {"filename": filename, "status": "deleted"}

async def delete_chunks(filename, current_user, session):
    delete_by_doc_name(filename, user_id=current_user.id)

    stmt = update(File).where(File.name == filename).values(is_load=False)
    await session.execute(stmt)
    await session.commit()
    return {"filename": filename, "status": "deleted from ai"}