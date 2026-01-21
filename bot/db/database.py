from functools import wraps
from typing import Awaitable, Callable, Concatenate, ParamSpec, TypeVar

from sqlalchemy import Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine: AsyncEngine = create_async_engine(url="sqlite+aiosqlite:///data/db.sqlite3")
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, class_=AsyncSession
)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


P = ParamSpec("P")
R = TypeVar("R")


def connection(
    func: Callable[Concatenate["AsyncSession", P], Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> R:
        async with async_session() as session:
            try:
                return await func(session, *args, **kwargs)

            except SQLAlchemyError as e:
                await session.rollback()
                raise e

            except Exception as e:
                await session.rollback()
                raise e

            finally:
                await session.close()

    return wrapper


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
