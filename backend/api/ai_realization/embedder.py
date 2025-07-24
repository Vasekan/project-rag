from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

model = SentenceTransformer("intfloat/multilingual-e5-large")
COLLECTION_NAME = "documents"
client = QdrantClient(url="http://localhost:6333")


def get_embedding(text: str):
    return model.encode(text).tolist()


def get_vector_size():
    return model.get_sentence_embedding_dimension()


def search_relevant_chunks(question: str, user_id: str, top_k: int = 3):
    query_vector = get_embedding(question)
    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,

        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(value=user_id)
                )
            ]
        )
    )
    return search_result
