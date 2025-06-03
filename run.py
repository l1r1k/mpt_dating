import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from create_form_handlers import router_create_form

from config import TG_API, async_angine

from queries import DatingDB

from keyboards import menu, yes_or_no_kb, actions, answer_on_action

bot = Bot(TG_API)
dp = Dispatcher()

class FormInAction(StatesGroup):
    form = State()
    action = State()
    message = State()

class Likes(StatesGroup):
    forms = State()
    liked_form = State()
    liked_form_id = State()
    action = State()

@dp.message(CommandStart())
async def start(message: Message):
    tg_user_id = message.from_user.id
    tg_user_full_name = message.from_user.full_name
    tg_user_username = message.from_user.username

    user = await DatingDB.get_user_by_tg_user_id(str(tg_user_id))
    if user:
        form = await DatingDB.get_form_by_id_user(user.id_user)
        if form:
            await message.answer(f'С возвращением, {tg_user_full_name}!', reply_markup=menu)
        else:
            await message.answer(f'С возвращением, {tg_user_full_name}! У вас еще нет анкеты, чтобы посмотреть другие анкеты сначала создайте свою! Пропишите /create, чтобы создать анкету!')
    else:
        await message.answer(f'Привет, {tg_user_full_name}! Сейчас запишем тебя в свою систему и сможешь создать анкету!')
        await DatingDB.add_user(tg_user_full_name, str(tg_user_id), tg_user_username)
        await message.answer(f'Поздравляем! Ты был успешно добавлен в систему! Напиши /create, чтобы создать анкету!')

@dp.message(F.text == 'Вернуться в меню')
async def shop_menu(message: Message):
    await message.answer('Выберите действие', reply_markup=menu)

@dp.message(F.text.in_(['Посмотреть анкеты 📗','Не нравится 👎']))
async def show_forms(message: Message, state: FSMContext):
    await message.answer('Вот анкета:', reply_markup=actions)
    forms = await DatingDB.get_forms()

    random_form = random.choice(forms)

    await state.set_state(FormInAction.form)
    await state.update_data(form=random_form)

    file = FSInputFile(random_form.form_media_path)

    caption = f"""
Имя: {random_form.username_from}
Возраст: {random_form.age_form}
Город: {random_form.city_form}
Пол: {'Женский' if random_form.gender_form else 'Мужской'}
Описание:
{random_form.description}
"""    
    if random_form.form_media_path.endswith('.jpg'):
        await message.answer_photo(file, caption=caption,reply_markup=actions)
    else:
        await message.answer_video(file, caption=caption,reply_markup=actions)

@dp.message(F.text.in_(['Лайк 👍', 'Отправить письмо 💌']))
async def like(message: Message, state: FSMContext):
    await state.set_state(FormInAction.action)
    await state.update_data(action=message.text)
    current_data = await state.get_data()
    
    match (message.text):
        case 'Лайк 👍':
            await DatingDB.add_like(str(message.from_user.id), current_data['form'].id_form)
            
            form = await DatingDB.get_form_by_id(current_data['form'].id_form)
            user = await DatingDB.get_user_by_id(form.user_id)

            await bot.send_message(user.tg_user_id, 'Вы кому то понравились! Посмотрите скорей!')
            await state.clear()
            await message.answer('Выберите действие', reply_markup=menu)
        case 'Отправить письмо 💌':
            await state.set_state(FormInAction.message)
            await message.answer('Напишите сообщение: ')

@dp.message(FormInAction.message)
async def like_with_message(message: Message, state: FSMContext):
    current_data = await state.get_data()
    await state.update_data(message=message.text)
    
    await DatingDB.add_like(str(message.from_user.id), current_data['form'].id_form, message.text)

    user = await DatingDB.get_user_by_id(current_data['form'].user_id)

    await bot.send_message(user.tg_user_id, 'Вы кому то понравились! Посмотрите скорей!')

    await state.clear()
    await message.answer('Выберите действие', reply_markup=menu)

@dp.message(F.text.in_(['Посмотреть кому я понравился 🔎','Не 👎']))
async def show_liked(message: Message, state: FSMContext):
    await message.answer('Вот анкеты кому вы понравились: ')

    user = await DatingDB.get_user_by_tg_user_id(str(message.from_user.id))
    form = await DatingDB.get_form_by_id_user(user.id_user)
    likes = await DatingDB.get_form_who_liked_me(form.id_form)
    likes = list(likes)
    if len(likes) < 1:
        await message.answer('Вас пока еще никто не оценил, можете вернуться посмотреть анкеты', reply_markup=menu)
        return ''
    
    await state.set_state(Likes.liked_form_id)
    await state.update_data(liked_form_id=likes[0].id_liked)

    user_who_liked = await DatingDB.get_user_by_tg_user_id(str(likes[0].tg_user_id))
    form_who_liked = await DatingDB.get_form_by_id_user(user_who_liked.id_user)
    liked_form = await DatingDB.get_form_by_id(form_who_liked.id_form)

    await state.set_state(Likes.liked_form)
    await state.update_data(liked_form=liked_form)

    message_from_liked_person = likes[0].message

    if message.text == 'Не 👎':
        await DatingDB.delete_like_by_id(likes[0].id_liked)
    likes.remove(likes[0])

    await state.set_state(Likes.forms)
    await state.update_data(forms=likes)

    file = FSInputFile(liked_form.form_media_path)

    caption = f"""
Имя: {liked_form.username_from}
Возраст: {liked_form.age_form}
Город: {liked_form.city_form}
Пол: {'Женский' if liked_form.gender_form else 'Мужской'}
Описание:
{liked_form.description}
{f'Письмо: {message_from_liked_person}' if message_from_liked_person else ''}
"""
    
    if liked_form.form_media_path.endswith('.jpg'):
        await message.answer_photo(file, caption=caption,reply_markup=answer_on_action)
    else:
        await message.answer_video(file, caption=caption,reply_markup=answer_on_action)


@dp.message(F.text == 'Взаимный лайк 👍')
async def match(message: Message, state: FSMContext):
    data = await state.get_data()
            
    form = await DatingDB.get_form_by_id(data['liked_form'].id_form)
    user = await DatingDB.get_user_by_id(form.user_id)

    user_liked = await DatingDB.get_user_by_tg_user_id(str(message.from_user.id))

    await bot.send_message(user.tg_user_id, f'У вас мэтч! Вот юзернейм: @{user_liked.tg_user_tag}')
    await message.answer(f'У вас мэтч! Вот тг юзернейм @{user.tg_user_tag}', reply_markup=menu)

    await DatingDB.delete_like_by_id(data['liked_form_id'])

    await state.set_state(Likes.forms)
    # data['forms'].remove(data['liked_form'])
    await state.update_data(likes=data['forms'])
        

async def main():
    dp.include_router(router_create_form)
    await dp.start_polling(bot)

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())