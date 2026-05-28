#!/usr/bin/env python3
"""
Database Initialization Script
Инициализирует данные при первом запуске системы
Запускается только через Python
"""

import sys
from typing import Any, Dict, List

from api_client import APIError, TutorPlatformClient


def print_header(text: str):
    """Печать заголовка"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_success(text: str):
    """Печать успеха"""
    print(f"✅ {text}")


def print_error(text: str):
    """Печать ошибки"""
    print(f"❌ {text}")


def print_info(text: str):
    """Печать информации"""
    print(f"ℹ️  {text}")


def initialize_default_tutors() -> int:
    """Добавить репетиторов по умолчанию"""
    print_header("INITIALIZING DEFAULT TUTORS")
    
    client = TutorPlatformClient()
    
    default_tutors: List[Dict[str, Any]] = [
        {
            "email": "math_tutor_1@tutors.local",
            "full_name": "Dr. Sarah Johnson",
            "specialization": "Mathematics",
            "hourly_rate": 75,
            "years_experience": 8,
            "tags": ["Algebra", "Calculus", "Statistics"]
        },
        {
            "email": "math_tutor_2@tutors.local",
            "full_name": "Michael Chen",
            "specialization": "Mathematics",
            "hourly_rate": 55,
            "years_experience": 5,
            "tags": ["Algebra", "Geometry", "Calculus"]
        },
        {
            "email": "english_tutor_1@tutors.local",
            "full_name": "Emma Davis",
            "specialization": "English",
            "hourly_rate": 60,
            "years_experience": 6,
            "tags": ["Grammar", "Literature", "Writing"]
        },
        {
            "email": "physics_tutor_1@tutors.local",
            "full_name": "Prof. James Wilson",
            "specialization": "Physics",
            "hourly_rate": 80,
            "years_experience": 10,
            "tags": ["Mechanics", "Thermodynamics", "Electromagnetism"]
        },
        {
            "email": "chemistry_tutor_1@tutors.local",
            "full_name": "Dr. Lisa Anderson",
            "specialization": "Chemistry",
            "hourly_rate": 70,
            "years_experience": 7,
            "tags": ["Organic Chemistry", "Biochemistry", "Lab Techniques"]
        }
    ]
    
    created_count = 0
    failed_count = 0
    
    for tutor in default_tutors:
        try:
            result = client.add_test_tutor(**tutor)
            if result:
                print_success(f"Created: {tutor['full_name']} ({tutor['specialization']})")
                created_count += 1
            else:
                print_error(f"Failed to create: {tutor['full_name']}")
                failed_count += 1
        except APIError as e:
            print_error(f"Error creating {tutor['full_name']}: {e}")
            failed_count += 1
    
    print_info(f"Total: {created_count} created, {failed_count} failed")
    return created_count


def verify_database_schema() -> bool:
    """Проверить схему БД"""
    print_header("VERIFYING DATABASE SCHEMA")
    
    client = TutorPlatformClient()
    
    # Just check that DB is accessible
    try:
        db_info = client.db_check()
        if db_info:
            print_success("Database schema verified")
            return True
        else:
            print_error("Database check failed")
            return False
    except APIError as e:
        print_error(f"Schema verification failed: {e}")
        return False


def verify_api_health() -> bool:
    """Проверить здоровье API"""
    print_header("VERIFYING API HEALTH")
    
    client = TutorPlatformClient()
    
    try:
        health = client.health_check()
        if health:
            print_success("API is healthy")
            return True
        else:
            print_error("API health check failed")
            return False
    except APIError as e:
        print_error(f"API health check failed: {e}")
        return False


def main():
    """Главная функция инициализации"""
    print_header("TUTOR PLATFORM - DATABASE INITIALIZATION")
    
    try:
        # 1. Проверить API
        print_info("Checking API availability...")
        if not verify_api_health():
            print_error("API is not available. Please start the services first.")
            print_info("Command: docker-compose up -d")
            return 1
        
        # 2. Проверить БД
        print_info("Checking database...")
        if not verify_database_schema():
            print_error("Database schema is not ready.")
            return 1
        
        # 3. Инициализировать данные
        print_info("Initializing default tutors...")
        created = initialize_default_tutors()
        
        if created > 0:
            print_header("INITIALIZATION COMPLETE")
            print_success(f"Successfully created {created} tutors")
            print_info("System is ready for testing")
            print_info("Run: python3 api_client.py full")
            return 0
        else:
            print_error("No tutors were created")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
