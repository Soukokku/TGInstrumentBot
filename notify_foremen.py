from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from DB import DB
import crud
<<<<<<< HEAD
# Fixed notification settings - 9:00 AM on the 1st of each month
TIMEZONE = 'Europe/Moscow'
NOTIFICATION_HOUR = 9
NOTIFICATION_MINUTE = 0
NOTIFICATION_DAY = 1
=======
>>>>>>> 2b43ccfb846ddfd640f886d374a935c1c06660cf

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
<<<<<<< HEAD
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.add_job(notify_foremen, "cron", day=NOTIFICATION_DAY, hour=NOTIFICATION_HOUR, minute=NOTIFICATION_MINUTE, args=[bot])
=======
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(notify_foremen, "cron", day=1, hour=9, minute=0, args=[bot])
>>>>>>> 2b43ccfb846ddfd640f886d374a935c1c06660cf
    scheduler.start() 