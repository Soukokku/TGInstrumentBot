from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from DB import DB
import crud

async def notify_foremen(bot: Bot):
    async with DB.db() as db:
        foremen = await crud.get_users_by_role(db, "прораб")
        for foreman in foremen:
            try:
                await bot.send_message(
                    foreman.chat_id,
                    "Необходимо провести инвентаризацию инструментов на вашем объекте."
                )
            except Exception as e:
                print(f"Не удалось отправить сообщение {foreman.full_name}: {e}")

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(notify_foremen, "cron", day=1, hour=9, minute=0, args=[bot])
    scheduler.start() 