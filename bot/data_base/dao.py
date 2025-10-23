from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .base import connection
from .db import AsyncSession
from .models import User


@connection
async def set_user(
    session: AsyncSession, tg_id: int, username: str, name: str
) -> Optional[User]:
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))

        if not user:
            new_user = User(id=tg_id, username=username, name=name)
            session.add(new_user)
            await session.commit()
            print("!!! Info !!! User created")
        else:
            print("!!! Info !!! User already exists")
            return user

    except SQLAlchemyError as e:
        print(f"!!! Error !!! set_user \n{e}\n")


@connection
async def get_user(session: AsyncSession, tg_id: int) -> User:
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))
        return user
    except SQLAlchemyError as e:
        print(f"!!! Error !!! get_user \n{e}\n")
