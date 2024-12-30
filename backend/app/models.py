import uuid
from decimal import Decimal

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    orders: list["Order"] = Relationship(back_populates="user", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Shared properties
class BeverageBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    price: Decimal = Field(default=0, max_digits=5, decimal_places=3)
    inventory: int = Field(ge=0)


# Properties to receive on beverage creation
class BeverageCreate(BeverageBase):
    pass


# Properties to receive on beverage update
class BeverageUpdate(BeverageBase):
    name: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    price: Decimal = Field(default=0, max_digits=5, decimal_places=3)
    inventory: int | None = Field(default=None, ge=0)


# Database model, database table inferred from class name
class Beverage(BeverageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Properties to return via API, id is always required
class BeveragePublic(BeverageBase):
    id: uuid.UUID


class BeveragesPublic(SQLModel):
    data: list[BeveragePublic]
    count: int


# Shared properties
class OrderBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    total_price: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    status: str = Field(default="pending", max_length=50)


# Properties to receive on order creation
class OrderCreate(OrderBase):
    pass


# Properties to receive on order update
class OrderUpdate(OrderBase):
    status: str | None = Field(default=None, max_length=50)  # type: ignore


# Database model, database table inferred from class name
class Order(OrderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user: User | None = Relationship(back_populates="orders")
    order_details: list["OrderDetail"] = Relationship(
        back_populates="order", cascade_delete=True
    )


# Properties to return via API, id is always required
class OrderPublic(OrderBase):
    id: uuid.UUID


class OrdersPublic(SQLModel):
    data: list[OrderPublic]
    count: int


# Shared properties
class OrderDetailBase(SQLModel):
    order_id: uuid.UUID = Field(foreign_key="order.id", nullable=False)
    item_id: uuid.UUID = Field(foreign_key="item.id", nullable=False)
    quantity: int = Field(ge=1)
    price: Decimal = Field(default=0, max_digits=10, decimal_places=2)


# Properties to receive on order detail creation
class OrderDetailCreate(OrderDetailBase):
    pass


# Properties to receive on order detail update
class OrderDetailUpdate(OrderDetailBase):
    quantity: int | None = Field(default=None, ge=1)  # type: ignore
    price: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)


# Database model, database table inferred from class name
class OrderDetail(OrderDetailBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order: Order | None = Relationship(back_populates="order_details")


# Properties to return via API, id is always required
class OrderDetailPublic(OrderDetailBase):
    id: uuid.UUID


class OrderDetailsPublic(SQLModel):
    data: list[OrderDetailPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
