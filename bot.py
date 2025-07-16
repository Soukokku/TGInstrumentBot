import asyncio
from aiogram import Bot, Dispatcher
from controllers import auth, tools, requests 
""" , tools, inventory, requests, qr, export """
 
API_TOKEN = '7895418717:AAEcd-sxOjEBkl7lNF7_qeEfApqEcB_rS4Q'

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    auth.register_handlers(dp)
    tools.register_handlers(dp)
    """ inventory.register_handlers(dp) """
    requests.register_handlers(dp) 
    """ qr.register_handlers(dp)
    export.register_handlers(dp) """

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
