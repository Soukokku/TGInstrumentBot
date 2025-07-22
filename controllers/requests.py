from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from DB import DB
import crud
from keyboards.inline import get_objects_with_tool_keyboard, tool_request_approval_keyboard, get_back_keyboard, main_keyboard_prorab, main_keyboard_worker
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from DB.models import Request

class RequestToolStates(StatesGroup):
    waiting_for_tool_name = State()
    waiting_for_target_object = State()

async def start_tool_request(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название инструмента:", reply_markup=get_back_keyboard())
    await state.set_state(RequestToolStates.waiting_for_tool_name)
    await callback.answer()

async def process_tool_name(message: types.Message, state: FSMContext):
    tool_name = message.text
    await state.update_data(tool_name=tool_name)
    async with DB.db() as db:
        objects = await crud.get_objects_with_tool_available(db, tool_name)
    if not objects:
        await message.answer("Инструмент не найден на других объектах.", reply_markup=get_back_keyboard())
        await state.clear()
        return
    keyboard = get_objects_with_tool_keyboard([obj.name for obj in objects], tool_name)
    await message.answer("Выберите объект, с которого хотите запросить инструмент:", reply_markup=keyboard)
    await state.set_state(RequestToolStates.waiting_for_target_object)

async def process_target_object(callback: types.CallbackQuery, state: FSMContext):
    _, tool_name, object_name = callback.data.split(":")
    data = await state.get_data()
    chat_id = callback.from_user.id
    async with DB.db() as db:
        user = await crud.get_user_by_chat_id(db, chat_id)
        tool = await crud.get_tool_by_name_and_object(db, tool_name, object_name)
        status = await crud.get_request_status_by_name(db, "создана")
        await crud.create_tool_request(
            db=db,
            tool_id=tool.id,
            from_object_id=tool.object_id,
            to_object_id=user.object_id,
            from_user_id=None,  
            to_user_id=user.id,
            status_id=status.id
        )
        foreman = await crud.get_foreman_by_object(db, tool.object_id)
        if foreman:
            await callback.bot.send_message(
                foreman.chat_id,
                f"Поступила новая заявка на инструмент!"
            )
    await callback.message.edit_text("Заявка на инструмент отправлена!")
    await state.clear()
    await callback.answer()

async def show_pending_tool_requests(callback: types.CallbackQuery):
    async with DB.db() as db:
        user = await crud.get_user_by_chat_id(db, callback.from_user.id)
        object_id = user.object_id if user else None
        requests = await crud.get_pending_tool_requests(db, status_name="создана", object_id=object_id, object_field="object_from_id")
    if not requests:
        await callback.message.answer("Нет заявок на инструменты для рассмотрения.", reply_markup=get_back_keyboard())
    else:
        for req in requests:
            text = (
                f"🔧 <b>{req.tool.name}</b>\n"
                f"С объекта: {req.object_from.name if req.object_from else '-'}\n"
                f"На объект: {req.object_to.name if req.object_to else '-'}\n"
                f"Запросил: {req.user_to.full_name if req.user_to else '-'}"
            )
            kb = tool_request_approval_keyboard(req.id)
            await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

async def approve_tool_request_callback(callback: types.CallbackQuery):
    request_id = int(callback.data.split("_")[2])
    async with DB.db() as db:
        await crud.approve_tool_request(db, request_id)
        result = await db.execute(
            select(Request).options(
                selectinload(Request.tool),
                selectinload(Request.user_to)
            ).where(Request.id == request_id)
        )
        req = result.scalar_one_or_none()
    await callback.message.edit_text(f"✅ Заявка на инструмент <b>{req.tool.name}</b> подтверждена.", parse_mode="HTML")
    try:
        from keyboards.inline import main_keyboard_worker
        await callback.bot.send_message(
            req.user_to.chat_id,
            f"Ваша заявка на инструмент '{req.tool.name}' одобрена!",
            reply_markup=main_keyboard_worker
        )
    except Exception as e:
        print(f"Не удалось отправить уведомление работнику: {e}")
    await callback.answer()

async def reject_tool_request_callback(callback: types.CallbackQuery):
    request_id = int(callback.data.split("_")[2])
    async with DB.db() as db:
        await crud.reject_tool_request(db, request_id)
        result = await db.execute(
            select(Request).options(
                selectinload(Request.tool),
                selectinload(Request.user_to)
            ).where(Request.id == request_id)
        )
        req = result.scalar_one_or_none()
    await callback.message.edit_text(f"❌ Заявка на инструмент <b>{req.tool.name}</b> отклонена.", parse_mode="HTML")
    try:
        from keyboards.inline import main_keyboard_worker
        await callback.bot.send_message(
            req.user_to.chat_id,
            f"Ваша заявка на инструмент '{req.tool.name}' отклонена.",
            reply_markup=main_keyboard_worker
        )
    except Exception as e:
        print(f"Не удалось отправить уведомление работнику: {e}")
    await callback.answer()

async def back_to_menu_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    async with DB.db() as db:
        user = await crud.get_user_by_chat_id(db, callback.from_user.id)
    if user and user.role.name == "прораб":
        await callback.message.answer("Главное меню:", reply_markup=main_keyboard_prorab)
    elif user and user.role.name == "работник":
        await callback.message.answer("Главное меню:", reply_markup=main_keyboard_worker)
    else:
        await callback.message.answer("Главное меню.")
    await callback.answer()

def register_handlers(dp: Dispatcher):
    dp.callback_query.register(start_tool_request, lambda c: c.data == "zayavka_instrument")
    dp.message.register(process_tool_name, StateFilter(RequestToolStates.waiting_for_tool_name))
    dp.callback_query.register(process_target_object, lambda c: c.data.startswith("choose_object:"), StateFilter(RequestToolStates.waiting_for_target_object))
    dp.callback_query.register(show_pending_tool_requests, lambda c: c.data == "zayavki_instrument")
    dp.callback_query.register(approve_tool_request_callback, lambda c: c.data.startswith("approve_tool_"))
    dp.callback_query.register(reject_tool_request_callback, lambda c: c.data.startswith("reject_tool_"))
    dp.callback_query.register(back_to_menu_callback, lambda c: c.data == "back_to_menu")
