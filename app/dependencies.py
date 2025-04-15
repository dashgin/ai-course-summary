from collections.abc import Generator
from typing import Annotated
import time

import jwt
import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from app.protocols import LLMService
from app.services.llm import OpenAILLMService


def get_redis_client() -> redis.Redis:
    """Dependency for getting the Redis client"""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )


def get_openai_service() -> LLMService:
    """Dependency for getting the LLM service"""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured",
        )
    return OpenAILLMService(api_key=settings.OPENAI_API_KEY)


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def check_rate_limit(
    user_id: int, redis_client: redis.Redis, max_requests: int = 3, window_seconds: int = 3600
) -> bool:
    """
    Check if the user has exceeded their rate limit for AI summaries.
    
    Args:
        user_id: The user's ID
        redis_client: Redis client
        max_requests: Maximum number of requests allowed in the time window
        window_seconds: Time window in seconds (default: 1 hour)
        
    Returns:
        bool: True if the user has not exceeded their rate limit, False otherwise
    """
    key = f"rate_limit:ai_summary:{user_id}"
    current_time = int(time.time())
    
    # Remove timestamps older than the window
    redis_client.zremrangebyscore(key, 0, current_time - window_seconds)
    
    # Count number of requests in the current window
    current_count = redis_client.zcard(key)
    
    # Check if the user has exceeded the rate limit
    if current_count > max_requests:
        return False
    
    # Add the current timestamp to the sorted set
    redis_client.zadd(key, {str(current_time): current_time})
    
    # Set the expiration for the key to the window time
    redis_client.expire(key, window_seconds)
    
    return True


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
OpenAILLMServiceDep = Annotated[OpenAILLMService, Depends(get_openai_service)]
RedisDep = Annotated[redis.Redis, Depends(get_redis_client)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
