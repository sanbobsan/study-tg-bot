from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .base import connection
from .db import AsyncSession
from .models import User


@connection
async def update_user(
    session: AsyncSession,
    tg_id: int,
    username: str,
    name: int,
) -> User:
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))

        if not user:
            print("!!! Error !!! dao.update_user User not founded")
            return None

        old_name = user.name
        user.username = username
        user.name = name
        await session.commit()
        print(f"!!! Info !!! User renamed {old_name} -> {name}")
        return user

    except SQLAlchemyError as e:
        print(f"!!! Error !!! dao.update_user \n{e}\n")
        await session.rollback()


@connection
async def set_user(
    session: AsyncSession,
    tg_id: int,
    username: str,
    name: str = None,
) -> Optional[User]:
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))

        if not user:
            new_user = User(
                id=tg_id,
                username=username,
                name=name,
            )
            session.add(new_user)
            await session.commit()
            print(f"!!! Info !!! User created {username}")
        else:
            return user

    except SQLAlchemyError as e:
        print(f"!!! Error !!! dao.set_user \n{e}\n")
        await session.rollback()


@connection
async def get_user(session: AsyncSession, tg_id: int) -> User | None:
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))
        return user

    except SQLAlchemyError as e:
        print(f"!!! Error !!! dao.get_user \n{e}\n")
        await session.rollback()


@connection
async def get_all_users(session: AsyncSession) -> list[User]:
    try:
        users = await session.scalars(select(User))
        return users

    except SQLAlchemyError as e:
        print(f"!!! Error !!! dao.get_all_users \n{e}\n")
        await session.rollback()