import json
import os
import time
import warnings
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from urllib3.exceptions import InsecureRequestWarning

load_dotenv()

warnings.simplefilter("ignore", InsecureRequestWarning)


def get_access_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {"scope": "GIGACHAT_API_PERS"}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "42154363-8912-48b2-9dd9-6067e9823414",
        "Authorization": f'Basic {os.getenv("API_KEY")}',
    }

    access_response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False
    )
    access_token = access_response.json()["access_token"]
    return access_token


def send_request_to_gigachat(user_input, access_token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    payload = json.dumps(
        {
            "model": "GigaChat",
            "messages": [{"role": "user", "content": f"{user_input}"}],
            "stream": False,
            "update_interval": 0,
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False
    )
    response_json = response.json()

    if response.status_code == 200:
        return response_json["choices"][0]["message"]["content"]
    else:
        return f"Ошибка: {response.status_code} - {response_json.get('message', 'Неизвестная ошибка')}"


def chat():
    access_token = get_access_token()
    token_expiry = datetime.now() + timedelta(minutes=30)

    print("Добро пожаловать! Введите запрос для Gigachat или 'exit' для выхода.")

    while True:
        user_input = input("Ваш запрос: ")

        # Проверка на выход
        if user_input.lower() == "exit":
            print("Выход из программы. До свидания!")
            break

        # Проверяем, не истек ли токен
        if datetime.now() >= token_expiry:
            print("Токен истек. Получаем новый токен...")
            access_token = get_access_token()
            token_expiry = datetime.now() + timedelta(minutes=30)

        response = send_request_to_gigachat(user_input, access_token)
        print(f"Ответ Gigachat: {response}\n")


if __name__ == "__main__":
    chat()
