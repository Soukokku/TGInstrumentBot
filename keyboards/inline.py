from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_keyboard_prorab = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Заявки", callback_data="zayavki"),
            InlineKeyboardButton(text="Заявки на инструменты", callback_data="zayavki_instrument"),
            InlineKeyboardButton(text="Инвентаризация", callback_data="inventarizatsiya")
        ],
        [
            InlineKeyboardButton(text="Сформировать отчет", callback_data="generate_xml_report")
        ]
    ]
)

main_keyboard_worker = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Инструменты на объекте", callback_data="moi_instrumenty")
        ],
        [
            InlineKeyboardButton(text="Оставить заявку на инструмент", callback_data="zayavka_instrument")
        ]
    ]
)

def get_back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
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

def approval_keyboard(user_id: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")
        ]
    ])
    return kb

def tool_request_approval_keyboard(request_id: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_tool_{request_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_tool_{request_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")
        ]
    ])
    return kb

def get_inventory_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Завершить инвентаризацию", callback_data="finish_inventory")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
        ]
    )