from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import router as api_router
from app.services import search
from crud import save_query, get_saved_queries
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Создание экземпляра FastAPI
app = FastAPI()

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def read_index(request: Request):
    """
    Обработчик для главной страницы.

    Args:
        request (Request): Объект запроса.

    Returns:
        TemplateResponse: Ответ с шаблоном главной страницы.
    """
    return templates.TemplateResponse("main_page.html", {"request": request})

@app.get("/search")
async def search_page(request: Request):
    """
    Обработчик для страницы поиска.

    Args:
        request (Request): Объект запроса.

    Returns:
        TemplateResponse: Ответ с шаблоном страницы поиска.
    """
    saved_queries = get_saved_queries()
    seen_queries = set()
    unique_queries = []

    for query in saved_queries:
        query_link = query['query_link']
        if query_link not in seen_queries:
            seen_queries.add(query_link)
            unique_queries.append(query)

    return templates.TemplateResponse("search_page.html", {"request": request, "saved_queries": unique_queries})

@app.get("/results")
async def results_page(request: Request, query: str, method: str, limit: int, relevance_score: bool):
    """
    Обработчик для страницы результатов поиска.

    Args:
        request (Request): Объект запроса.
        query (str): Поисковый запрос.
        method (str): Метод поиска.
        limit (int): Лимит результатов.
        relevance_score (bool): Оценка релевантности.

    Returns:
        TemplateResponse: Ответ с шаблоном страницы результатов поиска.
    """
    # Логика обработки запроса и получения данных
    results, total_time = search(query, method, limit, relevance_score)

    # Сохранение запроса и метода в базу данных
    query_link = f"/results?query={query}&method={method}&limit={limit}&relevance_score={relevance_score}"
    save_query(query, method, query_link)

    # Передаем результаты и время в шаблон
    return templates.TemplateResponse("result_page.html", {
        "request": request,
        "query": query,
        "results": results,
        "time": round(total_time, 2)
    })

# Включение маршрутов API
app.include_router(api_router, prefix="/api")