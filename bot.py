import asyncio
from aiogram import Bot, Dispatcher
from controllers import auth, tools, requests, inventory
from notify_foremen import setup_scheduler
<<<<<<< HEAD
from config import BOT_TOKEN

async def main():
    bot = Bot(token=BOT_TOKEN)
=======

API_TOKEN = '8073480508:AAE3-B1_RGVhJnl48JJ5ebJYDLLGUIm8w2k'

async def main():
    bot = Bot(token=API_TOKEN)
>>>>>>> 2b43ccfb846ddfd640f886d374a935c1c06660cf
    dp = Dispatcher()
    auth.register_handlers(dp)
    tools.register_handlers(dp)
    inventory.register_handlers(dp)
    requests.register_handlers(dp)
    setup_scheduler(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
