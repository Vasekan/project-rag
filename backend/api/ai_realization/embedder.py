from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

model = SentenceTransformer("intfloat/multilingual-e5-large")
COLLECTION_NAME = "documents"
client = QdrantClient(host="qdrant", port=6333)


def get_embedding(text: str):
    return model.encode(text).tolist()


def get_vector_size():
    return model.get_sentence_embedding_dimension()


def search_relevant_chunks(question: str, top_k: int = 3):
    query_vector = get_embedding(question)
    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True
    )
    return search_result
