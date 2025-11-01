from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


# TODO: доверенный пользователь? Хранение списка группы
class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    """Id привязанный к телеграмм аккаунту
    """
    username: Mapped[str] = mapped_column(String, nullable=True)
    """Username аккаунта (@example)
    """
    name: Mapped[str] = mapped_column(String, nullable=True)
    """Имя указанное пользователем в самом боте
    """

    # Под вопросом
    # acc_name: Mapped[str] = mapped_column(String, nullable=False)
    # """Имя полученное от имени аккаунта пользователя
    # """

    def __repr__(self):
        return f"<User(id={self.id}, tg_id={self.telegram_id}, username='{self.username}', name='{self.name}')>"
