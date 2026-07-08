"""
Тесты для AuthService: регистрация, логин, JWT.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.auth import AuthService


@pytest.mark.asyncio
async def test_hash_password():
    """Пароль должен хешироваться и не совпадать с оригиналом"""
    password = "test_password_123"
    hashed = AuthService.hash_password(password)

    assert hashed != password
    assert AuthService.verify_password(password, hashed) is True


@pytest.mark.asyncio
async def test_verify_password_wrong():
    """Неверный пароль не должен проходить проверку"""
    hashed = AuthService.hash_password("correct_password")
    assert AuthService.verify_password("wrong_password", hashed) is False


@pytest.mark.asyncio
async def test_create_access_token():
    """Access токен должен создаваться и содержать нужные поля"""
    data = {"sub": "test-user-id", "email": "test@example.com"}
    token = AuthService.create_access_token(data)

    assert token is not None
    assert isinstance(token, str)
    assert len(token.split(".")) == 3  # JWT состоит из 3 частей


@pytest.mark.asyncio
async def test_create_refresh_token():
    """Refresh токен должен создаваться"""
    data = {"sub": "test-user-id"}
    token = AuthService.create_refresh_token(data)

    assert token is not None
    assert isinstance(token, str)
    assert len(token.split(".")) == 3


@pytest.mark.asyncio
async def test_register_user_duplicate_email():
    """Попытка регистрации с существующим email должна вызывать ошибку"""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock()  # пользователь уже есть
    mock_db.execute.return_value = mock_result

    service = AuthService(mock_db)

    from app.schemas.user import UserCreate
    from fastapi import HTTPException

    user_data = UserCreate(email="existing@test.com", password="password123")

    with pytest.raises(HTTPException) as exc_info:
        await service.register(user_data)

    assert exc_info.value.status_code == 400
    assert "already registered" in str(exc_info.value.detail).lower()


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Логин с неверными данными должен возвращать 401"""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None  # пользователь не найден
    mock_db.execute.return_value = mock_result

    service = AuthService(mock_db)

    from app.schemas.user import UserLogin
    from fastapi import HTTPException

    credentials = UserLogin(email="nonexistent@test.com", password="wrong")

    with pytest.raises(HTTPException) as exc_info:
        await service.login(credentials)

    assert exc_info.value.status_code == 401
