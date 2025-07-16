from aiogram import types
from DB import DB
import crud

waiting_for_tool_name = set()

async def zayavka_instrument_callback(callback: types.CallbackQuery):
    chat_id = callback.from_user.id
    waiting_for_tool_name.add(chat_id)
    await callback.message.answer("Введите название инструмента:")
    await callback.answer()

async def process_tool_name(message: types.Message):
    chat_id = message.from_user.id
    if chat_id not in waiting_for_tool_name:
        return  

    tool_name = message.text.strip()
    waiting_for_tool_name.remove(chat_id)

    async with DB.db() as db:
        objects = await crud.get_objects_with_tool_available(db, tool_name)

    if not objects:
        await message.answer("Инструмент не найден в наличии на объектах.")
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=obj.name, callback_data=f"select_object:{obj.name}")]
            for obj in objects
        ]
    )

    await message.answer(f"Объекты с инструментом '{tool_name}' в наличии:", reply_markup=keyboard)

async def select_object_callback(callback: types.CallbackQuery):
    object_name = callback.data.split(":", maxsplit=1)[1]
    await callback.message.answer(f"Вы выбрали объект: {object_name}")
    await callback.answer()

def register_handlers(dp):
    dp.callback_query.register(zayavka_instrument_callback, lambda c: c.data == "zayavka_instrument")
    dp.message.register(process_tool_name)
    dp.callback_query.register(select_object_callback, lambda c: c.data.startswith("select_object:"))
