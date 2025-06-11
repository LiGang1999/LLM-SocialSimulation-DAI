from typing import Dict

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_server.database import Provider as DBProvider
from backend_server.database import get_db
from backend_server.server.auth import get_current_active_user
from backend_server.server.schemas import User
from backend_server.utils.config import enable_default_llm
from backend_server.utils.llm import LLMConfig


async def get_user_providers(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
) -> Dict[str, LLMConfig]:
    """
    Returns a dictionary of available providers for the current user.
    """
    result = await db.execute(select(DBProvider).where(DBProvider.username == current_user.username))
    providers = result.scalars().all()
    provider_configs = {
        provider.usage: {
            "kind": provider.kind,
            "base_url": provider.base_url,
            "api_key": provider.api_key,
            "model": provider.model,
            "temperature": provider.temperature,
            "max_tokens": provider.max_tokens,
            "top_p": provider.top_p,
            "frequency_penalty": provider.frequency_penalty,
            "presence_penalty": provider.presence_penalty,
            "stream": provider.stream,
        }
        for provider in providers
    }
    if not provider_configs and enable_default_llm:
        from backend_server.utils.config import default_providers

        return default_providers
    return provider_configs
