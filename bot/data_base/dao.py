import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .base import connection
from .database import AsyncSession
from .models import User


@connection
async def update_user(
    session: AsyncSession,
    tg_id: int,
    username: str,
    name: int,
) -> User:
    try:
        user = await session.scalar(select(User).filter_by(tg_id=tg_id))

        if not user:
            logging.warning("User not founded")
            return None

        old_name = user.name
        user.username = username
        user.name = name
        await session.commit()
        logging.info(f"User renamed {old_name} -> {name}")
        return user

    except SQLAlchemyError as e:
        logging.error(e)
        await session.rollback()


@connection
async def set_user(
    session: AsyncSession,
    tg_id: int,
    username: str,
    name: str = None,
) -> Optional[User]:
    try:
        user = await session.scalar(select(User).filter_by(tg_id=tg_id))

        if not user:
            new_user = User(
                tg_id=tg_id,
                username=username,
                name=name,
            )
            session.add(new_user)
            await session.commit()
            logging.info(f"User created {username}")
        else:
            return user

    except SQLAlchemyError as e:
        logging.error(e)
        await session.rollback()


@connection
async def get_user(session: AsyncSession, tg_id: int) -> User | None:
    try:
        user = await session.scalar(select(User).filter_by(tg_id=tg_id))
        return user

    except SQLAlchemyError as e:
        logging.error(e)
        await session.rollback()


@connection
async def get_all_users(session: AsyncSession) -> list[User]:
    try:
        users = await session.scalars(select(User))
        return users

    except SQLAlchemyError as e:
        logging.error(e)
        await session.rollback()
