from DB.models import User, Role, Object, Tool, ToolStatus, RequestStatus, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_

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

from sqlalchemy.orm import selectinload

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
                Tool.status == "в наличии"
            )
        )
        .distinct()
    )
    return result.scalars().all()