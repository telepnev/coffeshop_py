import pytest
from faker import Faker
from pydantic import BaseModel

from simples_tests.simple_http_client import SimpleHttpClient


# запрос
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


# ответ
class UserResponseDto(BaseModel):
    id: int
    username: str
    email: str
    role: str


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: UserResponseDto


class TypedHttpClient(SimpleHttpClient):
    """HTTP клиент с поддержкой Pydantic моделей"""

    def post_typed(self, path: str, request_model: BaseModel = None, response_model: type = None):
        """POST запрос с типизацией"""
        data = request_model.model_dump() if request_model else None
        response_data = self.post(path, data)

        if response_model and response_data:
            return response_model.model_validate(response_data)
        return response_data


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:8080"


@pytest.fixture(scope="session")
def typed_api_client(base_url):
    return TypedHttpClient(base_url)


@pytest.fixture()
def faker_instance():
    return Faker()


@pytest.fixture()
def unique_user_data(faker_instance):
    """ Генерируем уникального пользователя"""
    return {
        "username": faker_instance.user_name(),
        "email": faker_instance.email(),
        "password": faker_instance.password(length=12)
    }


@pytest.fixture
def typed_user_data(faker_instance):
    """Типизированные данные пользователя"""
    return RegisterRequest(
        username=faker_instance.user_name() + str(faker_instance.random_int(1000, 9999)),
        email=faker_instance.email(),
        password=faker_instance.password(length=12)

    )


def test_with_typed_models(base_url, typed_user_data):
    """Тест с типизированными моделями"""
    client = TypedHttpClient(base_url)

    # Регистрация с типизацией
    user_response = client.post_typed(
        "/api/auth/register",
        request_model=typed_user_data,
        response_model=UserResponseDto
    )

    assert user_response.username == typed_user_data.username
    assert user_response.email == typed_user_data.email

    # Логин с типизацией
    auth_request = AuthRequest(
        username=typed_user_data.username,
        password=typed_user_data.password
    )

    auth_response = client.post_typed(
        "/api/auth/login",
        request_model=auth_request,
        response_model=AuthResponse
    )

    assert auth_response.token is not None
    assert auth_response.user.username == typed_user_data.username


def test_with_specialized_client(auth_api, typed_user_data):
    """Тест со специализированным API клиентом"""
    # Регистрация
    user = auth_api.register(typed_user_data)
    assert user.username == typed_user_data.username

    # Логин
    auth_request = AuthRequest(
        username=typed_user_data.username,
        password=typed_user_data.password
    )
    auth_response = auth_api.login(auth_request)
    assert auth_response.token is not None