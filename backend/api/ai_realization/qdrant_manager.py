from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue, PointIdsList)
import uuid

COLLECTION_NAME = "documents"

client = QdrantClient(host="qdrant", port=6333)


# client = QdrantClient(url="http://localhost:6333")


def init_collection(vector_size: int):
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )


def upload_documents(chunks: list[dict], vector_size: int, user_id: str):
    init_collection(vector_size)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=chunk["embedding"],
            payload={
                "text": chunk["text"],
                "doc_name": chunk["doc_name"],
                "user_id": user_id
            }
        )
        for chunk in chunks
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return f"Загружено {len(points)} чанков в коллекцию '{COLLECTION_NAME}' пользователя '{user_id}'."


# Проверка, загружен ли такой документ
def is_document_loaded(doc_name: str, user_id: str) -> bool:
    from qdrant_client.http.models import Filter, FieldCondition, MatchValue

    hits = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(key="doc_name", match=MatchValue(value=doc_name)),
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            ]
        ),
        limit=1,
        with_payload=False
    )

    return len(hits[0]) > 0


def delete_by_doc_name(doc_name: str, user_id: str):
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(key="doc_name", match=MatchValue(value=doc_name)),
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            ]
        )
    )
    return f"Документ '{doc_name}' удалён из коллекции пользователя '{user_id}'."


def delete_by_id(doc_id: str):
    # Пытаемся получить точку по ID
    try:
        result = client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[doc_id]
        )
        if not result:
            print(f"Точка с ID '{doc_id}' не найдена.")
            return
    except Exception as e:
        print(f"Ошибка при попытке найти точку: {e}")
        return

    # Если точка найдена, удаляем её
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=PointIdsList(points=[doc_id])
    )
    return f"Точка с ID '{doc_id}' удалена из коллекции."


def list_documents(user_id: str, limit: int = 5):
    hits = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            ]
        ),
        limit=limit,
        with_payload=True,
        with_vectors=False
    )

    if not hits[0]:
        return "Пусто"

    output = []
    for point in hits[0]:
        output.append(f"ID: {point.id}")
        output.append(f"Имя документа: {point.payload.get('doc_name')}")
        output.append(f"Текст чанка: {point.payload.get('text')}")
        output.append("-" * 100)

    return "\n".join(output)
