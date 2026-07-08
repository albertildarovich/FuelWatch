"""
Интеграционные тесты API endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Регистрация нового пользователя должна возвращать 201"""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "strong_password_123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data  # пароль не должен возвращаться


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Повторная регистрация с тем же email — ошибка 400"""
    # Регистрируем первого
    await client.post(
        "/api/auth/register",
        json={"email": "duplicate@test.com", "password": "pass123"},
    )
    # Пробуем снова
    response = await client.post(
        "/api/auth/register",
        json={"email": "duplicate@test.com", "password": "pass456"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Логин с верными данными — получаем токены"""
    # Сначала регистрируемся
    await client.post(
        "/api/auth/register",
        json={"email": "login@test.com", "password": "password123"},
    )
    # Логинимся
    response = await client.post(
        "/api/auth/login",
        json={"email": "login@test.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Логин с неверным паролем — 401"""
    await client.post(
        "/api/auth/register",
        json={"email": "wrongpass@test.com", "password": "correct_pass"},
    )
    response = await client.post(
        "/api/auth/login",
        json={"email": "wrongpass@test.com", "password": "wrong_pass"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_stations(client: AsyncClient):
    """Список АЗС должен возвращаться"""
    response = await client.get("/api/stations/")
    assert response.status_code == 200
    # В тестовой БД пока пусто — это ок
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_fuel_types(client: AsyncClient):
    """Список типов топлива"""
    response = await client.get("/api/stations/fuel-types")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_prices(client: AsyncClient):
    """Цены должны возвращаться списком"""
    response = await client.get("/api/prices/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
