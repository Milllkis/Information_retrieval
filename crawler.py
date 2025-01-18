import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Tuple, Dict
from tqdm import tqdm


class BiographiesCrawler:
    def __init__(self) -> None:
        """Инициализация краулера для биографий."""
        self.session = requests.Session()
        self.ua = UserAgent()
        self.categories_links: List[str] = []
        self.category_people: Dict[str, List[Tuple[str, str]]] = {}

    def fetch_categories(self, url: str) -> None:
        """Парсит страничку с категориями и сохраняет ссылки на категории.

        Args:
            url (str): URL страницы с категориями.
        """
        req = self.session.get(url, headers={'User-Agent': self.ua.random})
        page = req.text
        soup = BeautifulSoup(page, 'html.parser')

        links = soup.select('.item__body a')
        self.categories_links = ['https://obrazovaka.ru' + str(link['href']) for link in links]

    def get_every_person(self, url: str) -> List[Tuple[str, str]]:
        """Извлекает имена и ссылки на биографии из указанной категории.

        Args:
            url (str): URL категории.

        Returns:
            List[Tuple[str, str]]: Список кортежей с именами и ссылками на биографии.
        """
        req = self.session.get(url, headers={'User-Agent': self.ua.random})
        page = req.text
        soup = BeautifulSoup(page, 'html.parser')

        biographies = soup.select('.biographis__item')
        list_of_people: List[Tuple[str, str]] = []

        for bio in biographies:
            name = bio.select_one('.item__name').text
            link = bio.select_one('.item__name')['href']
            list_of_people.append((name, link))

        return list_of_people

    def crawl_categories(self) -> None:
        """Обходит все категории и собирает информацию о людях."""
        for link in self.categories_links:
            category = link.split('/')[4]
            result = self.get_every_person(link)

            if category not in self.category_people:
                self.category_people[category] = []

            self.category_people[category].extend(result)

    def get_person_text(self, url: str) -> str:
        """Извлекает текст биографии из страницы.

        Args:
            url (str): URL страницы с биографией.

        Returns:
            str: Текст биографии или сообщение об ошибке.
        """
        req = self.session.get(url, headers={'User-Agent': self.ua.random})
        page = req.text
        soup = BeautifulSoup(page, 'html.parser')

        # Находим div с id 'summury_text'
        summary_div = soup.find("div", id='summury_text')

        if summary_div:
            # Сначала собираем текст из summury_div
            summary_text = summary_div.get_text(strip=True)

            # Получаем следующий элемент после summury_div
            next_element = summary_div.find_next_sibling()

            paragraphs: List[str] = []

            # Ищем все <p> теги после найденного элемента
            while next_element:
                if next_element.name == 'p':
                    paragraphs.append(next_element.get_text(strip=True))
                # Если встречаем h4 с текстом "Оценка по биографии", прерываем цикл
                elif next_element.name == 'h4' and next_element.get_text(strip=True) == "Оценка по биографии":
                    break

                # Переходим к следующему элементу
                next_element = next_element.find_next_sibling()

            # Объединяем текст из summary и найденные параграфы
            return summary_text + " " + " ".join(paragraphs).strip()
        else:
            return "Элемент с id 'summury_text' не найден."

    def scrape(self, categories_url: str) -> pd.DataFrame:
        """Основной метод для запуска краулера и сбора данных в DataFrame.

        Args:
            categories_url (str): URL страницы с категориями.

        Returns:
            pd.DataFrame: DataFrame с информацией о людях и их биографиях.
        """
        self.fetch_categories(categories_url)
        self.crawl_categories()

        df = pd.DataFrame(columns=['Person', 'Category', 'Text', 'Link'])
        person_id: int = 0

        # Используем tqdm для отслеживания прогресса при обходе людей
        total_people = sum(len(people) for people in self.category_people.values())

        for category, people in tqdm(self.category_people.items(), desc="Сбор данных", total=len(self.category_people)):
            for person, link in people:
                biography = self.get_person_text(link)
                df.loc[person_id] = [person, category, biography, link]
                person_id += 1

        return df


crawler = BiographiesCrawler()
categories_url = 'https://obrazovaka.ru/biografii'
df = crawler.scrape(categories_url)

df = df[df['Text'] != "Элемент с id 'summury_text' не найден."]
df = df.drop_duplicates()
df = df[df['Category'].isin(['iskusstvo', 'obshhestvo-kultura-obrazovanie'])]

df.to_csv('biographies.csv')