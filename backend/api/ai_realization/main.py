from backend.api.ai_realization.document_loader import load_txt_documents
from backend.api.ai_realization.embedder import get_vector_size
from backend.api.ai_realization.qdrant_manager import upload_documents, delete_by_doc_name, delete_by_id, \
    list_documents, is_document_loaded
from backend.api.ai_realization.task_assist import get_relevant_chunks, generate_answer_from_context
import os

FOLDER_PATH = "documents"  # Папка с .txt файлами
COLLECTION_NAME = "documents"


def show_menu():
    print(
        f"\nВыберите действие:\n "
        f"1. Загрузить документы в базу\n"
        f"2. Удалить документ по имени файла\n"
        f"3. Удалить вектор по ID\n"
        f"4. Посмотреть загруженные документы\n"
        f"5. Задать вопрос\n"
        f"6. Проверить, загружен ли документ с именем 'Имя'\n"
        f"0. Выход"
    )


def main():
    while True:
        show_menu()
        print("-" * 100)
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            if not os.path.exists(FOLDER_PATH):
                print(f"Папка '{FOLDER_PATH}' не найдена. Создайте её и положите .txt файлы.")
                continue

            chunks = load_txt_documents(FOLDER_PATH)
            if not chunks:
                print("Нет подходящих .txt файлов для загрузки.")
                continue

            vector_size = get_vector_size()
            upload_documents(chunks, vector_size)

        elif choice == "2":
            name = input("Введите имя файла (например, example.txt): ").strip()
            delete_by_doc_name(name)

        elif choice == "3":
            doc_id = input("Введите ID вектора для удаления: ").strip()
            delete_by_id(doc_id)

        elif choice == "4":
            list_documents()

        elif choice == "5":
            query = input("Введите ваш вопрос: ").strip()
            results = get_relevant_chunks(query, COLLECTION_NAME)
            if not results:
                print("Ничего не найдено.")
            else:
                print("+" * 100)
                for result in results:
                    print(f"Релевантность: {result.score:.3f}")
                    print(f"Документ: {result.payload.get('doc_name')}")
                    print(f"Текст чанка: {result.payload.get('text')[:100]}...")
                    print("+" * 100)

                answer = generate_answer_from_context(query, results)
                print(f"\nОтвет ассистента:\n{answer}\n")

        elif choice == '6':
            if is_document_loaded(input('Введите название документа "filename.txt:\n')):
                print("Файл/чанки из файла загружены")
            else:
                print("Такого нет!")

        elif choice == "0":
            print("Выход.")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
