from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def approval_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")
        ]
    ])


main_keyboard_prorab = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Заявки", callback_data="zayavki"),
            InlineKeyboardButton(text="Инвентаризация", callback_data="inventarizatsiya")
        ],
        [
            InlineKeyboardButton(text="Инструменты", callback_data="instrumenty")
        ],
        [
            InlineKeyboardButton(text="Оставить заявку на инструмент", callback_data="zayavka_instrument")
        ]
    ]
)

main_keyboard_worker = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Мои инструменты", callback_data="moi_instrumenty")
        ],
        [
            InlineKeyboardButton(text="Оставить заявку на инструмент", callback_data="zayavka_instrument")
        ]
    ]
)

def get_objects_keyboard(objects: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=obj, callback_data=f"select_object:{obj}")]
        for obj in objects
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_objects_with_tool_keyboard(objects: list[str], tool_name: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=obj, callback_data=f"choose_object:{tool_name}:{obj}")]
        for obj in objects
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)