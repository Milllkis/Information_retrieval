from typing import List, Dict, Tuple
from information_retrieval import InformationRetrieval
from app.config import CONFIG
import time
import logging
from crud import read_data

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Инициализация класса поисковика InformationRetrieval
ir = InformationRetrieval(
    csv_file=CONFIG.DATA_PATH,
    tfidf_pkl_file=CONFIG.TFIDF_INDEX_PATH,
    bert_pkl_file=CONFIG.BERT_INDEX_PATH
)

def search(query: str, method: str, limit: int, relevance_score: bool) -> Tuple[List[Dict[str, float]], float]:
    """
    Выполняет поиск по заданному запросу с использованием указанного метода.

    :param query: Запрос для поиска.
    :param method: Метод поиска ('tf-idf' или 'bert').
    :param limit: Максимальное количество результатов для возврата.
    :param relevance_score: Нужно ли возвращать оценку релевантности.
    :return: Список результатов и общее время выполнения поиска.
    """
    start_time = time.time()

    if method == 'tf-idf':
        docs = ir.search_tfidf(query, top_n=limit)
    elif method == 'bert':
        docs = ir.search_bert(query, top_n=limit)
    else:
        raise ValueError(f"Неподдерживаемый метод поиска: {method}")

    results = []
    for doc in docs:
        person_id, category, text, link = doc[0], doc[1], doc[2], doc[3]
        person_data = read_data(person_id)
        if relevance_score:
            score = ir.evaluate_relevance(query, text)
            results.append({
                'doc_id': person_id,
                'category': category,
                'text': text,
                'link': link,
                'cosine_sim': score,
                'person_data': person_data
            })
        else:
            results.append({
                'doc_id': person_id,
                'category': category,
                'text': text,
                'link': link,
                'person_data': person_data
            })

    total_time = time.time() - start_time

    return results, total_time

async def get_available_methods() -> List[str]:
    """
    Возвращает список доступных методов поиска.

    :return: Список доступных методов поиска.
    """
    return ['tf-idf', 'bert']

def get_corpus_info() -> Dict[str, int]:
    """
    Возвращает информацию о корпусе: количество документов и токенов.

    :return: Словарь с информацией о корпусе.
    """
    num_docs = len(ir.df)
    num_tokens_tfidf = ir.df['Processed_TFIDF'].apply(lambda x: len(x.split())).sum()
    num_tokens_bert = ir.df['Processed_BERT'].apply(lambda x: len(x.split())).sum()
    return {
        'num_docs': num_docs,
        'num_tokens_tfidf': num_tokens_tfidf,
        'num_tokens_bert': num_tokens_bert
    }