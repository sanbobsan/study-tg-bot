from random import shuffle

from bot.db.dao import get_all_users, get_user


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Queue(metaclass=Singleton):
    """Класс, который хранит и обрабатывает очередь"""

    _queue: list[int] = []
    """Состоит из tg_id пользователей
    """

    def get_queue(self) -> list[int]:
        """Возвращает очередь

        Returns:
            list[int]: Состоит из  tg_id пользователей
        """
        return self._queue

    def shuffle(self):
        """Размешивает очередь в случайном порядке"""
        shuffle(self._queue)

    def _next(self):
        """Отправляет пользователя из начала в конец очереди, то есть переходит к следующему"""
        self._queue = self._queue[1:] + [self._queue[0]]

    async def next(self):
        """Пролистывает список до следуюшего желающего пользователя, пропуская тех кто не желает"""
        # Бексонечный цикл, если никто не хочет
        if not self._queue:
            return
        self._next()
        print("goooooo")
        user = await get_user(self._queue[0])
        while not user.has_desire:
            self._next()
            user = await get_user(self._queue[0])
            print("goooooo")

    async def create_queue(self):
        """Создает очередь из пользователей из бд"""
        users = await get_all_users()
        self._queue = [user.tg_id for user in users]

    # TODO: (has_desire_only: bool = False)
    async def build_queue_text(self) -> str:
        """Возвращает список из пользователей в очереди

        Returns:
            str: Текст со списком вида
            1. Иван @username хочет
            2. Максим @username не хочет
        """
        users = [await get_user(tg_id) for tg_id in self._queue]

        if not users:
            return "✨ Очередь пуста ✨"

        result = "✨ Текущая очередь ✨\n"
        for index, user in enumerate(users):
            username = f"@{user.username}" if user.username is not None else ""
            status = "🟢 хочет" if user.has_desire else "🔴 не хочет"
            result += f"{index + 1}. {user.name} {status} {username}\n"

        return result
