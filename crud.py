import pymysql
import pandas as pd
import argparse
from typing import List, Dict

# Настройки подключения к базе данных
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mileshka',
    'database': 'biography_db'
}

def create_connection():
    """Создает и возвращает подключение к базе данных MySQL."""
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database']
    )

def insert_data(file_path: str) -> None:
    """Вставляет данные из CSV файла в базу данных.

    Args:
        file_path (str): Путь к CSV файлу.
    """
    df = pd.read_csv(file_path)
    connection = create_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():
        cursor.execute("INSERT IGNORE INTO Person (name) VALUES (%s)", (row['Person'],))
        cursor.execute("SELECT id FROM Person WHERE name = %s", (row['Person'],))
        person_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO Biography (person_id, text, link) VALUES (%s, %s, %s)",
                       (person_id, row['Text'], row['Link']))

        cursor.execute("INSERT INTO Categories (person_id, name) VALUES (%s, %s)",
                       (person_id, row['Category']))

    connection.commit()
    cursor.close()
    connection.close()

def read_data(person_id: int) -> Dict[str, str]:
    """Читает данные о персоне по ID.

    Args:
        person_id (int): ID персоны.

    Returns:
        Dict[str, str]: Словарь с данными о персоне.
    """
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Person WHERE id = %s", (person_id,))
    person = cursor.fetchone()

    if person:
        person_data = {
            'id': person[0],
            'name': person[1],
            'biographies': [],
            'categories': []
        }

        cursor.execute("SELECT * FROM Biography WHERE person_id = %s", (person_id,))
        biographies = cursor.fetchall()
        for bio in biographies:
            person_data['biographies'].append({
                'id': bio[0],
                'text': bio[2],
                'link': bio[3]
            })

        cursor.execute("SELECT * FROM Categories WHERE person_id = %s", (person_id,))
        categories = cursor.fetchall()
        for category in categories:
            person_data['categories'].append({
                'id': category[0],
                'name': category[2]
            })

        cursor.close()
        connection.close()
        return person_data
    else:
        cursor.close()
        connection.close()
        return {}

def update_data(person_id: int, new_name: str, new_bio_text: str, new_link: str, new_category: str) -> None:
    """Обновляет данные персоны и связанные с ней записи.

    Args:
        person_id (int): ID персоны.
        new_name (str): Новое имя персоны.
        new_bio_text (str): Новый текст биографии.
        new_link (str): Новый линк для биографии.
        new_category (str): Новая категория для персоны.
    """
    connection = create_connection()
    cursor = connection.cursor()

    # Обновляем имя в таблице Person
    cursor.execute("UPDATE Person SET name = %s WHERE id = %s", (new_name, person_id))

    # Обновляем биографию
    cursor.execute("UPDATE Biography SET text = %s, link = %s WHERE person_id = %s",
                   (new_bio_text, new_link, person_id))

    # Обновляем категорию
    cursor.execute("UPDATE Categories SET name = %s WHERE person_id = %s",
                   (new_category, person_id))

    connection.commit()
    cursor.close()
    connection.close()

def delete_data(person_id: int) -> None:
    """Удаляет персону и связанные с ней данные по ID.

    Args:
        person_id (int): ID персоны.
    """
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Categories WHERE person_id = %s", (person_id,))
    cursor.execute("DELETE FROM Biography WHERE person_id = %s", (person_id,))
    cursor.execute("DELETE FROM Person WHERE id = %s", (person_id,))

    connection.commit()
    cursor.close()
    connection.close()

def save_query(query_text: str, method: str, query_link: str) -> None:
    """Сохраняет запрос пользователя и метод в таблицу Query."""
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Query (query_text, method, query_link) VALUES (%s, %s, %s)",
                   (query_text, method, query_link))

    connection.commit()
    cursor.close()
    connection.close()

def get_saved_queries() -> List[Dict[str, str]]:
    """Читает все запросы из таблицы Query."""
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Query")
    queries = cursor.fetchall()

    cursor.close()
    connection.close()

    return [{'id': q[0], 'query_text': q[1], 'method': q[2], 'query_link': q[3]} for q in queries]

def main() -> None:
    """Главная функция для обработки аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Insert data into the database.")
    parser.add_argument('--action', type=str, required=True, help='Action to perform: insert, read, update, delete')
    parser.add_argument('--file', type=str, help='CSV file path for insertion')
    parser.add_argument('--id', type=int, help='Person ID for reading/updating/deleting')
    parser.add_argument('--name', type=str, help='New name for updating')
    parser.add_argument('--bio', type=str, help='New biography text for updating')
    parser.add_argument('--link', type=str, help='New biography link for updating')
    parser.add_argument('--category', type=str, help='New category name for updating')

    args = parser.parse_args()

    if args.action == 'insert':
        if args.file:
            insert_data(args.file)
        else:
            print("File path is required for insert action.")

    elif args.action == 'read':
        if args.id is not None:
            person_data = read_data(args.id)
            print(person_data)
        else:
            print("Person ID is required for read action.")

    elif args.action == 'update':
        if args.id is not None and args.name and args.bio and args.link and args.category:
            update_data(args.id, args.name, args.bio, args.link, args.category)
        else:
            print("Person ID, new name, biography text, link and category are required for update action.")

    elif args.action == 'delete':
        if args.id is not None:
            delete_data(args.id)
        else:
            print("Person ID is required for delete action.")

if __name__ == "__main__":
    main()