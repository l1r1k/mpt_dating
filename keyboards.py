from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

gender_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мужской ♂️'), KeyboardButton(text='Женский ♀️')],
], resize_keyboard=True, input_field_placeholder='Выберите пол'
, one_time_keyboard=True)

yes_or_no_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Да ✅')],
    [KeyboardButton(text='Нет ❌')],
], resize_keyboard=True, input_field_placeholder='Выберите действие',
one_time_keyboard=True)

menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Посмотреть анкеты 📗'), KeyboardButton(text='Посмотреть кому я понравился 🔎')],
], resize_keyboard=True, input_field_placeholder='Выберите действие',
one_time_keyboard=True)

actions = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Лайк 👍'), KeyboardButton(text='Отправить письмо 💌'), KeyboardButton(text='Не нравится 👎')],
    [KeyboardButton(text='Вернуться в меню')],
], resize_keyboard=True, input_field_placeholder='Выберите действие')

answer_on_action = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Взаимный лайк 👍'), KeyboardButton(text='Не 👎')],
    [KeyboardButton(text='Вернуться в меню')],
], resize_keyboard=True, input_field_placeholder='Выберите действие')

# only_back_to_meny = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Вернуться в меню')],
# ])