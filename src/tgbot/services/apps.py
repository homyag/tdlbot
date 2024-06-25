import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')


def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_managers():
    # API_URL_MANAGERS = "http://127.0.0.1:8000/api/v1/managers/"
    API_URL_MANAGERS = "https://tdleningrad.ru/api/v1/managers/"
    headers = {'Authorization': f'{API_TOKEN}'}
    response = requests.get(API_URL_MANAGERS, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def get_results():
    # API_URL_RESULTS = "http://127.0.0.1:8000/api/v1/results/"
    API_URL_RESULTS = "https://tdleningrad.ru/api/v1/results/"
    headers = {'Authorization': f'{API_TOKEN}'}
    response = requests.get(API_URL_RESULTS, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []