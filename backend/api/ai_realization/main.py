from backend.api.ai_realization.document_loader import load_txt_documents
from backend.api.ai_realization.embedder import get_vector_size
from backend.api.ai_realization.qdrant_manager import upload_documents, delete_by_doc_name, delete_by_id, \
    list_documents, is_document_loaded
from backend.api.ai_realization.task_assist import get_relevant_chunks, generate_answer_from_context
import os

FOLDER_PATH = "documents"  # Папка с .txt файлами
COLLECTION_NAME = "documents"


def show_menu():
    return (
        f"\nВыберите действие:\n "
        f"1. Загрузить документы в базу\n"
        f"2. Удалить документ по имени файла (Пример: 2 example.txt)\n"
        f"3. Удалить вектор по ID (Пример: 3 123456)\n"
        f"4. Посмотреть загруженные документы\n"
        f"5. Задать вопрос (Пример: 5 Как дела?)\n"
        f"6. Проверить, загружен ли документ с именем 'Имя' (Пример: 6 example.txt)"
    )


def main(user_message: str):
    choice = user_message[:1]
    argument = user_message[1:].strip()

    if choice == "1":
        if not os.path.exists(FOLDER_PATH):
            return f"Папка '{FOLDER_PATH}' не найдена. Создайте её и положите .txt файлы."

        chunks = load_txt_documents(FOLDER_PATH)
        if not chunks:
            return "Нет подходящих .txt файлов для загрузки."

        vector_size = get_vector_size()
        return upload_documents(chunks, vector_size)

    elif choice == "2":
        if not argument:
            return "Пожалуйста, укажите имя файла. Пример: 2 example.txt"
        return delete_by_doc_name(argument.strip())

    elif choice == "3":
        if not argument:
            return "Пожалуйста, укажите ID. Пример: 3 123456"
        return delete_by_id(argument.strip())
    
    elif choice == "4":
        return list_documents()
 
    elif choice == "5":
        results = get_relevant_chunks(argument.split(), COLLECTION_NAME)
        if not results:
            return "Ничего не найдено."
        output = ["+" * 100]
        for result in results:
            output.append(f"Релевантность: {result.score:.3f}")
            output.append(f"Документ: {result.payload.get('doc_name')}")
            output.append(f"Текст чанка: {result.payload.get('text')[:100]}...") 
            output.append("+" * 100)

        answer = generate_answer_from_context(argument.split(), results)
        return "\n".join(output + [f"\nОтвет ассистента:\n{answer}"])

    elif choice == '6':
        if is_document_loaded(argument.strip()):
            return "Файл/чанки из файла загружены"
        else:
            return "Неверный выбор. Попробуйте снова."

    else:
        return show_menu()