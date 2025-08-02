# backend/api/ai_realization/task_assist.py

# from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from qdrant_client import QdrantClient

# Настройки

URL="http://qdrant:6333"
OLLAMA_MODEL = "qwen2.5:32b-instruct-q3_K_S"
OLLAMA_BASE_URL = "http://176.57.78.197:11434"

# Инициализация
qdrant_client = QdrantClient(url=URL)

# Модель Ollama
ollama_llm = OllamaLLM(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL
)


# RAG
def truncate_context(context: str, max_length: int = 8000) -> str:
    """Обрезка контекста по лимитам"""
    return context[:max_length]


def get_relevant_chunks(question: str, user_id: str, collection_name: str = "documents", top_k: int = 3):
    """Поиск релевантных чанков (qdrant.query_points)"""
    from backend.api.ai_realization.embedder import get_embedding
    from backend.api.ai_realization.qdrant_manager import client as qdrant_client
    from qdrant_client.http.models import Filter, FieldCondition, MatchValue

    query_vector = get_embedding(question)
    search_result = qdrant_client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        with_payload=True,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=str(user_id))
                )
            ]
        )
    )
    return search_result.points


def generate_answer_from_context(question: str, relevant_chunks):
    if not relevant_chunks:
        return "Я не знаю."
    context_text = "\n\n".join([chunk.payload.get("text", "") for chunk in relevant_chunks])
    context_text = truncate_context(context_text)
    prompt = (
        f"Система: Ты — ИИ-ассистент, который обязан отвечать только на основе предоставленного контекста. "
        f"Если в контексте нет информации — отвечай 'Я не знаю.'\n\n"
        f"Контекст:\n{context_text}\n\n"
        f"На основе КОНТЕКСТА, кратко и точно ответь на следующий вопрос:\n"
        f"Вопрос: {question}\n"
        f"Ответ:"
    )

    try:
        response = ollama_llm.invoke(prompt)
        return response.strip()
    except Exception as e:
        return f"Ошибка при обращении к модели: {e}"