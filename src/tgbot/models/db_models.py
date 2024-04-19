import datetime
import logging

from sqlalchemy import BigInteger, VARCHAR, ForeignKey, text, Date, Time, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.tgbot.database.connect import Base

logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )  # <- Идентификатор телеграм пользователя

    fullname: Mapped[str] = mapped_column(VARCHAR(129), nullable=True)
    username: Mapped[str] = mapped_column(VARCHAR(32), nullable=True)
    locale: Mapped[str] = mapped_column(VARCHAR(2), default="ru")

    @property
    def to_dict(self) -> dict:
        """
        Конвертирует модель в словарь
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Structure(Base):
    __tablename__ = "business_structure"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )
    type: Mapped[str] = mapped_column(VARCHAR(129), unique=True)


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )
    name: Mapped[str] = mapped_column(VARCHAR(129), nullable=True)
    inn: Mapped[int] = mapped_column(BigInteger, unique=True)
    phone: Mapped[str] = mapped_column(VARCHAR(20), nullable=True)
    mail: Mapped[str] = mapped_column(VARCHAR(129), nullable=True)
    manager: Mapped[int] = mapped_column(ForeignKey('user.id',
                                                    ondelete='SET NULL')
                                         )
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )
    structure: Mapped[int] = mapped_column(
        ForeignKey('business_structure.type', ondelete='SET NULL')
    )

    @property
    def to_dict(self) -> dict:
        """
        Конвертирует модель в словарь
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Factory(Base):
    __tablename__ = "factory"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )
    name: Mapped[int] = mapped_column(VARCHAR(129), unique=True)

    @property
    def to_dict(self) -> dict:
        """
        Конвертирует модель в словарь
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )
    name: Mapped[str] = mapped_column(VARCHAR(256), unique=True)

    @property
    def to_dict(self) -> dict:
        """
        Конвертирует модель в словарь
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ProductType(Base):
    __tablename__ = "product_type"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )
    product: Mapped[str] = mapped_column(
        ForeignKey('product.name', ondelete='NO ACTION')
    )
    product_type: Mapped[str] = mapped_column(VARCHAR(256), unique=True)
    price: Mapped[float] = mapped_column(Float)

    @property
    def to_dict(self) -> dict:
        """
        Конвертирует модель в словарь
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Shipment(Base):
    __tablename__ = "shipment"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True
    )
    date: Mapped[datetime.date] = mapped_column(Date)  # дата
    factory_name: Mapped[str] = mapped_column(
        ForeignKey('factory.name', ondelete='SET NULL')
    )  # завод
    delivery_address: Mapped[str] = mapped_column(VARCHAR(256),
                                                  nullable=True)  # адрес доставки
    time_on_site: Mapped[datetime.time] = mapped_column(Time,
                                                        nullable=True)  # время на объекте
    loading_time: Mapped[datetime.time] = mapped_column(Time,
                                                        nullable=True)  # время на погрузке
    product_name: Mapped[str] = mapped_column(
        ForeignKey('product.name', ondelete='NO ACTION')
    )
    call_product_type: Mapped[str] = mapped_column(
        ForeignKey('product_type.product_type', ondelete='NO ACTION')
    )
    real_product_type: Mapped[str] = mapped_column(
        ForeignKey('product_type.product_type', ondelete='NO ACTION')
    )
    price: Mapped[float] = mapped_column(Float, nullable=True)
    additional_equipment: Mapped[str] = mapped_column(VARCHAR(256),
                                                      nullable=True)
    payment: Mapped[str] = mapped_column(VARCHAR(3))
    comment: Mapped[str] = mapped_column(VARCHAR(256), nullable=True)
    supplier: Mapped[str] = mapped_column(VARCHAR(256),
                                          nullable=True)  # грузоотправитель
    consignee: Mapped[str] = mapped_column(
        ForeignKey('customer.id', ondelete='NO ACTION'))  # грузополучатель
    consignee_phone: Mapped[str] = mapped_column(VARCHAR(20), nullable=True)
    manager: Mapped[str] = mapped_column(
        ForeignKey('user.id', ondelete='NO ACTION'))

    @property
    def to_dict(self) -> dict:
        """
        Конвертирует модель в словарь
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
