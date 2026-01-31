import logging
from dataclasses import dataclass
from random import shuffle

from bot.db import User, get_all_trusted_users, get_user
from bot.utils.json_storage import load_queues, save_queues


class Queue:
    """Класс, который представляет одну очередь"""

    def __init__(self) -> None:
        """Инициализирует новый объект очереди"""
        self._queue: list[int] = []
        """Состоит из tg_id пользователей"""
        self._cached_text: str = ""
        """Кешированный подготовленный текст для сообщения (Имя очереди включено)"""

    def get_queue(self) -> list[int]:
        """Геттер для очереди
        Returns:
            list[int]: Очередь, состоит из tg_id пользователей
        """
        return self._queue.copy()

    async def set_queue(self, tg_ids: list[int], queue_name: str) -> None:
        """Сеттер для очереди
        Args:
            tg_ids (list[int]): Очередь, состоит из tg_id пользователей
        """
        self._queue = tg_ids
        await self.update_cached_text(queue_name=queue_name)

    async def init_from_db(self, queue_name: str) -> None:
        """Наполняет очередь пользователями из бд"""
        users = await get_all_trusted_users()
        self._queue = [user.tg_id for user in users]
        await self.update_cached_text(queue_name=queue_name)

    async def shuffle(self, queue_name: str) -> None:
        """Размешивает очередь в случайном порядке"""
        shuffle(self._queue)
        await self.update_cached_text(queue_name=queue_name)

    def move(self, steps: int = 1) -> None:
        """Циклический сдвиг очереди вперед или назад на заданное количество шагов"""
        if not self._queue:
            return
        steps = steps % len(self._queue)
        self._queue = self._queue[steps:] + self._queue[:steps]

    async def next_desiring(self, queue_name: str) -> None:
        """Переходит к следующему желающему пользователю (has_desire=True), пропуская тех кто не желает.
        Использует циклический сдвиг (первый в очереди становится последним)
        """
        if not self._queue:
            return
        for _ in range(len(self._queue)):
            self.move(steps=1)
            user: User | None = await get_user(self._queue[0])
            if user is not None and user.has_desire:
                await self.update_cached_text(queue_name=queue_name)
                return

    def get_text(self) -> str:
        """Возвращает подготовленный текст для сообщения из кеша"""
        return self._cached_text

    async def update_cached_text(self, queue_name: str) -> None:
        """Обновляет кешированный подготовленный текст для сообщения"""
        self._cached_text = await self._build_queue_text(queue_name)

    async def _build_queue_text(self, queue_name: str) -> str:
        """Возвращает список из пользователей в очереди
        Returns:
            str: Текст со списком вида
            1. Иван @username хочет
            2. Максим @username не хочет
        """
        users: list[User | None] = [await get_user(tg_id) for tg_id in self._queue]
        if not users:
            return f"✨ Очередь {queue_name} пуста ✨"
        result: str = f"✨ Очередь {queue_name} ✨\n"
        for index, user in enumerate(users):
            if user is None:
                logging.error("User in queue, but not in db")
                continue
            username: str = f"@{user.username}" if user.username is not None else ""
            status: str = "🟢" if user.has_desire else "🔴"
            result += f"{index + 1}. {user.name} {status} {username}\n"
        return result


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass
class GetQueueContext:
    queue: Queue | None
    """Объект очереди"""
    queue_name: str | None
    """Название очереди"""
    is_current: bool
    """Текущая ли очередь"""


