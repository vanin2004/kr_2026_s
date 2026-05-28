#!/usr/bin/env python3
"""
Tutor Platform API Client
Скрипт для интеграции и тестирования API платформы поиска репетиторов
"""

import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests


@dataclass
class Config:
    """Конфигурация клиента"""
    base_url: str = "http://localhost"
    keycloak_url: str = "http://keycloak:8080"
    realm: str = "tutor-platform"
    client_id: str = "tutor-api"
    timeout: int = 10
    verify_ssl: bool = False


class APIError(Exception):
    """Базовое исключение для ошибок API"""
    pass


class TutorPlatformClient:
    """Клиент для работы с Tutor Platform API"""

    def __init__(self, config: Optional[Config] = None):
        """
        Инициализация клиента
        
        Args:
            config: Конфигурация клиента
        """
        self.config = config or Config()
        self.session = requests.Session()
        self.session.verify = self.config.verify_ssl
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None

    def _log(self, message: str, level: str = "INFO"):
        """Логирование с временной меткой"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level:8} | {message}")

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        authenticated: bool = False,
        full_url: bool = False
    ) -> Dict[str, Any]:
        """
        Выполнить HTTP запрос
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Данные для отправки
            authenticated: Требуется ли аутентификация
            full_url: Использовать ли URL как полный
            
        Returns:
            JSON ответ
            
        Raises:
            APIError: При ошибке запроса
        """
        if authenticated and not self.access_token:
            raise APIError("Требуется аутентификация. Используйте authenticate()")

        url = endpoint if full_url else urljoin(self.config.base_url, endpoint)
        headers = {"Content-Type": "application/json"}

        if authenticated:
            headers["Authorization"] = f"Bearer {self.access_token}"

        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=self.config.timeout)
            elif method == "POST":
                response = self.session.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=self.config.timeout
                )
            else:
                raise ValueError(f"Неподдерживаемый метод: {method}")

            response.raise_for_status()
            return response.json() if response.text else {}

        except requests.exceptions.Timeout:
            raise APIError(f"Timeout при обращении к {url}")
        except requests.exceptions.ConnectionError:
            raise APIError(f"Невозможно подключиться к {url}")
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_msg = error_data.get("detail", str(e))
            except:
                error_msg = str(e)
            raise APIError(f"HTTP {e.response.status_code}: {error_msg}")
        except Exception as e:
            raise APIError(f"Ошибка запроса: {str(e)}")

    def authenticate(self, username: str, password: str) -> bool:
        """
        Аутентифицироваться и получить токен доступа
        
        Args:
            username: Email пользователя
            password: Пароль
            
        Returns:
            True если успешно, False иначе
        """
        try:
            self._log(f"Аутентификация пользователя: {username}")

            token_url = urljoin(
                self.config.keycloak_url,
                f"/realms/{self.config.realm}/protocol/openid-connect/token"
            )

            response = self.session.post(
                token_url,
                data={
                    "grant_type": "password",
                    "client_id": self.config.client_id,
                    "username": username,
                    "password": password
                },
                timeout=self.config.timeout
            )

            response.raise_for_status()
            data = response.json()

            self.access_token = data["access_token"]
            self.token_expires_at = time.time() + data.get("expires_in", 300)

            self._log(f"✓ Успешная аутентификация (токен истекает через {data.get('expires_in')} сек)")
            return True

        except Exception as e:
            self._log(f"✗ Ошибка аутентификации: {e}", "ERROR")
            return False

    def is_authenticated(self) -> bool:
        """Проверить, аутентифицирован ли клиент и токен еще действителен"""
        if not self.access_token or not self.token_expires_at:
            return False
        return time.time() < self.token_expires_at

    def health_check(self) -> bool:
        """
        Проверить здоровье API
        
        Returns:
            True если API работает, False иначе
        """
        try:
            self._log("Проверка здоровья API...")
            result = self._request("GET", "/api/custom/health")
            
            self._log(
                f"✓ API здоров: {result.get('status')} "
                f"(версия {result.get('version')})"
            )
            return True
        except APIError as e:
            self._log(f"✗ API недоступен: {e}", "ERROR")
            return False

    def db_check(self) -> bool:
        """
        Проверить подключение к БД
        
        Returns:
            True если БД доступна, False иначе
        """
        try:
            self._log("Проверка подключения к БД...")
            result = self._request("GET", "/api/custom/db-check")
            
            self._log(
                f"✓ БД подключена: {result.get('database_name')} "
                f"(PostgreSQL {result.get('postgres_version')})"
            )
            return True
        except APIError as e:
            self._log(f"✗ Ошибка БД: {e}", "ERROR")
            return False

    def auth_check(self) -> bool:
        """
        Проверить валидность токена
        
        Returns:
            True если токен действителен, False иначе
        """
        try:
            self._log("Проверка валидности токена...")
            result = self._request("GET", "/api/custom/auth-check", authenticated=True)
            
            self._log(
                f"✓ Токен действителен для {result.get('email')} "
                f"(роли: {', '.join(result.get('roles', []))})"
            )
            return True
        except APIError as e:
            self._log(f"✗ Ошибка аутентификации: {e}", "ERROR")
            return False

    def add_test_tutor(
        self,
        email: str,
        full_name: str,
        specialization: str,
        hourly_rate: int,
        years_experience: int,
        tags: List[str]
    ) -> Optional[Dict]:
        """
        Добавить тестового репетитора
        
        Args:
            email: Email репетитора
            full_name: Полное имя
            specialization: Предмет специализации
            hourly_rate: Ставка за час
            years_experience: Лет опыта
            tags: Список навыков/тегов
            
        Returns:
            Данные созданного репетитора или None при ошибке
        """
        try:
            self._log(f"Добавление тестового репетитора: {full_name}")

            data = {
                "email": email,
                "full_name": full_name,
                "specialization": specialization,
                "hourly_rate": hourly_rate,
                "years_experience": years_experience,
                "tags": tags
            }

            result = self._request("POST", "/api/custom/test-data", data=data)
            
            self._log(
                f"✓ Репетитор создан (ID: {result['id']}, "
                f"ставка: ${result.get('hourly_rate')}/час)"
            )
            return result

        except APIError as e:
            self._log(f"✗ Ошибка при создании репетитора: {e}", "ERROR")
            return None

    def get_suggestions(
        self,
        subject: str,
        max_rate: int,
        min_experience: int,
        desired_tags: Optional[List[str]] = None,
        weights: Optional[Dict[str, float]] = None
    ) -> Optional[List[Dict]]:
        """
        Получить рекомендации репетиторов
        
        Args:
            subject: Предмет обучения
            max_rate: Максимальная ставка
            min_experience: Минимальный опыт (лет)
            desired_tags: Желаемые навыки
            weights: Веса для алгоритма скоринга
            
        Returns:
            Список репетиторов или None при ошибке
        """
        try:
            self._log(
                f"Поиск репетиторов по {subject} "
                f"(макс ${max_rate}/час, мин {min_experience} лет)"
            )

            data = {
                "subject": subject,
                "max_rate": max_rate,
                "min_experience": min_experience,
                "desired_tags": desired_tags or [],
                "weights": weights or {
                    "efficiency": 0.30,
                    "communication": 0.15,
                    "overall": 0.20,
                    "responsiveness": 0.15,
                    "tags": 0.20
                }
            }

            result = self._request(
                "POST",
                "/api/custom/suggestions",
                data=data,
                authenticated=True
            )

            self._log(f"✓ Найдено {len(result)} репетиторов")
            
            for i, tutor in enumerate(result, 1):
                self._log(
                    f"  {i}. {tutor['full_name']} "
                    f"(Score: {tutor.get('match_score', 0):.1f}%, "
                    f"${tutor.get('hourly_rate')}/час, "
                    f"★{tutor.get('rating_overall', 0):.1f})"
                )

            return result

        except APIError as e:
            self._log(f"✗ Ошибка поиска: {e}", "ERROR")
            return None

    def recalculate_ratings(
        self,
        run_efficiency: bool = True,
        run_communication: bool = True
    ) -> Optional[Dict]:
        """
        Пересчитать рейтинги репетиторов
        
        Args:
            run_efficiency: Пересчитать рейтинг эффективности
            run_communication: Пересчитать рейтинг общения
            
        Returns:
            Статус выполнения или None при ошибке
        """
        try:
            self._log("Запуск пересчета рейтингов...")

            data = {
                "run_efficiency": run_efficiency,
                "run_communication": run_communication
            }

            result = self._request(
                "POST",
                "/api/custom/jobs/recalculate-ratings",
                data=data,
                authenticated=True
            )

            self._log(
                f"✓ Рейтинги пересчитаны ({result.get('tutors_updated')} репетиторов, "
                f"{result.get('execution_time_seconds', 0):.2f}с)"
            )
            return result

        except APIError as e:
            self._log(f"✗ Ошибка пересчета: {e}", "ERROR")
            return None


def demo_full_flow():
    """Полная демонстрация работы API"""
    
    client = TutorPlatformClient()
    
    print("\n" + "="*70)
    print("TUTOR PLATFORM API CLIENT - ПОЛНАЯ ДЕМОНСТРАЦИЯ")
    print("="*70 + "\n")

    # 1. Проверка здоровья
    if not client.health_check():
        print("\n❌ API недоступен. Убедитесь, что контейнеры запущены:")
        print("   cd backend && docker-compose up -d")
        return

    # 2. Проверка БД
    if not client.db_check():
        print("\n❌ БД недоступна. Проверьте logs:")
        print("   docker-compose logs postgres")
        return

    # 3. Аутентификация (опционально)
    print("\n--- Тестирование аутентификации ---")
    if client.authenticate("admin@example.com", "admin_password"):
        client.auth_check()
    else:
        print("⚠️  Пропускаем аутентификацию (токен не требуется для некоторых операций)\n")

    # 4. Добавить тестовых репетиторов
    print("\n--- Добавление тестовых репетиторов ---")
    tutors_data = [
        {
            "email": "tutor1@example.com",
            "full_name": "Dr. Sarah Johnson",
            "specialization": "Mathematics",
            "hourly_rate": 75,
            "years_experience": 8,
            "tags": ["Algebra", "Calculus", "Statistics"]
        },
        {
            "email": "tutor2@example.com",
            "full_name": "Michael Chen",
            "specialization": "Mathematics",
            "hourly_rate": 55,
            "years_experience": 5,
            "tags": ["Algebra", "Geometry", "Calculus"]
        },
        {
            "email": "tutor3@example.com",
            "full_name": "Emma Davis",
            "specialization": "English",
            "hourly_rate": 60,
            "years_experience": 6,
            "tags": ["Grammar", "Literature", "Writing"]
        }
    ]

    for tutor in tutors_data:
        client.add_test_tutor(**tutor)
        time.sleep(0.5)  # Задержка между запросами

    # 5. Поиск репетиторов
    print("\n--- Поиск репетиторов по Математике ---")
    if client.is_authenticated():
        suggestions = client.get_suggestions(
            subject="Mathematics",
            max_rate=100,
            min_experience=2,
            desired_tags=["Algebra", "Calculus"],
            weights={
                "efficiency": 0.40,
                "communication": 0.20,
                "overall": 0.15,
                "responsiveness": 0.15,
                "tags": 0.10
            }
        )

        if suggestions:
            print("\n📊 Детали лучших репетиторов:")
            for i, tutor in enumerate(suggestions[:2], 1):
                print(f"\n  Репетитор #{i}: {tutor['full_name']}")
                print(f"    ID: {tutor['id']}")
                print(f"    Ставка: ${tutor.get('hourly_rate')}/час")
                print(f"    Опыт: {tutor.get('years_experience')} лет")
                print("    Рейтинги:")
                print(f"      - Эффективность: ★{tutor.get('rating_efficiency', 0):.1f}/5.0")
                print(f"      - Общение: ★{tutor.get('rating_communication', 0):.1f}/5.0")
                print(f"      - Общий: ★{tutor.get('rating_overall', 0):.1f}/5.0")
                print(f"    Навыки: {', '.join(tutor.get('tags', []))}")
                print(f"    🎯 Score: {tutor.get('match_score', 0):.1f}%")
    else:
        print("\n⚠️  Аутентификация требуется для поиска репетиторов")

    # 6. Пересчет рейтингов
    print("\n--- Пересчет рейтингов ---")
    if client.is_authenticated():
        client.recalculate_ratings(run_efficiency=True, run_communication=True)
    else:
        print("⚠️  Требуется аутентификация")

    print("\n" + "="*70)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*70 + "\n")


def demo_quick_search():
    """Быстрый поиск репетиторов"""
    
    client = TutorPlatformClient()
    
    print("\n--- Быстрый поиск репетиторов ---\n")

    if not client.health_check():
        return

    if not client.db_check():
        return

    # Попытка аутентификации
    client.authenticate("admin@example.com", "admin_password")

    if client.is_authenticated():
        client.get_suggestions(
            subject="Mathematics",
            max_rate=100,
            min_experience=2
        )
    else:
        print("⚠️  Пропуск поиска (требуется аутентификация)")


def main():
    """Главная функция"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "quick":
            demo_quick_search()
        elif command == "full":
            demo_full_flow()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python api_client.py [quick|full]")
    else:
        demo_full_flow()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)
