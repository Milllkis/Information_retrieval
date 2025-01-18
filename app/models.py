from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

class SearchMethod(str, Enum):
    """Перечисление методов поиска.

    Атрибуты:
        tfidf (str): Метод поиска на основе TF-IDF.
        bert (str): Метод поиска на основе BERT.
    """
    tfidf = 'tf-idf'
    bert = 'bert'

class SearchResult(BaseModel):
    """Модель для представления результата поиска.

    Атрибуты:
        document_id (int): Уникальный идентификатор документа.
        category (str): Категория документа.
        text (str): Текст документа, найденного в результате поиска.
        link (str): Ссылка на документ.
        score (Optional[float]): Оценка релевантности результата. Может быть None, если не указана.
        person_data (Dict[str, str]): Данные о персоне.
    """
    document_id: int
    category: str
    text: str
    link: str
    score: Optional[float] = None
    person_data: Dict[str, str]

class SearchRequest(BaseModel):
    """Модель запроса на поиск.

    Атрибуты:
        query (str): Запрос пользователя для выполнения поиска.
        method (SearchMethod): Метод поиска, выбранный пользователем из доступных методов.
        limit (int): Максимальное количество результатов, которые нужно вернуть. По умолчанию 5.
        relevance_score (bool): Оценка релевантности. По умолчанию False.
    """
    query: str
    method: SearchMethod
    limit: int = 5
    relevance_score: bool = False

class SearchResponse(BaseModel):
    """Модель ответа на запрос поиска.

    Атрибуты:
        results (List[SearchResult]): Список результатов поиска.
        time_taken (Optional[float]): Время, затраченное на выполнение поиска, может быть None, если не указано.
    """
    results: List[SearchResult]
    total_time: Optional[float] = None

class CorpusInfo(BaseModel):
    """Модель информации о корпусе документов.

    Атрибуты:
        num_documents (int): Общее количество документов в корпусе.
        corpus_name (str): Название корпуса документов.
    """
    num_docs: int
    num_tokens_tfidf: int
    num_tokens_bert: int

class AvailableMethodsResponse(BaseModel):
    """Модель ответа с доступными методами поиска.

    Атрибуты:
        methods (List[SearchMethod]): Список доступных методов поиска.
    """
    methods: List[SearchMethod]