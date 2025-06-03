from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Annotated
from datetime import datetime

intpk = Annotated[int, mapped_column(primary_key=True)]
str_255 = Annotated[int, mapped_column(String(255))]

class Base(DeclarativeBase):
    pass

class UsersOrm(Base):
    __tablename__='users'

    id_user: Mapped[intpk]
    username: Mapped[str_255 | None]
    tg_user_id: Mapped[str_255]
    tg_user_tag: Mapped[str_255]
    created_at: Mapped[datetime | None]

class FormsOrm(Base):
    __tablename__='form'

    id_form: Mapped[intpk]
    username_from: Mapped[str_255]
    age_form: Mapped[int]
    city_form: Mapped[str_255]
    gender_form: Mapped[bool]
    description: Mapped[str | None] = mapped_column(String(1024))
    form_media_path: Mapped[str | None] = mapped_column(String(1024))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id_user'))

class LikesOrm(Base):
    __tablename__ = 'liked'

    id_liked: Mapped[intpk]
    tg_user_id: Mapped[str_255]
    liked_form_id: Mapped[int] = mapped_column(ForeignKey('form.id_form'))
    message: Mapped[str_255 | None]