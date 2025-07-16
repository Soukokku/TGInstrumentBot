from aiogram import types
from DB import DB
import crud

async def my_tools_callback(callback: types.CallbackQuery):
    chat_id = callback.from_user.id
    async with DB.db() as db:
        user = await crud.get_user_by_chat_id(db, chat_id)
        if not user or not user.object_id:
            await callback.message.answer("Пользователь не найден или не привязан к объекту.")
            await callback.answer()
            return

        tools = await crud.get_tools_by_object(db, user.object_id)
        if not tools:
            await callback.message.answer("На вашем объекте пока нет инструментов.")
        else:
            text = "Инструменты на вашем объекте:\n" + "\n".join(
                f"• {tool.name} (Серийный номер: {tool.serial_number or 'нет'})"
                for tool in tools
            )
            await callback.message.answer(text)

    await callback.answer()

def register_handlers(dp):
    dp.callback_query.register(my_tools_callback, lambda c: c.data == "moi_instrumenty")
