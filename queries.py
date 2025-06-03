from sqlalchemy import select, insert, update, delete
from config import session_factory
from models import UsersOrm, FormsOrm, LikesOrm

class DatingDB:

    @staticmethod
    async def get_forms():
        async with session_factory() as session:
            query = select(FormsOrm)

            result = await session.execute(query)
            forms = result.scalars().all()

            if len(forms) > 0:
                return forms
            
            return None
        
    @staticmethod
    async def get_form_by_id(id):
        async with session_factory() as session:
            form = await session.get(FormsOrm, id)

            return form
        
    @staticmethod
    async def get_form_by_id_user(id):
        async with session_factory() as session:
            query = select(FormsOrm).where(FormsOrm.__table__.c.user_id==id)

            result = await session.execute(query)
            form = result.scalar_one_or_none()

            return form


    @staticmethod
    async def get_user_by_id(id):
        async with session_factory() as session:
            user = await session.get(UsersOrm, id)

            return user

    @staticmethod
    async def get_user_by_tg_user_id(tg_user_id):
        async with session_factory() as session:
            query = (
                select(UsersOrm)
                .where(UsersOrm.__table__.c.tg_user_id==tg_user_id)
            )

            result = await session.execute(query)
            user = result.scalar_one_or_none()

            return user
        
    @staticmethod
    async def add_user(username: str, tg_user_id: str, tg_user_tag:str):
        async with session_factory() as session:
            new_user = UsersOrm(username=username, tg_user_id=tg_user_id, tg_user_tag=tg_user_tag)

            session.add(new_user)
            await session.commit()

    @staticmethod
    async def add_form(username, age, city, gender, desctiption, form_media_path, user_id):
        async with session_factory() as session:
            new_form = FormsOrm(
                username_from=username,
                age_form=age,
                city_form=city,
                gender_form=gender,
                description=desctiption,
                form_media_path=form_media_path,
                user_id=user_id
            )    

            session.add(new_form)
            await session.commit()

    @staticmethod
    async def add_like(tg_user_id, form_id, message = None):
        async with session_factory() as session:
            new_like = LikesOrm(tg_user_id=tg_user_id, liked_form_id=form_id, message=message)

            session.add(new_like)

            await session.commit()

    @staticmethod
    async def get_form_who_liked_me(form_id):
        async with session_factory() as session:
            query = select(LikesOrm).where(LikesOrm.__table__.c.liked_form_id==form_id)

            result = await session.execute(query)
            likes = result.scalars().all()

            return likes
        
    @staticmethod
    async def delete_like_by_id(id):
        async with session_factory() as session:
            like = await session.get(LikesOrm, id)

            if like:
                await session.delete(like)
                await session.commit()
