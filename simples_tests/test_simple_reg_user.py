import pytest
import requests
from faker import Faker


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


@pytest.fixture
def registered_user(base_url, unique_user_data):
    """Фикстура для создания зарегистрированного пользователя"""
    url = f"{base_url}/api/auth/register"
    response = requests.post(url, json=unique_user_data)
    user_data = response.json()

    return {
        "user_info": user_data,
        "credentials": unique_user_data
    }


def test_login_with_registered_user(base_url, registered_user):
    """Тест логина с использованием фикстуры зарегистрированного пользователя"""
    url = f"{base_url}/api/auth/login"
    payload = {
        "username": registered_user["credentials"]["username"],
        "password": registered_user["credentials"]["password"]
    }

    response = requests.post(url, json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data


