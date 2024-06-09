import datetime
import logging

from sqlalchemy import (BigInteger, VARCHAR, ForeignKey, text, Date, Time,
                        Float, String)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.tgbot.database.connect import Base

logger = logging.getLogger(__name__)

class Users(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )  #  <- Идентификатор телеграм пользователя

    fullname: Mapped[str] = mapped_column(VARCHAR(129), nullable=True)
    username: Mapped[str] = mapped_column(VARCHAR(32), nullable=True)
    locale: Mapped[str] = mapped_column(VARCHAR(2), default="ru")
    role: Mapped["Roles"] = relationship("Roles", back_populates="user")

    @property
    def to_dict(self) -> dict:
        """
        Конвертирует модель в словарь
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Roles(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True,
                                    autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["Users"] = relationship("Users", back_populates="role")

    @property
    def to_dict(self) -> dict:
        """
        Конвертирует модель в словарь
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
