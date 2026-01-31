from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdminFilter(BaseFilter):
    """Фильтр для проверки администратора"""

    def __init__(self, admin_ids: list[int]):
        self.admin_ids: list[int] = admin_ids

    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        return message.from_user.id in self.admin_ids
