import pymysql
from typing import List, Tuple

# Настройки подключения к базе данных
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'biography_db'
}

def create_connection():
    """Создает и возвращает соединение с базой данных."""
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database']
    )

def fetch_all_people(connection) -> List[Tuple]:
    """Получает всех людей из базы данных (максимум 5)."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Person LIMIT 5")
        return cursor.fetchall()

def fetch_biography_by_name(connection, name: str) -> List[Tuple]:
    """Находит биографию по имени человека."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Biography.text FROM Biography
            JOIN Person ON Biography.person_id = Person.id
            WHERE Person.name = %s
        """, (name,))
        return cursor.fetchall()

def fetch_category_for_person(connection, person_id: int) -> List[Tuple]:
    """Получает категорию для определенного человека (если есть)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Categories.name FROM Categories
            WHERE person_id = %s
            ORDER BY id LIMIT 1
        """, (person_id,))
        return cursor.fetchall()

def count_biographies_per_person(connection) -> List[Tuple]:
    """Подсчитывает количество биографий для каждого человека (максимум 5)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Person.name, COUNT(Biography.id) AS biography_count
            FROM Person
            LEFT JOIN Biography ON Person.id = Biography.person_id
            GROUP BY Person.id
            LIMIT 5
        """)
        return cursor.fetchall()

def count_words_in_biographies(connection) -> int:
    """Подсчитывает общее количество слов в биографиях."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT SUM(LENGTH(text) - LENGTH(REPLACE(text, ' ', '')) + 1) AS word_count
            FROM Biography
        """)
        row = cursor.fetchone()
        return row[0] if row else 0

def count_categories_per_person(connection) -> List[Tuple]:
    """Получает людей и их количество категорий, отсортированных по количеству категорий (максимум 5)."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Person.name, COUNT(Categories.id) AS category_count
            FROM Person
            LEFT JOIN Categories ON Person.id = Categories.person_id
            GROUP BY Person.id
            ORDER BY category_count DESC
            LIMIT 5
        """)
        return cursor.fetchall()

def main() -> None:
    """Основная функция для выполнения запросов и вывода результатов."""
    connection = create_connection()

    print("=== Запросы к базе данных ===\n")

    # Блок простых запросов
    print("----- Простые запросы -----")

    people = fetch_all_people(connection)
    print("\n1. Получить всех людей (максимум 5):")
    print(people)

    name_to_search = 'Xzibit'  # Замените на нужное имя
    biography = fetch_biography_by_name(connection, name_to_search)
    print(f"\n2. Найти биографию по имени человека '{name_to_search}':")
    print(biography[0][0])

    person_id_to_search = 1  # Замените на нужный ID
    first_category = fetch_category_for_person(connection, person_id_to_search)
    print(f"\n3. Получить категорию для человека с ID {person_id_to_search}:")
    print(first_category[0][0])

    # Блок сложных запросов
    print("\n----- Сложные запросы -----")

    biography_counts = count_biographies_per_person(connection)
    print("\n1. Подсчет количества биографий для каждого человека (максимум 5):")
    print(biography_counts)

    total_word_count = count_words_in_biographies(connection)
    print("\n2. Общее количество слов в биографиях:")
    print(total_word_count)

    category_counts = count_categories_per_person(connection)
    print("\n3. Люди и количество категорий, отсортированные по количеству категорий (максимум 5):")
    print(category_counts)

    connection.close()

if __name__ == "__main__":
    main()