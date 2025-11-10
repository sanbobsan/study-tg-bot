import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(url="sqlite+aiosqlite:///data/db.sqlite3")


async def upgrade():
    async with engine.connect() as conn:
        # Добавляем новый столбец chat_id, если его еще нет
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN chat_id BIGINT"))
            await conn.commit()
        except Exception:
            print("Столбец chat_id уже существует")
            await conn.rollback()

        # Все chat_id будут неправильными, чтобы обновить на текущие нужно уже существующим пользователям написать /start
        # Заполняем chat_id уникальными значениями (используем id)
        await conn.execute(text("UPDATE users SET chat_id = -id WHERE chat_id IS NULL"))
        await conn.commit()

        # Добавляем ограничение UNIQUE и NOT NULL после заполнения
        await conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_chat_id ON users (chat_id)"
            )
        )
        await conn.commit()


if __name__ == "__main__":
    asyncio.run(upgrade())
    print("Миграция успешно выполнена")
