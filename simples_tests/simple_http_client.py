import pytest
import requests
import json
import logging
from faker import Faker

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:8080"


@pytest.fixture()
def faker_instance():
    return Faker()


@pytest.fixture()
def unique_user_data(faker_instance):
    """ Генерируем уникального пользователя"""
    return {
        "username": faker_instance.user_name() ,
        "email": faker_instance.email(),
        "password": faker_instance.password(length=12)
    }


class SimpleHttpClient:
    """Простой HTTP клиент для API тестирования"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["Content-Type"] = "application/json"

    def post(self, path: str, data: dict = None):
        """Отправка POST запроса"""
        url = f"{self.base_url}{path}"
        logger.info(f"POST {url}")
        if data:
            logger.info(f"Request body: {json.dumps(data, indent=2)}")

        response = self.session.post(url, json=data)

        logger.info(f"Response status: {response.status_code}")
        if response.text:
            logger.info(f"Response body: {response.text}")

        response.raise_for_status()
        return response.json() if response.text else None

    def get(self, path: str, params: dict = None):
        """Отправка GET запроса"""
        url = f"{self.base_url}{path}"
        logger.info(f"GET {url}")

        response = self.session.get(url, params=params)

        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        return response.json() if response.text else None


@pytest.fixture(scope="session")
def api_client(base_url):
    return SimpleHttpClient(base_url)


def test_with_http_client(api_client, unique_user_data):
    """Тест с использованием HTTP клиента"""
    # Регистрация
    user_data = api_client.post("/api/auth/register", unique_user_data)
    assert user_data["username"] == unique_user_data["username"]

    # Логин
    login_data = {
        "username": unique_user_data["username"],
        "password": unique_user_data["password"]
    }
    auth_response = api_client.post("/api/auth/login", login_data)
    assert "token" in auth_response
