from random import shuffle

from bot.data_base.models import User


# TODO: Redis?
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# TODO: хранение лишь id пользователей в очереди?
# - чтобы при изменении имени информация обновлялась при следующем же вызове
# - меньше хранить в переменной, но чаще вызывать бд?
# - оно тогда станет async, стоит ли?
class Queue(metaclass=Singleton):
    """Класс, который хранит очередь и буффер пользователей
    - Буффер - это те кто хотят попасть в очередь
    - Пользователи из буффера попадают в очередь, перемешиваясь
    """

    __queue: list[User] = []
    """Состоит из пользователей, порядок имеет значение
    """
    __buffer: list[User] = []
    """Состоит из пользователей, порядок не имеет значения, потому что
    перемешивается перед попаданием в очередь
    """

    def add_user_to_buffer(self, user: User):
        """Добавляет пользователя в буффер

        Args:
            user (User): Модель пользователя
        """
        if user.id not in [user_from_queue.id for user_from_queue in self.__queue] + [
            user_from_buffer.id for user_from_buffer in self.__buffer
        ]:
            self.__buffer.append(user)

    def del_user_from_buffer(self, user: User):
        """Удаляет пользователя из буффера

        Args:
            user (User): модель пользователя
        """
        for index, user_from_buffer in enumerate(self.__buffer):
            if user_from_buffer.id == user.id:
                del self.__buffer[index]

    def insert_buffer_into_queue(self):
        """Добавляет буффер к очереди, перемешивая его"""
        shuffle(self.__buffer)
        self.__queue += self.__buffer
        self.__buffer.clear()

    def clear(self):
        """Очищает очередь и буффер"""
        self.__queue.clear()
        self.__buffer.clear()

    def get_queue(self) -> list[User]:
        """Возвращает очередь

        Returns:
            list[User]: список пользователей
        """
        return self.__queue

    def get_buffer(self) -> list[User]:
        """Возвращает буффер

        Returns:
            list[User]: список пользователей
        """
        return self.__buffer

    def get_queue_str(self) -> str:
        """Генерирует текст со списком пользователей в очереди

        Returns:
            str: список пользователей в очереди, разделенные новыми строками
        """
        result = ""
        for index, user in enumerate(self.__queue):
            line = f"{index + 1}. {user.name}"
            if user.username is not None:
                line += f" @{user.username}"
            result += line + "\n"
        return result

    def get_buffer_str(self) -> str:
        """Генерирует текст со списком пользователей в буффере

        Returns:
            str: список пользователей в буффере, разделенные новыми строками
        """
        result = ""
        for user in self.__buffer:
            line = f"- {user.name}"
            if user.username is not None:
                line += f" @{user.username}"
            result += line + "\n"
        return result

    def get_text_for_message(self) -> str:
        """Генерирует готовый текст для сообщения

        Returns:
            str: текст для сообщения
        """
        queue_str = self.get_queue_str()
        buffer_str = self.get_buffer_str()

        if len(self.__queue) == 0:
            queue_str = "Очередь пуста\n"
        if len(self.__buffer) == 0:
            buffer_str = "- Петр Несуществующий\n"

        text = f"""{queue_str}Буффер:\n{buffer_str}
Буффер перемешивается и попадает в конец очереди
/join - присоединиться к буфферу
/leave - выйти из буффера"""
        return text
