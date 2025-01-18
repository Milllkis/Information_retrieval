import pymysql

# Настройки подключения к базе данных
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mileshka',
    'database': 'biography_db'
}

def create_database() -> None:
    """Создает базу данных biography_db, если она не существует."""
    connection = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = connection.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS biography_db")
    cursor.close()
    connection.close()

def setup_tables() -> None:
    """Создает необходимые таблицы в базе данных biography_db."""
    connection = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database']
    )
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Person (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Biography (
        id INT AUTO_INCREMENT PRIMARY KEY,
        person_id INT,
        text TEXT,
        link VARCHAR(255),
        FOREIGN KEY (person_id) REFERENCES Person(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Query (
        id INT AUTO_INCREMENT PRIMARY KEY,
        query_text VARCHAR(255),
        method VARCHAR(50),
        query_link VARCHAR(255)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        person_id INT,
        name VARCHAR(255) NOT NULL,
        FOREIGN KEY (person_id) REFERENCES Person(id)
    )
    """)

    connection.commit()
    cursor.close()
    connection.close()

def setup_database() -> None:
    """Создает базу данных и таблицы, необходимые для работы приложения."""
    create_database()
    setup_tables()

if __name__ == "__main__":
    setup_database()