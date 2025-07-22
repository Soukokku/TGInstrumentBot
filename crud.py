from DB.models import User, Role, Object, Tool, ToolStatus, RequestStatus, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

async def get_role_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()

async def get_user_by_chat_id(db: AsyncSession, chat_id: int):
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.chat_id == chat_id)
    )
    return result.scalar_one_or_none()

async def create_user_pending(db: AsyncSession, chat_id: int, tg_username: str, full_name: str, object_name: str):
    pending_role = await get_role_by_name(db, "в ожидании")
    if not pending_role:
        raise Exception("Роль 'в ожидании' не найдена в базе данных")
    result = await db.execute(select(Object).where(Object.name == object_name))
    obj = result.scalar_one_or_none()
    if not obj:
        obj = Object(name=object_name)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
    user = User(
        chat_id=chat_id,
        tg_username=tg_username,
        full_name=full_name,
        role_id=pending_role.id,
        object_id=obj.id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await db.refresh(user, attribute_names=["role"])
    return user

async def get_pending_users(db: AsyncSession):
    pending_role = await get_role_by_name(db, "в ожидании")
    if not pending_role:
        return []
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.role),   
            selectinload(User.object)  
        )
        .where(User.role_id == pending_role.id)
    )
    return result.scalars().all()

async def update_user_role(db: AsyncSession, user_id: int, new_role_name: str):
    role = await get_role_by_name(db, new_role_name)
    if not role:
        raise Exception(f"Роль '{new_role_name}' не найдена в базе данных")
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.role_id = role.id
        await db.commit()
        await db.refresh(user)
        await db.refresh(user, attribute_names=["role"])
    return user

async def get_objects_list(db: AsyncSession) -> list[str]:
    result = await db.execute(select(Object.name))
    return [row[0] for row in result.all()]

async def approve_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        worker_role = await get_role_by_name(db, "работник")
        if not worker_role:
            raise Exception("Роль 'работник' не найдена")
        user.role_id = worker_role.id
        await db.commit()
        await db.refresh(user)
    return user

async def reject_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        await db.delete(user)
        await db.commit()
    return user

async def get_tools_by_object(db: AsyncSession, object_id: int) -> list[Tool]:
    result = await db.execute(
        select(Tool).where(Tool.object_id == object_id)
    )
    return result.scalars().all()

async def get_objects_with_tool_available(db: AsyncSession, tool_name: str) -> list[Object]:
    result = await db.execute(
        select(Object)
        .join(Tool)
        .where(
            and_(
                Tool.name.ilike(f"%{tool_name}%"),
                Tool.status.has(name="в наличии")
            )
        )
        .distinct()
    )
    return result.scalars().all()

async def get_tool_by_name_and_object(db: AsyncSession, name: str, object_name: str):
    result = await db.execute(
        select(Tool)
        .join(Object)
        .where(
            Tool.name.ilike(f"%{name}%"),
            Object.name == object_name
        )
    )
    return result.scalar_one_or_none()

async def get_request_status_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(RequestStatus).where(RequestStatus.name == name))
    return result.scalar_one_or_none()

async def create_tool_request(db: AsyncSession, tool_id: int, from_object_id: int, to_object_id: int, from_user_id: int, to_user_id: int, status_id: int):
    request = Request(
        tool_id=tool_id,
        object_from_id=from_object_id,
        object_to_id=to_object_id,
        user_from_id=from_user_id,
        user_to_id=to_user_id,
        status_id=status_id
    )
    db.add(request)
    await db.commit()
    return request

async def get_pending_tool_requests(db: AsyncSession, status_name: str = "создана", object_id: int = None, object_field: str = "object_to_id"):
    status = await get_request_status_by_name(db, status_name)
    if not status:
        return []
    query = select(Request).options(
        selectinload(Request.tool),
        selectinload(Request.object_from),
        selectinload(Request.object_to),
        selectinload(Request.user_to),
        selectinload(Request.status)
    ).where(Request.status_id == status.id)
    if object_id is not None:
        if object_field == "object_to_id":
            query = query.where(Request.object_to_id == object_id)
        elif object_field == "object_from_id":
            query = query.where(Request.object_from_id == object_id)
    result = await db.execute(query)
    return result.scalars().all()

async def approve_tool_request(db: AsyncSession, request_id: int):
    result = await db.execute(select(Request).where(Request.id == request_id))
    request = result.scalar_one_or_none()
    if request:
        approved_status = await get_request_status_by_name(db, "одобрена")
        if not approved_status:
            raise Exception("Статус 'одобрена' не найден")
        request.status_id = approved_status.id
        await db.commit()
        await db.refresh(request)
    return request

async def reject_tool_request(db: AsyncSession, request_id: int):
    result = await db.execute(select(Request).where(Request.id == request_id))
    request = result.scalar_one_or_none()
    if request:
        rejected_status = await get_request_status_by_name(db, "отклонена")
        if not rejected_status:
            raise Exception("Статус 'отклонена' не найден")
        request.status_id = rejected_status.id
        await db.commit()
        await db.refresh(request)
    return request

async def get_tool_by_qr(db: AsyncSession, qr_code: str):
    result = await db.execute(select(Tool).where(Tool.qr_code == qr_code))
    return result.scalar_one_or_none()

async def set_tool_status(db: AsyncSession, tool_id: int, status_name: str):
    from DB.models import ToolStatus, Tool
    status = await db.execute(select(ToolStatus).where(ToolStatus.name == status_name))
    status = status.scalar_one_or_none()
    if not status:
        raise Exception(f"Статус '{status_name}' не найден")
    tool = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = tool.scalar_one_or_none()
    if not tool:
        raise Exception("Инструмент не найден")
    tool.status_id = status.id
    await db.commit()
    await db.refresh(tool)
    return tool

async def get_users_by_role(db: AsyncSession, role_name: str):
    from DB.models import User, Role
    result = await db.execute(
        select(User).join(Role).where(Role.name == role_name)
    )
    return result.scalars().all()

async def get_foreman_by_object(db, object_id):
    from DB.models import User, Role
    result = await db.execute(
        select(User).join(Role).where(Role.name == "прораб", User.object_id == object_id)
    )
    return result.scalar_one_or_none()

async def get_object_by_name(db, object_name: str):
    from DB.models import Object
    result = await db.execute(select(Object).where(Object.name == object_name))
    return result.scalar_one_or_none()