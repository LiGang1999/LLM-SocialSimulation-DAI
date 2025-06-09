from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_server.database import Provider as DBProvider
from backend_server.database import get_db
from backend_server.server.auth import get_current_active_user
from backend_server.server.schemas import Provider, ProviderCreate, User

router = APIRouter()


@router.post("/providers", response_model=Provider, status_code=status.HTTP_201_CREATED)
async def create_provider(
    provider: ProviderCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new provider configuration for the current user.
    """
    new_provider = DBProvider(**provider.dict(), username=current_user.username)
    db.add(new_provider)
    try:
        await db.commit()
        await db.refresh(new_provider)
        return new_provider
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider with this usage already exists for the user.",
        )


@router.get("/providers", response_model=List[Provider])
async def get_providers(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all provider configurations for the current user.
    """
    result = await db.execute(select(DBProvider).where(DBProvider.username == current_user.username))
    providers = result.scalars().all()
    return providers


@router.delete("/providers/{usage}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    usage: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a provider configuration for the current user.
    """
    result = await db.execute(
        select(DBProvider).where(DBProvider.username == current_user.username, DBProvider.usage == usage)
    )
    provider = result.scalar_one_or_none()
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    await db.delete(provider)
    await db.commit()
