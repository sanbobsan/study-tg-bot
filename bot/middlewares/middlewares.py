import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot.db.models import User


class IsTrustedMiddleware(BaseMiddleware):
    """Фильтр для проверки доверенного пользователя"""

    def __init__(self, get_user_func: Callable[[int], Awaitable[User | None]]):
        """
        Args:
            get_user_func: Асинхронная функция get_user(tg_id: int) -> User | None
        """
        self.get_user_func: Callable[[int], Awaitable[User | None]] = get_user_func

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any | None:
        if not isinstance(event, Message):
            logging.warning("IsTrustedMiddleware received non-Message event")
            return await handler(event, data)
        if not event.from_user:
            return None

        user: User | None = await self.get_user_func(event.from_user.id)
        if user.trusted if user else False:
            return await handler(event, data)
        else:
            await event.answer(
                "У вас нет доступа к этому боту. Обратитесь к администратору."
            )
            return None
