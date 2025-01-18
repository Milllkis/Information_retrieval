import os
import pandas as pd
import pymorphy2
import re
import string
import pickle
import joblib
import numpy as np
from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel
from nltk.corpus import stopwords
import torch
from tqdm import tqdm

class InformationRetrieval:
    """
    Класс для извлечения информации с использованием моделей TF-IDF и BERT.

    Основные функции:
    - Предобработка текста
    - Индексация текстов с помощью TF-IDF и BERT
    - Поиск по индексам с использованием TF-IDF и BERT
    """

    def __init__(self, csv_file: str, tfidf_pkl_file: Optional[str] = None, bert_pkl_file: Optional[str] = None, processed_data_file: Optional[str] = 'processed_data.pkl') -> None:
        """
        Инициализация класса.

        :param csv_file: Путь к файлу CSV с колонкой 'Text', содержащей тексты для анализа.
        :param tfidf_pkl_file: Путь к файлу PKL с моделью TF-IDF.
        :param bert_pkl_file: Путь к файлу PKL с эмбеддингами BERT.
        :param processed_data_file: Путь к файлу PKL с предобработанными данными.
        """
        self.df = pd.read_csv(csv_file)
        if 'id' not in self.df.columns:
            self.df['id'] = range(1, len(self.df) + 1)
        self.morph = pymorphy2.MorphAnalyzer()
        self.stop_words = set(stopwords.words('russian'))
        self.tfidf_vectorizer = TfidfVectorizer(preprocessor=self.preprocess_text_tf_idf)
        self.tfidf_matrix = None
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.bert_embeddings = None

        # Проверка наличия файла с предобработанными данными
        if os.path.exists(processed_data_file):
            self.load_processed_data(processed_data_file)
            print('Processed data loaded successfully!')
        else:
            # Предобработка текста
            self.df['Processed_TFIDF'] = self.df['Text'].apply(self.preprocess_text_tf_idf)
            self.df['Processed_BERT'] = self.df['Text'].apply(self.preprocess_text_bert)
            self.save_processed_data(processed_data_file)
            print('Texts processed and saved successfully!')

        # Загрузка индексов
        if tfidf_pkl_file and bert_pkl_file:
            self.load_index(tfidf_pkl_file, bert_pkl_file)

    def preprocess_text_tf_idf(self, text: str) -> str:
        """
        Предобработка текста: преобразование в нижний регистр, удаление пунктуации,
        цифр и стоп-слов.

        :param text: Исходный текст.
        :return: Обработанный текст.
        """
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        text = re.sub(r'\d+', '', text)
        tokens = text.split()
        processed_tokens = [
            self.morph.parse(token)[0].normal_form
            for token in tokens if token not in self.stop_words
        ]
        return ' '.join(processed_tokens)

    def preprocess_text_bert(self, text: str) -> str:
        """
        Предобработка текста: преобразование в нижний регистр, удаление пунктуации и
        цифр.

        :param text: Исходный текст.
        :return: Обработанный текст.
        """
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def index_tfidf(self) -> None:
        """
        Индексация текстов с использованием модели TF-IDF.
        Результат сохраняется в файл 'tfidf_index.pkl'.
        """
        if not self.df.empty:
            texts = self.df['Processed_TFIDF'].tolist()
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(tqdm(texts, desc="Processing TF-IDF"))
            with open('indexes/tfidf_index.pkl', 'wb') as f:
                pickle.dump((self.tfidf_vectorizer, self.tfidf_matrix), f)

    def index_bert(self) -> None:
        """
        Индексация текстов с использованием модели BERT.
        Результат сохраняется в файл 'bert_index.pkl'.
        """
        if not self.df.empty:
            texts = self.df['Processed_BERT'].tolist()
            self.bert_embeddings = self.get_embeddings(texts)
            joblib.dump(self.bert_embeddings, 'indexes/bert_index.pkl')

    def get_embeddings(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Получение эмбеддингов для заданных текстов с использованием BERT.

        :param texts: Список текстов для обработки.
        :param batch_size: Размер батча для обработки.
        :return: Список эмбеддингов.
        """
        embeddings = []
        for i in tqdm(range(0, len(texts), batch_size), desc="Processing BERT embeddings"):
            batch_texts = texts[i:i + batch_size]
            inputs = self.tokenizer(batch_texts, return_tensors='pt', padding=True, truncation=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
                batch_embeddings = outputs.last_hidden_state[:, 0, :].numpy()
                embeddings.extend(batch_embeddings)
        return embeddings

    def load_index(self, tfidf_pkl_file: str, bert_pkl_file: str) -> None:
        """
        Загрузка ранее сохраненных индексов TF-IDF и BERT из файлов.

        :param tfidf_pkl_file: Путь к файлу PKL с моделью TF-IDF.
        :param bert_pkl_file: Путь к файлу PKL с эмбеддингами BERT.
        """
        with open(tfidf_pkl_file, 'rb') as f:
            self.tfidf_vectorizer, self.tfidf_matrix = pickle.load(f)

        with open(bert_pkl_file, 'rb') as f:
            self.bert_embeddings = joblib.load(f)

    def search_tfidf(self, query: str, top_n: int = 5) -> List[Tuple[int, str, str]]:
        """
        Поиск по индексам TF-IDF.

        :param query: Запрос для поиска.
        :param top_n: Количество результатов для возврата.
        :return: Список кортежей (id документа, текст, ссылка).
        """
        query_vector = self.tfidf_vectorizer.transform([query])
        scores = np.array(query_vector.dot(self.tfidf_matrix.T).toarray()).flatten()
        top_indices = np.argsort(scores)[::-1][:top_n]

        return [(self.df.iloc[i]['id'], self.df.iloc[i]['Category'], self.df.iloc[i]['Text'], self.df.iloc[i]['Link']) for i in top_indices]

    def search_bert(self, query: str, top_n: int = 5) -> List[Tuple[int, str, str]]:
        """
        Поиск по индексам BERT.

        :param query: Запрос для поиска.
        :param top_n: Количество результатов для возврата.
        :return: Список кортежей (id документа, текст, ссылка).
        """
        processed_query = self.preprocess_text_bert(query)
        query_embedding = self.get_embeddings([processed_query])[0].reshape(1, -1)

        similarities = cosine_similarity(query_embedding, self.bert_embeddings).flatten()
        similarities = (similarities - np.min(similarities)) / (np.max(similarities) - np.min(similarities))

        top_indices = np.argsort(similarities)[::-1][:top_n]

        return [(self.df.iloc[i]['id'], self.df.iloc[i]['Category'], self.df.iloc[i]['Text'], self.df.iloc[i]['Link']) for i in top_indices]

    def evaluate_relevance(self, query: str, response: str) -> float:
        """
        Оценка релевантности ответа запросу.

        :param query: Запрос для поиска.
        :param response: Ответ на запрос.
        :return: Оценка релевантности (косинусное сходство).
        """
        processed_query = self.preprocess_text_bert(query)
        processed_response = self.preprocess_text_bert(response)

        query_embedding = self.get_embeddings([processed_query])[0].reshape(1, -1)
        response_embedding = self.get_embeddings([processed_response])[0].reshape(1, -1)

        relevance_score = cosine_similarity(query_embedding, response_embedding).flatten()[0]
        return relevance_score

    def save_processed_data(self, file_path: str) -> None:
        """
        Сохранение предобработанных данных в файл.

        :param file_path: Путь к файлу для сохранения.
        """
        with open(file_path, 'wb') as f:
            pickle.dump(self.df, f)

    def load_processed_data(self, file_path: str) -> None:
        """
        Загрузка предобработанных данных из файла.

        :param file_path: Путь к файлу для загрузки.
        """
        with open(file_path, 'rb') as f:
            self.df = pickle.load(f)