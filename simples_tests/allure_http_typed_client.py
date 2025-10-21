import json

import allure
import pytest
from allure_commons.types import AttachmentType
from faker import Faker
from pydantic import BaseModel

from simples_tests.typed_http_client import TypedHttpClient, RegisterRequest, UserResponseDto, AuthRequest, AuthResponse


class AllureHttpClient(TypedHttpClient):
    """HTTP клиент с интеграцией Allure"""

    def post_typed(self, path: str, request_model: BaseModel = None, response_model: type = None,
                   step_title: str = None):
        """POST запрос с Allure шагами"""
        title = step_title or f"POST {path}"

        with allure.step(title):
            # Аттачим запрос
            if request_model:
                request_json = json.dumps(request_model.model_dump(), indent=2, ensure_ascii=False)
                allure.attach(request_json, name="Request Body", attachment_type=AttachmentType.JSON)

            # Выполняем запрос
            data = request_model.model_dump() if request_model else None
            response_data = self.post(path, data)

            # Аттачим ответ
            if response_data:
                response_json = json.dumps(response_data, indent=2, ensure_ascii=False)
                allure.attach(response_json, name="Response Body", attachment_type=AttachmentType.JSON)

            # Возвращаем типизированный результат
            if response_model and response_data:
                return response_model.model_validate(response_data)
            return response_data


class AuthAPIWithAllure(AllureHttpClient):
    """Auth API с Allure отчетностью"""

    def register(self, request: RegisterRequest) -> UserResponseDto:
        return self.post_typed(
            "/api/auth/register",
            request_model=request,
            response_model=UserResponseDto,
            step_title=f"Регистрация пользователя: {request.username}"
        )

    def login(self, request: AuthRequest) -> AuthResponse:
        return self.post_typed(
            "/api/auth/login",
            request_model=request,
            response_model=AuthResponse,
            step_title=f"Авторизация пользователя: {request.username}"
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
def allure_auth_api(base_url):
    return AuthAPIWithAllure(base_url)


@allure.feature("Аутентификация")
class TestAuthWithAllure:

    @allure.story("Регистрация и авторизация пользователя")
    def test_full_auth_flow(self, base_url, typed_user_data):
        """Полный цикл аутентификации с Allure отчетами"""
        auth_api = AuthAPIWithAllure(base_url)

        with allure.step("Регистрация нового пользователя"):
            user = auth_api.register(typed_user_data)
            assert user.username == typed_user_data.username

        with allure.step("Авторизация зарегистрированного пользователя"):
            auth_request = AuthRequest(
                username=typed_user_data.username,
                password=typed_user_data.password
            )
            auth_response = auth_api.login(auth_request)
            assert auth_response.token is not None
