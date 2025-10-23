from random import shuffle

from bot.data_base.models import User


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Queue(metaclass=Singleton):
    def __init__(self):
        self.queue: list[User] = []
        self.buffer: list[User] = []

    def add_user(self, user: User) -> None:
        id = user.id
        if id not in [user.id for user in self.queue] + [
            user.id for user in self.buffer
        ]:
            self.buffer.append(user)

    def del_user(self, user) -> None:
        id = user.id
        # for n, q_user in enumerate(self.queue):
        #     if q_user.id == id:
        #         del self.queue[n]
        for n, b_user in enumerate(self.buffer):
            if b_user.id == id:
                del self.buffer[n]

    def insert_buffer_in_queue(self):
        shuffle(self.buffer)
        self.queue += self.buffer
        self.buffer.clear()

    def clear(self):
        self.queue.clear()
        self.buffer.clear()

    def get_queue(self) -> list[User]:
        return self.queue

    def get_buffer(self) -> list[User]:
        return self.buffer
