from .db import async_session, engine, Base


def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)

    return wrapper


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
