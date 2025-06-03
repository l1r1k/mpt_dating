from aiogram import Router,Bot

from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards import gender_kb, yes_or_no_kb, menu

from config import TG_API
from queries import DatingDB

import os

bot_handlers = Bot(TG_API)

router_create_form = Router()

class CreateForm(StatesGroup):
    username_form = State()
    age_form = State()
    city_form = State()
    gender_form = State()
    description_form = State()
    media_path_form = State()
    choose_action = State()

@router_create_form.message(Command('create'))
async def input_username_form_first(message: Message, state: FSMContext):
    await state.set_state(CreateForm.username_form)
    await message.answer('Введите имя, которое будет отображаться в вашей анкете')

@router_create_form.message(CreateForm.username_form)
async def input_username_form_second(message: Message, state: FSMContext):
    await state.update_data(username_form=message.text)
    await state.set_state(CreateForm.age_form)
    await message.answer('Введите свой возраст')

@router_create_form.message(CreateForm.age_form)
async def input_age_form_second(message: Message, state: FSMContext):
    await state.update_data(age_form=message.text)
    await state.set_state(CreateForm.city_form)
    await message.answer('Введите город')

@router_create_form.message(CreateForm.city_form)
async def input_city_form_second(message: Message, state: FSMContext):
    await state.update_data(city_form=message.text)
    await state.set_state(CreateForm.gender_form)
    await message.answer('Выберите свой пол (Мужской или Женский)', reply_markup=gender_kb)

@router_create_form.message(CreateForm.gender_form)
async def input_gender_form_second(message: Message, state: FSMContext):
    await state.update_data(gender_form=message.text)
    await state.set_state(CreateForm.description_form)
    await message.answer('Опишите себя (не более 1024 символов)')

@router_create_form.message(CreateForm.description_form)
async def input_description_form_second(message: Message, state: FSMContext):
    if len(message.text) <= 1024:
        await state.update_data(description_form=message.text)
        await state.set_state(CreateForm.media_path_form)
        await message.answer('Отправьте аватарку или кружок, который увидят другие пользователи')
    else:
        await message.answer(f'Превышен лимит по 1024 символов, было введено: {len(message.text)}')

async def download_file(file_id, user_id, type_file):
    file = await bot_handlers.get_file(file_id)
    file_path = file.file_path

    pc_path = f'media/{user_id}_pic.{type_file}'

    await bot_handlers.download_file(file_path, pc_path)
    return pc_path

@router_create_form.message(CreateForm.media_path_form)
async def input_media_path_form_second(message: Message, state: FSMContext):
    if message.photo:
        file_id = message.photo[-1].file_id
        pc_path = await download_file(file_id, message.from_user.id, 'jpg')        
    elif message.video_note:
        file_id = message.video_note.file_id
        pc_path = await download_file(file_id, message.from_user.id, 'mp4')
    else:
        await message.answer('Отправьте фото или кружок!')
        return ''

    await state.update_data(media_path_form=pc_path)
    data = await state.get_data()
    await message.answer('Создание акенты завершено! Пожалуйста проверьте, все ли верно заполнено!')

    file = FSInputFile(data['media_path_form'])

    caption = f"""
Имя: {data['username_form']}
Возраст: {data['age_form']}
Город: {data['city_form']}
Пол: {data['gender_form']}
Описание:
{data['description_form']}
"""

    if data['media_path_form'].endswith('.jpg'):
        await message.answer_photo(file, caption=caption)
    else:
        await message.answer_video(file, caption=caption)

    await message.answer('Выберите дальнейшее действие: Да, для просмотра анкет. Нет, для начала заполнения анкеты заново.', reply_markup=yes_or_no_kb)
    await state.set_state(CreateForm.choose_action)

@router_create_form.message(CreateForm.choose_action)
async def input_choose_action_second(message: Message, state: FSMContext):
    await state.update_data(choose_action=message.text)
    data = await state.get_data()
    if message.text.__contains__('Да'):
        await state.clear()
        user = await DatingDB.get_user_by_tg_user_id(str(message.from_user.id))
        gender = True if data['gender_form'].__contains__('Жен') else False

        await DatingDB.add_form(data['username_form'],
                                int(data['age_form']), 
                                data['city_form'], 
                                gender, 
                                desctiption=data['description_form'], 
                                form_media_path=data['media_path_form'],
                                user_id=user.id_user)
        
        await message.answer('Анкета успешно создана! ✅', reply_markup=menu)
    else:
        os.remove(data['media_path_form'])
        await state.clear()
        await state.set_state(CreateForm.username_form)
        await message.answer('Введите имя, которое будет отображаться в вашей анкете')
