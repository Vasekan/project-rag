import os

from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse


async def get_files():
    return {"files": os.listdir("./documents")}

async def upload_files(file: UploadFile):
    allowed_extensions = ['.pdf', '.docx', '.txt']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Разрешены только файлы PDF и DOCX.")

    upload_directory = "./documents"
    file_location = f"{upload_directory}/{file.filename}"

    if os.path.exists(file_location):
        raise HTTPException(status_code=400, detail=f"Файл с именем '{file.filename}' уже существует.")
    
    os.makedirs(upload_directory, exist_ok=True)

    with open(file_location, 'wb') as buffer:
        buffer.write(await file.read())

    return {"message": f"{file.filename} сохранено в {file_location}"}

async def delete_files(filename: str):
    filepath = os.path.join("./documents", filename)
    if not os.path.exists(filepath):
        return JSONResponse(status_code=404, content={"error": "Файд не найден"})
    os.remove(filepath)
    return {"filename": filename, "status": "deleted"}