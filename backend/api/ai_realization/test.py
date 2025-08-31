# для тестирования RAG-системы
# tests/test_ragas.py
import os
import asyncio
from datasets import Dataset, load_dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
    answer_correctness
)
from backend.api.ai_realization.task_assist import get_relevant_chunks, generate_answer_from_context, truncate_context
from backend.api.schemas.chat import ChatBaseSchema
from backend.api.ai_realization.main import main # RAG


current_user = 'user'

async def test_rag_system(chat: ChatBaseSchema):
    # Тестовый датасет. Берем 50 вопросов-ответов
    squad = load_dataset("squad", "plain_text")
    test_data = squad["train"].select(range(50))
    

    if not results:
        return {"message": "Ничего не найдено."}
    output = ["+" * 100]
    for result in results:
        output.append(f"Релевантность: {result.score:.3f}")
        output.append(f"Документ: {result.payload.get('doc_name')}")
        output.append(f"Текст чанка: {result.payload.get('text')[:100]}...") 
        output.append("+" * 100)

    
    # Получаем ответы от системы
    answers = []
    contexts = []
    
    for question in test_data["question"]:
        results = get_relevant_chunks(question, current_user.id, test_data)
        answers.append(generate_answer_from_context(question, results))
        context_text = "\n\n".join([chunk.payload.get("text", "") for chunk in results])
        contexts.append(truncate_context(context_text))
    
    # Создаем датасет для Ragas
    dataset = Dataset.from_dict({
        "question": test_data["question"],
        "answer": answers,
        "contexts": contexts,
        "ground_truth": test_data["answers"]
    })
    
    # Вычисляем метрики
    metrics = [
        answer_relevancy,
        faithfulness,
        context_recall,
        context_precision,
        answer_correctness
    ]
    
    result = evaluate(dataset, metrics=metrics)
    
    print("RAGAS Evaluation Results:")
    print(result)
    
    # Проверяем, что метрики выше threshold
    assert result['answer_relevancy'] > 0.7
    assert result['faithfulness'] > 0.8
    assert result['answer_correctness'] > 0.6
    
    return result

if __name__ == "__main__":
    asyncio.run(test_rag_system())