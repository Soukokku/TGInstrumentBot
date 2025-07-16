""" from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard_prorab = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Заявки"), KeyboardButton(text="📦 Инвентаризация")],
        [KeyboardButton(text="🔧 Инструменты")]
    ],
    resize_keyboard=True
)

main_keyboard_worker = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔧 Мои инструменты")]
    ],
    resize_keyboard=True
)
 """