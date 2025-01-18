import os


class Config:
    TFIDF_INDEX_PATH = os.getenv('TFIDF_INDEX_PATH', 'indexes/tfidf_index.pkl')
    BERT_INDEX_PATH = os.getenv('BERT_INDEX_PATH', 'indexes/bert_index.pkl')
    DATA_PATH = os.getenv('DATA_PATH', 'new_biographies.csv')


CONFIG = Config()