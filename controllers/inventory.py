from aiogram import types, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from DB import DB
import crud
from keyboards.inline import get_back_keyboard, main_keyboard_prorab, main_keyboard_worker
from pyzbar.pyzbar import decode
from PIL import Image
import io
from aiogram.types import FSInputFile
import xml.etree.ElementTree as ET
from datetime import datetime
import tempfile
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from DB.models import User, Tool

class InventoryStates(StatesGroup):
    waiting_for_qr = State()

def get_inventory_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Завершить инвентаризацию", callback_data="finish_inventory")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
        ]
    )

async def start_inventory(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Отправьте фото с QR-кодом инструмента для инвентаризации.", reply_markup=get_inventory_keyboard())
    await state.set_state(InventoryStates.waiting_for_qr)
    await state.update_data(scanned_tools=[])
    await callback.answer()

async def process_qr_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото с QR-кодом.")
        return
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    file_bytes = await message.bot.download_file(file.file_path)
    image = Image.open(io.BytesIO(file_bytes.read()))
    decoded = decode(image)
    if not decoded:
        await message.answer("QR-код не распознан. Попробуйте ещё раз.")
        return
    qr_data = decoded[0].data.decode("utf-8")
    async with DB.db() as db:
        tool = await crud.get_tool_by_qr(db, qr_data)
        if not tool:
            await message.answer("Инструмент с таким QR-кодом не найден.")
            return
        user = await crud.get_user_by_chat_id(db, message.chat.id)
        if tool.object_id != user.object_id:
            await message.answer("Этот инструмент не относится к вашему объекту.")
            return
        data = await state.get_data()
        scanned = set(data.get("scanned_tools", []))
        scanned.add(tool.id)
        await state.update_data(scanned_tools=list(scanned))
        await message.answer(f"Инструмент {tool.name} (серийный: {tool.serial_number}) отмечен как проверенный.\nСканируйте следующий QR-код или завершите инвентаризацию.", reply_markup=get_inventory_keyboard())

async def finish_inventory_callback(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    scanned = set(data.get("scanned_tools", []))
    async with DB.db() as db:
        user = await crud.get_user_by_chat_id(db, callback.from_user.id)
        all_tools = await crud.get_tools_by_object(db, user.object_id)
        for tool in all_tools:
            if tool.id in scanned:
                await crud.set_tool_status(db, tool.id, "в наличии")
            else:
                await crud.set_tool_status(db, tool.id, "отсутствует")
    await state.clear()
    await callback.message.answer(
        "Инвентаризация завершена! Все данные обновлены.",
        reply_markup=main_keyboard_prorab
    )
    await callback.answer()

async def generate_inventory_xml(db, user):
    result = await db.execute(
        select(User).options(selectinload(User.object)).where(User.id == user.id)
    )
    user_with_object = result.scalar_one_or_none()
    object_ = user_with_object.object
    tools_result = await db.execute(
        select(Tool).options(selectinload(Tool.status)).where(Tool.object_id == user.object_id)
    )
    tools = tools_result.scalars().all()
    root = ET.Element("InventoryReport")
    ET.SubElement(root, "Date").text = datetime.now().strftime("%Y-%m-%d")
    ET.SubElement(root, "Object").text = object_.name
    ET.SubElement(root, "Foreman").text = user.full_name
    tools_el = ET.SubElement(root, "Tools")
    for tool in tools:
        tool_el = ET.SubElement(tools_el, "Tool")
        ET.SubElement(tool_el, "Name").text = tool.name
        ET.SubElement(tool_el, "SerialNumber").text = tool.serial_number or ""
        ET.SubElement(tool_el, "QRCode").text = tool.qr_code or ""
        ET.SubElement(tool_el, "Status").text = tool.status.name
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp:
        tree = ET.ElementTree(root)
        tree.write(tmp, encoding='utf-8', xml_declaration=True)
        return tmp.name

async def send_inventory_report(callback: types.CallbackQuery):
    async with DB.db() as db:
        user = await crud.get_user_by_chat_id(db, callback.from_user.id)
        xml_path = await generate_inventory_xml(db, user)
    xml_file = FSInputFile(xml_path)
    await callback.message.answer_document(xml_file, caption="XML-отчет по инвентаризации")
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
    dp.callback_query.register(start_inventory, lambda c: c.data == "inventarizatsiya")
    dp.message.register(process_qr_photo, StateFilter(InventoryStates.waiting_for_qr))
    dp.callback_query.register(finish_inventory_callback, lambda c: c.data == "finish_inventory")
    dp.callback_query.register(send_inventory_report, lambda c: c.data == "generate_xml_report")
    dp.callback_query.register(back_to_menu_callback, lambda c: c.data == "back_to_menu") 