class QueueManager(metaclass=Singleton):
    """Менеджер для управления очередями.
    Предназначен для готового использования.
    Внешние методы возвращают готовые строки для сообщений
    """

    _queues: dict[str, Queue] = {}
    _current_queue_name: str | None = None

    def _get_queue_context(self, queue_name: str | None = None) -> GetQueueContext:
        """Возвращает результат поиска, контекст.
        Когда имя не указано или передано имя текущей очереди: возвращает текущую очередь.
        """

        if not queue_name or queue_name == self._current_queue_name:
            return GetQueueContext(
                queue=self._queues.get(self._current_queue_name),  # type: ignore
                queue_name=self._current_queue_name,
                is_current=True,
            )

        return GetQueueContext(
            queue=self._queues.get(queue_name),
            queue_name=queue_name,
            is_current=False,
        )

    def _build_queue_report(
        self,
        queue: Queue | None,
        is_current: bool = False,
        add_at_start: str | None = None,
    ) -> str:
        """Составляет готовый текст для сообщения
        Args:
            queue (Queue | None): очередь
            is_current (bool, optional): текущая ли очередь?
            add_at_start (str | None, optional): добавляет строку в начале
        Returns:
            str: текст для сообщения
        """
        if queue:
            text = queue.get_text()
            if add_at_start:
                text = add_at_start + "\n" + text
            return text
        elif is_current:
            return "❌ Текущая очередь не установлена"
        else:
            return "❌ Очередь не найдена"

    # region Queues
    async def create_queue(self, queue_name: str | None) -> str:
        """Создает новую очередь из пользователей из бд и переключает текущую"""
        if queue_name is None:
            return "❌ Введи название очереди"
        if queue_name in self._queues:
            return "❌ Очередь с таким именем уже существует"

        queue = Queue()
        await queue.init_from_db(queue_name)
        self._queues[queue_name] = queue
        self._current_queue_name = queue_name

        return self._build_queue_report(
            queue=queue,
            is_current=True,
            add_at_start="⚙️ Очередь создана",
        )

    async def copy_queue(self, queue_name: str | None) -> str:
        """Создает копию текущей очереди и переключает текущую на нее"""
        if queue_name is None:
            return "❌ Введи название очереди"
        if queue_name in self._queues:
            return "❌ Очередь с таким именем уже существует"

        current_context = self._get_queue_context()
        if not current_context.queue:
            return "❌ Текущая очередь не установлена"

        queue = Queue()
        await queue.set_queue(current_context.queue.get_queue(), queue_name=queue_name)
        self._queues[queue_name] = queue
        self._current_queue_name = queue_name

        return self._build_queue_report(
            queue=queue,
            is_current=True,
            add_at_start=f"⚙️ Очередь {current_context.queue_name} скопирована",
        )

    def delete_queue(self, queue_name: str | None = None) -> str:
        """Удаляет очередь"""
        context = self._get_queue_context(queue_name=queue_name)
        if not context.queue or not context.queue_name:
            return "❌ Очередь не найдена"
        if context.is_current:
            self._current_queue_name = None
        del self._queues[context.queue_name]
        return f"⚙️ Очередь {context.queue_name} удалена"

    def get_queue_names(self) -> str:
        """Возвращает список названий всех очередей"""
        text = ", ".join(list(self._queues.keys()))
        if not text:
            return "⚙️ Ни одной очереди нет"
        return "⚙️ Существующие очереди:\n" + text

    def get_current_queue_name(self) -> str:
        """Геттер имени текущей очереди"""
        text = self._current_queue_name
        if not text:
            return "Текущая очередь не установлена"
        return f"Текущая очередь: ✨ {text} ✨"

    async def set_current_queue(self, queue_name: str | None) -> str:
        """Устанавливает очередь текущей по ее названию"""
        cxt = self._get_queue_context(queue_name=queue_name)
        if not cxt.queue or queue_name is None:
            return "❌ Такой очереди нет"
        if cxt.is_current:
            return "❌ Эта очередь уже является текущей"

        self._current_queue_name = queue_name
        await cxt.queue.update_cached_text(queue_name=queue_name)

        return self._build_queue_report(
            queue=cxt.queue,
            is_current=False,
            add_at_start=f'⚙️ Очередь "{queue_name}" теперь текущая',
        )

    # endregion

    # region Queue
    async def queue_show(self, queue_name: str | None = None) -> str:
        """Возвращает текстовое представление очереди"""
        cxt = self._get_queue_context(queue_name)
        return self._build_queue_report(queue=cxt.queue, is_current=cxt.is_current)

    async def queue_shuffle(self, queue_name: str | None = None) -> str:
        """Перемешивает очередь"""
        cxt = self._get_queue_context(queue_name)
        if cxt.queue and cxt.queue_name:
            await cxt.queue.shuffle(cxt.queue_name)
        return self._build_queue_report(
            queue=cxt.queue,
            is_current=cxt.is_current,
            add_at_start="⚙️ Очередь перемешана",
        )

    async def queue_next_desiring(self, queue_name: str | None = None) -> str:
        """Переходит к следующему желающему в очереди"""
        cxt = self._get_queue_context(queue_name)
        if cxt.queue and cxt.queue_name:
            await cxt.queue.next_desiring(cxt.queue_name)
        return self._build_queue_report(
            queue=cxt.queue,
            is_current=cxt.is_current,
            add_at_start="⚙️ Переход выполнен",
        )

    async def queue_init(self, queue_name: str | None = None) -> str:
        """Инициализирует очередь пользователями из бд"""
        cxt = self._get_queue_context(queue_name)
        if cxt.queue and cxt.queue_name:
            await cxt.queue.init_from_db(cxt.queue_name)
        return self._build_queue_report(
            queue=cxt.queue,
            is_current=cxt.is_current,
            add_at_start="⚙️ Очередь инициализирована",
        )

    async def queue_update_cached_text(self, queue_name: str | None = None) -> str:
        """Обновляет кешированный подготовленный текст для сообщения ТОЛЬКО у одной очереди"""
        cxt = self._get_queue_context(queue_name)
        if cxt.queue and cxt.queue_name:
            await cxt.queue.update_cached_text(cxt.queue_name)
        return self._build_queue_report(
            queue=cxt.queue,
            is_current=cxt.is_current,
            add_at_start="⚙️ Кешированный текст обновлен",
        )

    async def queue_move(self, queue_name: str | None = None, steps: int = 1) -> str:
        """Циклический сдвиг очереди вперед или назад на заданное количество шагов"""
        cxt: GetQueueContext = self._get_queue_context(queue_name)
        if cxt.queue and cxt.queue_name:
            cxt.queue.move(steps)
            await cxt.queue.update_cached_text(cxt.queue_name)
        return self._build_queue_report(
            queue=cxt.queue,
            is_current=cxt.is_current,
            add_at_start=f"⚙️ Очередь сдвинута вперед на {steps} шаг(ов)",
        )

    # endregion

    async def load_from_file(self) -> None:
        """Подгружает очереди из файла"""
        queues_dict: dict[str, list[int]] = await load_queues()
        for queue_name, tg_ids in queues_dict.items():
            queue = Queue()
            await queue.set_queue(tg_ids, queue_name=queue_name)
            self._queues[queue_name] = queue

    async def save_to_file(self) -> None:
        """Сохраняет очереди в файл"""
        data_for_save: dict[str, list[int]] = {}
        for queue_name, queue in self._queues.items():
            data_for_save[queue_name] = queue.get_queue()
        await save_queues(data=data_for_save)
