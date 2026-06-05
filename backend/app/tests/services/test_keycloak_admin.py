"""
Тесты для интеграции с Keycloak — Admin API.

Проверяют:
1. Admin API Keycloak (создание/чтение/удаление пользователей и ролей)
2. Direct Access Grants (OAuth2 password flow — вход пользователя)
3. Полный жизненный цикл: регистрация → вход → повторный вход → удаление → невозможность входа

Для запуска требуется работающий Keycloak (docker-compose up).
По умолчанию Keycloak доступен на http://localhost:8081/auth
"""

import os
import unittest
import uuid

import pytest
import requests

pytestmark = pytest.mark.integration

# -------------------------------------------------------------------
# Конфигурация — подтягиваем из окружения или используем значения по умолчанию
# -------------------------------------------------------------------
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL", "http://localhost:8080")
"""Базовый URL Keycloak (без /auth) — для обращений через Nginx, который проксирует /auth/ на Keycloak.
По умолчанию используется порт 8080, соответствующий стандартной конфигурации docker-compose."""

KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "tutorapp")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "tutorapp-client")

KEYCLOAK_ADMIN_USER = os.getenv("KEYCLOAK_ADMIN_USER", "admin")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")


def _kc_url(path: str) -> str:
    """
    Формирует полный URL к Keycloak через nginx.
    Nginx проксирует /auth/ на Keycloak (см. nginx.conf),
    поэтому все пути к Keycloak должны начинаться с /auth/.
    Пример: _kc_url("realms/master/protocol/openid-connect/token")
             -> http://localhost/auth/realms/master/protocol/openid-connect/token
    """
    path = path.lstrip("/")
    return f"{KEYCLOAK_BASE_URL}/auth/{path}"


# URL-ы Keycloak (через nginx)
TOKEN_URL = _kc_url(f"realms/{KEYCLOAK_REALM}/protocol/openid-connect/token")
ADMIN_USERS_URL = _kc_url(f"admin/realms/{KEYCLOAK_REALM}/users")
ADMIN_ROLES_URL = _kc_url(f"admin/realms/{KEYCLOAK_REALM}/roles")


