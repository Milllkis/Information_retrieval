import requests

# Базовый URL для API
base_url = "http://127.0.0.1:8000/api"

# Поиск по запросу с использованием метода TF-IDF
search_payload = {
    "query": "Мария",
    "method": "tf-idf",
    "limit": 1
}
response = requests.post(f"{base_url}/search", json=search_payload)
print(response.json())

# Поиск по запросу с использованием метода BERT
search_payload = {
    "query": "Мария",
    "method": "bert",
    "limit": 1
}
response = requests.post(f"{base_url}/search", json=search_payload)
print(response.json())