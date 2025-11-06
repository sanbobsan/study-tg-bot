import logging

from sqlalchemy import select

from .database import AsyncSession, connection
from .models import User


@connection
async def get_user(session: AsyncSession, tg_id: int) -> User | None:
    """Получает пользователя из бд

    Args:
        session (AsyncSession): Объект сессии
        tg_id (int): Id, привязанный к телеграмм аккаунту

    Returns:
        User: Пользователь
    """
    try:
        user = await session.scalar(select(User).filter_by(tg_id=tg_id))
        return user
    except Exception as e:
        logging.error(e)


@connection
async def create_user(
    session: AsyncSession,
    tg_id: int,
    username: str | None = None,
) -> User | None:
    """Создает, добавляет пользователя в бд, если такого нет.
    Возвращает пользователя, если найден или None, если создан

    Args:
        session (AsyncSession): Объект сессии
        tg_id (int): Id, привязанный к телеграмм аккаунту
        username (str | None, optional): Username аккаунта (@example). Defaults to None

    Returns:
        User: Найденный пользователь
    """
    try:
        user = await get_user(tg_id=tg_id)
        if user is not None:
            logging.info(f"User already exists {tg_id} @{user.username} {user.name}")
            return user

        new_user = User(tg_id=tg_id, username=username)
        if username is not None:
            new_user.username = username
        session.add(new_user)
        await session.commit()
        logging.info(f"User created {tg_id} @{username}")

    except Exception as e:
        logging.error(e)


@connection
async def get_all_users(session: AsyncSession):
    """Получает всех пользователей из бд

    Args:
        session (AsyncSession): Объект сессии

    Returns:
        Sequence[User]: Последовательность из всех пользователей
    """
    try:
        users = (await session.scalars(select(User))).all()
        return users
    except Exception as e:
        logging.error(e)


@connection
async def update_user(
    session: AsyncSession,
    tg_id: int,
    username: str = None,
    name: int = None,
    has_desire: bool = None,
    trusted: bool = None,
) -> User | None:
    """Обновляет пользователя, если найден
    - Все поля необязательны, кроме tg_id

    Args:
        session (AsyncSession): Объект сессии
        tg_id (int): Id, привязанный к телеграмм аккаунту
        username (str, optional): Username аккаунта (@example). Defaults to None.
        name (int, optional): Имя, указанное пользователем в самом боте. Defaults to None.
        has_desire (bool, optional): Хочет ли пользователь участвовать в очереди. Defaults to None.
        trusted (bool, optional):Является ли пользователем доверенным. Defaults to None.

    Returns:
        User: Обновленный пользователь
    """
    try:
        user = await session.scalar(select(User).filter_by(tg_id=tg_id))

        if user is None:
            logging.error(f"User not founded {tg_id} @{username}")
            return None

        if username is not None:
            user.username = username

        if name is not None:
            old_name = user.name
            logging.info(f"User renamed {tg_id} @{user.username} {old_name} -> {name}")
            user.name = name

        if has_desire is not None:
            user.has_desire = has_desire

        if trusted is not None:
            user.trusted = trusted
            logging.info(f"User trust has changed {tg_id} @{user.username}")

        await session.commit()
        return user

    except Exception as e:
        logging.error(e)


# TODO: get_desire_status
# TODO: update user by row_id for admin panel
