import os
from typing import List, Dict
from backend.api.ai_realization.embedder import get_embedding
from docx import Document as DocxDocument
import pdfplumber

FOLDER_PATH = "documents"
MIN_CHUNK_LENGTH = 500 # Минимальное количество символов в чанке


def chunk_text(text: str) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    combined_chunks = []
    current_chunk = ""
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) < MIN_CHUNK_LENGTH:
            current_chunk = f"{current_chunk}\n\n{paragraph}" if current_chunk else paragraph
        else:
            if current_chunk:
                combined_chunks.append(current_chunk)
            current_chunk = paragraph
    if current_chunk:
        combined_chunks.append(current_chunk)
    return combined_chunks


def parse_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_pdf(path: str) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def parse_docx(path: str) -> str:
    doc = DocxDocument(path)
    return "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])


def load_all_documents(filename: str, user_id: str) -> List[Dict]:
    chunks = []

    if not os.path.exists(FOLDER_PATH):
        return []

    full_path = os.path.join(FOLDER_PATH, f"{user_id}/{filename}")
    if not os.path.isfile(full_path):
        return []

    ext = os.path.splitext(filename)[1].lower()
    try:
        if ext == ".txt":
            text = parse_txt(full_path)
        elif ext == ".pdf":
            text = parse_pdf(full_path)
        elif ext == ".docx":
            text = parse_docx(full_path)
        else:
            return []  # Другой формат, который не поддерживается

        for chunk in chunk_text(text):
            chunks.append({
                "text": chunk,
                "embedding": get_embedding(chunk),
                "doc_name": filename,
                "user_id": str(user_id)
            })

    except Exception as e:
        print(f"Ошибка при обработке {filename}: {e}")

    return chunks
