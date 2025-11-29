from bot.create_bot import bot
from bot.db.dao import get_all_trusted_users, get_all_users
from bot.utils.queue import QueueManager


async def send(message_text: str, trusted_only: bool = True) -> None:
    """Отправляет сообщение всем пользователям
    Args:
        message_text (str): Сообщение, которое будет отправлено
        trusted_only (bool, optional): Если true, то сообщение отправится только доверенным пользователям, в ином случае всем
    """
    if trusted_only:
        users = await get_all_trusted_users()
    else:
        users = await get_all_users()
    for user in users:
        await bot.send_message(user.chat_id, text=message_text)


async def send_queue() -> None:
    """Отправляет доверенным пользователям актуальную очередь"""
    queue_manager = QueueManager()
    await send(await queue_manager.queue_show())
