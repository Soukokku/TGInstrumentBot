from aiogram import types, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.state import StateFilter

from DB import DB
import crud

from keyboards.inline import (
    main_keyboard_prorab,
    main_keyboard_worker,
    get_objects_keyboard,
    approval_keyboard
)

class RegisterStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_object = State()

async def start_handler(message: types.Message, state: FSMContext):
    async with DB.db() as db:
        user = await crud.get_user_by_chat_id(db, message.chat.id)

    if user:
        role = user.role.name
        if role == "прораб":
            await message.answer("Вы прораб! Показываю кнопки прораба.", reply_markup=main_keyboard_prorab)
        elif role == "работник":
            await message.answer("Вы работник! Показываю кнопки работника.", reply_markup=main_keyboard_worker)
        elif role == "в ожидании":
            await message.answer("Ваша заявка еще рассматривается, пожалуйста, ожидайте.")
        else:
            await message.answer("Ваша роль не определена.")
    else:
        await message.answer("Добро пожаловать! Пожалуйста, введите ваше полное имя:")
        await state.set_state(RegisterStates.waiting_for_name)

async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    async with DB.db() as db:
        objects_list = await crud.get_objects_list(db)
    keyboard = get_objects_keyboard(objects_list)
    await message.answer("Пожалуйста, выберите объект:", reply_markup=keyboard)
    await state.set_state(RegisterStates.waiting_for_object)

async def process_object_callback(callback: types.CallbackQuery, state: FSMContext):
    object_name = callback.data.split("select_object:")[1]

    data = await state.get_data()
    full_name = data.get("full_name")
    tg_username = callback.from_user.username or ""
    chat_id = callback.from_user.id

    async with DB.db() as db:
        await crud.create_user_pending(db, chat_id, tg_username, full_name, object_name)

    await callback.message.answer("Спасибо! Ваша заявка отправлена на рассмотрение прорабу.")
    await state.clear()
    await callback.answer()

async def show_pending_users(callback: types.CallbackQuery):
    print(f"show_pending_users called by {callback.from_user.id}")
    async with DB.db() as db:
        users = await crud.get_pending_users(db)

    if not users:
        await callback.message.answer("Нет заявок на рассмотрение.")
    else:
        for user in users:
            text = f"👤 <b>{user.full_name}</b>\n🏗️ Объект: {user.object.name}"
            await callback.message.answer(text, reply_markup=approval_keyboard(user.id), parse_mode="HTML")
    await callback.answer()

async def approve_user_callback(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    async with DB.db() as db:
        user = await crud.approve_user(db, user_id)
    await callback.message.edit_text(f"✅ Заявка от <b>{user.full_name}</b> одобрена.", parse_mode="HTML")
    await callback.answer()

async def reject_user_callback(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    async with DB.db() as db:
        await crud.reject_user(db, user_id)
    await callback.message.edit_text("❌ Заявка отклонена.")
    await callback.answer()

def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command("start"))
    dp.message.register(process_name, StateFilter(RegisterStates.waiting_for_name))
    dp.callback_query.register(
        process_object_callback,
        lambda c: c.data and c.data.startswith("select_object:"),
        StateFilter(RegisterStates.waiting_for_object)
    )
    dp.callback_query.register(show_pending_users, lambda c: c.data == "zayavki")
    dp.callback_query.register(approve_user_callback, lambda c: c.data.startswith("approve_"))
    dp.callback_query.register(reject_user_callback, lambda c: c.data.startswith("reject_"))
