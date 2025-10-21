import pytest
from faker import Faker

from simples_tests.typed_http_client import TypedHttpClient, RegisterRequest, UserResponseDto, AuthRequest, AuthResponse


class AuthAPI(TypedHttpClient):
    """Специализированный клиент для работы с аутентификацией"""

    def register(self, request: RegisterRequest) -> UserResponseDto:
        """Регистрация пользователя"""
        return self.post_typed(
            "/api/auth/register",
            request_model=request,
            response_model=UserResponseDto
        )

    def login(self, request: AuthRequest) -> AuthResponse:
        """Авторизация пользователя"""
        return self.post_typed(
            "/api/auth/login",
            request_model=request,
            response_model=AuthResponse
        )


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:8080"


@pytest.fixture()
def faker_instance():
    return Faker()


@pytest.fixture
def typed_user_data(faker_instance):
    """Типизированные данные пользователя"""
    return RegisterRequest(
        username=faker_instance.user_name() + str(faker_instance.random_int(1000, 9999)),
        email=faker_instance.email(),
        password=faker_instance.password(length=12)

    )


@pytest.fixture(scope="session")
def auth_api(base_url):
    return AuthAPI(base_url)


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
