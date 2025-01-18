import click
import sys
import time
from information_retrieval import InformationRetrieval

# Создаем объект класса поисковика
ir = InformationRetrieval('new_biographies.csv', 'indexes/tfidf_index.pkl', 'indexes/bert_index.pkl')

@click.group()
def cli():
    """Командная строка для работы с системой поиска информации."""
    pass

@click.command()
def welcome():
    """Информация о том, как использовать CLI."""
    click.echo("Добро пожаловать в систему поиска!")
    click.echo("Индексация данных будет автоматически загружена из сохраненных файлов при запуске.")
    click.echo("Для поиска используйте команду:")
    click.echo("python cli.py search <ваш запрос> --index <tf-idf|bert>.")

@click.command()
@click.argument('query', type=str)
@click.option('--index', type=click.Choice(['tf-idf', 'bert'], case_sensitive=False), required=True,
              help="Выберите индекс: 'tf-idf' или 'bert'.")
def search(query: str, index: str):
    """
    Поиск по запросу с использованием указанного индекса.

    :param query: Запрос для поиска.
    :param index: Тип индекса ('tf-idf' или 'bert').
    """
    click.echo(f"Выполняется поиск по запросу: '{query}' с использованием индекса '{index}'...")

    start_time = time.time()  # Запоминаем время начала поиска

    # Выполняем поиск
    if index == 'tf-idf':
        results = ir.search_tfidf(query, top_n=2)
        method_name = "TF-IDF"
    else:
        results = ir.search_bert(query, top_n=2)
        method_name = "BERT"

    elapsed_time = time.time() - start_time  # Время выполнения поиска

    if results:
        click.echo(f"Результаты поиска ({method_name}):")
        for idx, result in enumerate(results):
            click.echo(f"\n--- Результат {idx + 1} ---\nID: {result[0]}\nCategory: {result[1]}\nText: {result[2]}\nLink: {result[3]}")
            # Здесь добавлен код для получения и отображения оценки релевантности
            relevance_score = ir.evaluate_relevance(query, result[2])
            click.echo(f"Оценка релевантности: {relevance_score:.4f}")
    else:
        click.echo("По вашему запросу ничего не найдено.")

    click.echo(f"\nВремя выполнения поиска: {elapsed_time:.2f} секунд.")

# Добавляем команды в главный интерфейс
cli.add_command(welcome)
cli.add_command(search)

if __name__ == '__main__':
    # Если скрипт запущен без параметров, вызываем команду welcome по умолчанию.
    if len(sys.argv) == 1:
        welcome()
    else:
        cli()