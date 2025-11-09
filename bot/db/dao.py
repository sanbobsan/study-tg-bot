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
    chat_id: int,
    username: str | None = None,
    name: str | None = None,
) -> User | None:
    """Создает, добавляет пользователя в бд, если такого нет.
    Возвращает пользователя, если найден или None, если создан

    Args:
        session (AsyncSession): Объект сессии
        tg_id (int): Id, привязанный к телеграмм аккаунту
        username (str | None, optional): Username аккаунта (@example). Defaults to None
        name (str | None, optional): Имя пользователя. Defaults to None

    Returns:
        User: Найденный пользователь
    """
    try:
        user = await get_user(tg_id=tg_id)
        if user is not None:
            logging.info(f"User already exists {tg_id} @{user.username} {user.name}")
            return user

        new_user = User(tg_id=tg_id, chat_id=chat_id)
        if username is not None:
            new_user.username = username
        if name is not None:
            new_user.name = name
        session.add(new_user)
        await session.commit()
        logging.info(f"User created {tg_id} @{username}")

    except Exception as e:
        logging.error(e)


@connection
async def get_all_users(session: AsyncSession) -> list[User]:
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
async def get_all_trusted_users(session: AsyncSession) -> list[User]:
    """Получает доверенных пользователей из бд

    Args:
        session (AsyncSession): Объект сессии

    Returns:
        Sequence[User]: Последовательность из доверенных пользователей
    """
    try:
        users = (await session.scalars(select(User).filter_by(trusted=True))).all()
        return users
    except Exception as e:
        logging.error(e)


def _apply_user_updates(
    user: User,
    username: str | None = None,
    name: str | None = None,
    has_desire: bool | None = None,
    trusted: bool | None = None,
) -> None:
    """Применяет обновления к объекту пользователя

    Args:
        user (User): Объект пользователя для обновления
        username (str | None, optional): Username аккаунта (@example). Defaults to None.
        name (str | None, optional): Имя, указанное пользователем в самом боте. Defaults to None.
        has_desire (bool | None, optional): Хочет ли пользователь участвовать в очереди. Defaults to None.
        trusted (bool | None, optional): Является ли пользователь доверенным. Defaults to None.
    """
    if username is not None:
        user.username = username

    if name is not None:
        old_name = user.name
        logging.info(
            f"User renamed id={user.id} tg_id={user.tg_id} @{user.username} {old_name} -> {name}"
        )
        user.name = name

    if has_desire is not None:
        user.has_desire = has_desire

    if trusted is not None:
        user.trusted = trusted
        logging.info(
            f"User trust has changed id={user.id} tg_id={user.tg_id} @{user.username}"
        )


@connection
async def update_user(
    session: AsyncSession,
    tg_id: int,
    username: str | None = None,
    name: str | None = None,
    has_desire: bool | None = None,
    trusted: bool | None = None,
) -> User | None:
    """Обновляет пользователя по tg_id, если найден
    - Все поля необязательны, кроме tg_id

    Args:
        session (AsyncSession): Объект сессии
        tg_id (int): Id, привязанный к телеграмм аккаунту
        username (str | None, optional): Username аккаунта (@example). Defaults to None.
        name (str | None, optional): Имя, указанное пользователем в самом боте. Defaults to None.
        has_desire (bool | None, optional): Хочет ли пользователь участвовать в очереди. Defaults to None.
        trusted (bool | None, optional): Является ли пользователь доверенным. Defaults to None.

    Returns:
        User | None: Обновленный пользователь или None, если не найден
    """
    try:
        user = await session.scalar(select(User).filter_by(tg_id=tg_id))

        if user is None:
            logging.error(f"User not found tg_id={tg_id} @{username}")
            return None

        _apply_user_updates(
            user, username=username, name=name, has_desire=has_desire, trusted=trusted
        )

        await session.commit()
        await session.refresh(user)
        return user

    except Exception as e:
        logging.error(e)
        return None


@connection
async def update_user_by_id(
    session: AsyncSession,
    user_id: int,
    username: str | None = None,
    name: str | None = None,
    has_desire: bool | None = None,
    trusted: bool | None = None,
) -> User | None:
    """Обновляет пользователя по внутреннему id, если найден
    - Все поля необязательны, кроме user_id
    - Предназначена для использования в админ-панели

    Args:
        session (AsyncSession): Объект сессии
        user_id (int): Внутренний id пользователя (row_id, primary key)
        username (str | None, optional): Username аккаунта (@example). Defaults to None.
        name (str | None, optional): Имя, указанное пользователем в самом боте. Defaults to None.
        has_desire (bool | None, optional): Хочет ли пользователь участвовать в очереди. Defaults to None.
        trusted (bool | None, optional): Является ли пользователь доверенным. Defaults to None.

    Returns:
        User | None: Обновленный пользователь или None, если не найден
    """
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))

        if user is None:
            logging.error(f"User not found id={user_id}")
            return None

        _apply_user_updates(
            user, username=username, name=name, has_desire=has_desire, trusted=trusted
        )

        await session.commit()
        await session.refresh(user)
        return user

    except Exception as e:
        logging.error(e)
        return None


# TODO: get_desire_status
# TODO: new DAO get_all_trusted_user_ids
