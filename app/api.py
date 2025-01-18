import logging
from fastapi import APIRouter, HTTPException
from app.models import SearchRequest, SearchResponse, AvailableMethodsResponse, CorpusInfo
from app.services import (
    search as perform_search,
    get_available_methods as fetch_available_methods,
    get_corpus_info as fetch_corpus_info,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
def read_root() -> dict:
    """
    Корневой эндпоинт, возвращающий приветственное сообщение.

    Returns:
        dict: Приветственное сообщение.
    """
    return {"message": "Добро пожаловать в поисковую систему!"}


@router.get("/methods", response_model=AvailableMethodsResponse)
async def get_available_methods() -> AvailableMethodsResponse:
    """
    Эндпоинт для получения доступных методов поиска.

    Returns:
        AvailableMethodsResponse: Список доступных методов поиска.
    """
    methods = await fetch_available_methods()
    return AvailableMethodsResponse(methods=methods)


@router.get("/corpus", response_model=CorpusInfo)
async def get_corpus_info() -> CorpusInfo:
    """
    Эндпоинт для получения информации о корпусе.

    Returns:
        CorpusInfo: Информация о корпусе.
    """
    corpus_info = fetch_corpus_info()
    return corpus_info


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    """
    Эндпоинт для выполнения поиска по запросу с возможностью оценки релевантности.

    Args:
        request (SearchRequest): Запрос на поиск.

    Returns:
        SearchResponse: Результаты поиска и время выполнения.
    
    Raises:
        HTTPException: Ошибка при выполнении поиска.
    """
    try:
        # Выполняем поиск с учетом оценки релевантности
        results, total_time = await perform_search(
            query=request.query,
            method=request.method,
            limit=request.limit,
            relevance_score=request.relevance_score,
        )
        return SearchResponse(results=results, total_time=total_time)
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))