def get_admin_token() -> str:
    """
    Получает admin-токен от Keycloak с использованием master realm.
    """
    master_token_url = _kc_url("realms/master/protocol/openid-connect/token")
    resp = requests.post(
        master_token_url,
        data={
            "client_id": "admin-cli",
            "username": KEYCLOAK_ADMIN_USER,
            "password": KEYCLOAK_ADMIN_PASSWORD,
            "grant_type": "password",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


class TestKeycloakAdminAPI(unittest.TestCase):
    """Тесты Admin API Keycloak — создание, поиск, удаление пользователей."""

    @classmethod
    def setUpClass(cls):
        """Получаем admin-токен один раз для всех тестов в классе."""
        cls.admin_token = get_admin_token()
        cls.admin_headers = {
            "Authorization": f"Bearer {cls.admin_token}",
            "Content-Type": "application/json",
        }

    def setUp(self):
        """Генерируем уникальные данные для каждого теста."""
        self.unique_tag = uuid.uuid4().hex[:8]
        self.test_username = f"test_user_{self.unique_tag}"
        self.test_email = f"{self.unique_tag}@example.com"
        self.test_password = "testP@ss123"

    def tearDown(self):
        """Удаляем созданного пользователя после каждого теста (если он есть)."""
        # Ищем пользователя по username
        search_resp = requests.get(
            ADMIN_USERS_URL,
            headers=self.admin_headers,
            params={"username": self.test_username},
            timeout=10,
        )
        if search_resp.status_code == 200 and search_resp.json():
            user_id = search_resp.json()[0]["id"]
            requests.delete(
                f"{ADMIN_USERS_URL}/{user_id}",
                headers=self.admin_headers,
                timeout=10,
            )

    def _create_test_user(self) -> str | None:
        """
        Создаёт тестового пользователя через Admin API.
        Возвращает ID созданного пользователя или None.
        """
        resp = requests.post(
            ADMIN_USERS_URL,
            headers=self.admin_headers,
            json={
                "username": self.test_username,
                "email": self.test_email,
                "enabled": True,
                "credentials": [
                    {
                        "type": "password",
                        "value": self.test_password,
                        "temporary": False,
                    }
                ],
            },
            timeout=10,
        )
        if resp.status_code == 201:
            # Достаём ID из Location header
            location = resp.headers.get("Location", "")
            return location.rstrip("/").split("/")[-1] if location else None
        return None

    # ------------------------------------------------------------------
    # 1. Admin API: CRUD пользователей
    # ------------------------------------------------------------------
    def test_01_create_user(self):
        """Создание пользователя через Admin API."""
        user_id = self._create_test_user()
        self.assertIsNotNone(user_id, "Не удалось создать пользователя")

    def test_02_get_user_by_username(self):
        """Поиск пользователя по username через Admin API."""
        # Сначала создаём
        self._create_test_user()

        # Ищем
        search_resp = requests.get(
            ADMIN_USERS_URL,
            headers=self.admin_headers,
            params={"username": self.test_username},
            timeout=10,
        )
        self.assertEqual(search_resp.status_code, 200)
        data = search_resp.json()
        self.assertGreater(len(data), 0, "Должен быть найден хотя бы один пользователь")
        self.assertEqual(data[0]["username"], self.test_username)
        self.assertEqual(data[0]["email"], self.test_email)
        self.assertIn("id", data[0], "Пользователь должен иметь id")

    def test_03_delete_user(self):
        """Удаление пользователя через Admin API."""
        # Создаём
        self._create_test_user()

        # Ищем, чтобы получить ID
        search_resp = requests.get(
            ADMIN_USERS_URL,
            headers=self.admin_headers,
            params={"username": self.test_username},
            timeout=10,
        )
        if search_resp.status_code == 200 and search_resp.json():
            user_id = search_resp.json()[0]["id"]

            # Удаляем
            delete_resp = requests.delete(
                f"{ADMIN_USERS_URL}/{user_id}",
                headers=self.admin_headers,
                timeout=10,
            )
            self.assertEqual(
                delete_resp.status_code,
                204,
                f"Ожидался 204 при удалении, получен {delete_resp.status_code}",
            )

            # Проверяем, что пользователь действительно удалён
            check_resp = requests.get(
                ADMIN_USERS_URL,
                headers=self.admin_headers,
                params={"username": self.test_username},
                timeout=10,
            )
            self.assertEqual(len(check_resp.json()), 0)

    def test_04_get_realm_roles(self):
        """Получение списка realm-ролей (tutor, student)."""
        resp = requests.get(ADMIN_ROLES_URL, headers=self.admin_headers, timeout=10)
        self.assertEqual(resp.status_code, 200)
        roles = resp.json()
        role_names = [r["name"] for r in roles]
        self.assertIn("tutor", role_names, "В реалме должна быть роль 'tutor'")
        self.assertIn("student", role_names, "В реалме должна быть роль 'student'")

    # ------------------------------------------------------------------
    # 2. Direct Access Grants: OAuth2 password flow
    # ------------------------------------------------------------------
    def test_05_direct_access_grants_login(self):
        """Аутентификация пользователя через Direct Access Grants (password flow)."""
        # Сначала создаём пользователя через Admin API
        self._create_test_user()

        # Логинимся как этот пользователь
        token_resp = requests.post(
            TOKEN_URL,
            data={
                "client_id": KEYCLOAK_CLIENT_ID,
                "username": self.test_username,
                "password": self.test_password,
                "grant_type": "password",
            },
            timeout=10,
        )
        self.assertEqual(
            token_resp.status_code, 200, f"Ошибка аутентификации: {token_resp.text}"
        )
        token_data = token_resp.json()

        # Проверяем структуру ответа
        self.assertIn("access_token", token_data)
        self.assertIn("refresh_token", token_data)
        self.assertIn("expires_in", token_data)
        self.assertIn("token_type", token_data)
        self.assertEqual(token_data["token_type"], "Bearer")

        # access_token должен быть JWT (проверяем базово)
        parts = token_data["access_token"].split(".")
        self.assertEqual(
            len(parts), 3, "Токен должен быть JWT формата header.payload.signature"
        )

    def test_06_direct_access_grants_wrong_password(self):
        """Попытка входа с неверным паролем должна вернуть 401."""
        # Пользователь не создаётся — используем заведомо несуществующего
        resp = requests.post(
            TOKEN_URL,
            data={
                "client_id": KEYCLOAK_CLIENT_ID,
                "username": f"nonexistent_{self.unique_tag}",
                "password": "wrong_password",
                "grant_type": "password",
            },
            timeout=10,
        )
        self.assertEqual(
            resp.status_code,
            401,
            f"Ожидался 401, получен {resp.status_code}: {resp.text}",
        )

    # ------------------------------------------------------------------
    # 3. Полный жизненный цикл: регистрация → вход → повторный вход → удаление → невозможность входа
    # ------------------------------------------------------------------
    def test_07_full_lifecycle_register_login_delete_cannot_login(self):
        """
        Имитация полного жизненного цикла пользователя:
        1. Регистрация (создание в Keycloak через Admin API)
        2. Вход — получение access_token и refresh_token
        3. Повторный вход — получение ещё одного токена (имитация повторного визита)
        4. Удаление аккаунта через Admin API
        5. Попытка входа после удаления — должна вернуть ошибку 401
        """
        # ---- 1. Регистрация пользователя ----
        user_id = self._create_test_user()
        self.assertIsNotNone(user_id, "Пользователь должен быть создан")
        assert user_id is not None
        self.assertGreater(len(user_id), 0, "ID пользователя не должен быть пустым")

        # ---- 2. Первый вход (имитация: пользователь только что зарегистрировался) ----
        login1_resp = requests.post(
            TOKEN_URL,
            data={
                "client_id": KEYCLOAK_CLIENT_ID,
                "username": self.test_username,
                "password": self.test_password,
                "grant_type": "password",
            },
            timeout=10,
        )
        self.assertEqual(
            login1_resp.status_code,
            200,
            f"Первый вход должен быть успешным. Ошибка: {login1_resp.text}",
        )
        login1_data = login1_resp.json()
        self.assertIn(
            "access_token", login1_data, "При первом входе должен быть access_token"
        )
        self.assertIn(
            "refresh_token", login1_data, "При первом входе должен быть refresh_token"
        )
        first_access_token = login1_data["access_token"]
        first_refresh_token = login1_data["refresh_token"]

        # Убедимся, что токен — это JWT
        self.assertEqual(
            len(first_access_token.split(".")),
            3,
            "access_token должен быть JWT формата header.payload.signature",
        )

        # ---- 3. Повторный вход пользователя (имитация: вернулся на следующий день) ----
        login2_resp = requests.post(
            TOKEN_URL,
            data={
                "client_id": KEYCLOAK_CLIENT_ID,
                "username": self.test_username,
                "password": self.test_password,
                "grant_type": "password",
            },
            timeout=10,
        )
        self.assertEqual(
            login2_resp.status_code,
            200,
            f"Повторный вход должен быть успешным. Ошибка: {login2_resp.text}",
        )
        login2_data = login2_resp.json()
        self.assertIn(
            "access_token", login2_data, "При повторном входе должен быть access_token"
        )
        self.assertIn(
            "refresh_token",
            login2_data,
            "При повторном входе должен быть refresh_token",
        )

        # Проверим, что токены разные (это разные сессии)
        self.assertNotEqual(
            login2_data["access_token"],
            first_access_token,
            "Токены при разных входах должны отличаться",
        )
        self.assertNotEqual(
            login2_data["refresh_token"],
            first_refresh_token,
            "Refresh-токены при разных входах должны отличаться",
        )

        # ---- 4. Удаление аккаунта через Admin API ----
        delete_resp = requests.delete(
            f"{ADMIN_USERS_URL}/{user_id}",
            headers=self.admin_headers,
            timeout=10,
        )
        self.assertEqual(
            delete_resp.status_code,
            204,
            f"Удаление пользователя должно вернуть 204. Получено: {delete_resp.status_code}",
        )

        # Проверяем, что пользователь действительно удалён
        check_deleted = requests.get(
            ADMIN_USERS_URL,
            headers=self.admin_headers,
            params={"username": self.test_username},
            timeout=10,
        )
        self.assertEqual(
            len(check_deleted.json()),
            0,
            "После удаления пользователь не должен находиться поиском",
        )

        # ---- 5. Попытка входа после удаления — должна завершиться ошибкой ----
        login_after_delete_resp = requests.post(
            TOKEN_URL,
            data={
                "client_id": KEYCLOAK_CLIENT_ID,
                "username": self.test_username,
                "password": self.test_password,
                "grant_type": "password",
            },
            timeout=10,
        )
        self.assertEqual(
            login_after_delete_resp.status_code,
            401,
            f"Вход после удаления должен возвращать 401. "
            f"Получен {login_after_delete_resp.status_code}: {login_after_delete_resp.text}",
        )

        # Проверяем, что в ответе есть признак ошибки аутентификации
        error_data = login_after_delete_resp.json()
        self.assertIn(
            "error", error_data, "Ответ с ошибкой должен содержать поле 'error'"
        )
