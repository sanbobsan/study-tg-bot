from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    """Модель пользователя"""

    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    """Id, привязанный к телеграмм аккаунту"""
    username: Mapped[str] = mapped_column(String, nullable=True)
    """Username аккаунта (@example)"""
    name: Mapped[str] = mapped_column(String, nullable=True)
    """Имя пользователя, указанное пользователем в самом боте, 
    или, если пользователь не указывал, то берет имя у аккаунта"""
    has_desire: Mapped[bool] = mapped_column(Boolean, default=False)
    """Хочет ли пользователь участвовать в очереди"""
    trusted: Mapped[bool] = mapped_column(Boolean, default=False)
    """Является ли пользователем доверенным"""
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    """Id, привязанный к чату с пользователем"""

    # TODO: DO last_queue_message_id, стоит ли?
    # для того, чтобы при каждом обновлении очереди
    # актуализировать последнее сообщение с ней у пользователя

    def __repr__(self) -> str:
        return f"<User(id={self.id}, tg_id={self.tg_id}, username='{self.username}', name='{self.name}', has_desire='{self.has_desire}', trusted='{self.trusted}')>"
