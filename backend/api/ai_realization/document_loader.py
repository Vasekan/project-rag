import os
from backend.api.ai_realization.embedder import get_embedding


FOLDER_PATH = "documents"  
MIN_CHUNK_LENGTH = 500  # минимальное количество символов для чанка


def load_txt_documents(filename: str):
    chunks = []
    full_path = os.path.join(FOLDER_PATH, filename)
    with open(full_path, "r", encoding="utf-8") as f:
        text = f.read()
        # Разбиваем текст на абзацы
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        # Объединяем до достижения мин длины
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

        for chunk in combined_chunks:
            chunks.append({
                "text": chunk,
                "embedding": get_embedding(chunk),
                "doc_name": filename
            })
    return chunks
