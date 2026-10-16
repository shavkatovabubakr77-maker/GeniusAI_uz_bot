import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

import config
from database import db
from handlers import start, chat, writing, translate, coding, profile, admin

# Loglarni sozlash (xavfsiz, tokenni ko'rsatmaydi)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("GeniusAIBot")

async def set_bot_commands(bot: Bot) -> None:
    """Telegram menyusidagi buyruqlar ro'yxatini sozlash"""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="menu", description="Asosiy menyu"),
        BotCommand(command="help", description="Yordam va qo'llanma"),
        BotCommand(command="admin", description="Admin paneli (faqat adminlar uchun)"),
    ]
    await bot.set_my_commands(commands)

async def main() -> None:
    """Botning asosiy ishga tushirish funksiyasi"""
    logger.info("Genius AI Telegram Boti ishga tushirilmoqda...")

    if not config.BOT_TOKEN:
        logger.error(
            "XATOLIK: BOT_TOKEN topilmadi! Iltimos, .env faylida BOT_TOKEN ni belgilang."
        )
        sys.exit(1)

    # Ma'lumotlar bazasini initsializatsiya qilish
    try:
        await db.init_db()
        logger.info("SQLite ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")
    except Exception as e:
        logger.error(f"Ma'lumotlar bazasini ochishda xatolik: {e}")
        sys.exit(1)

    # Bot va Dispatcherni yaratish
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni tartib bilan ulash
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(chat.router)
    dp.include_router(writing.router)
    dp.include_router(translate.router)
    dp.include_router(coding.router)
    dp.include_router(profile.router)

    # Bot menyusidagi komandalar
    await set_bot_commands(bot)

    # Adminlarga xabar berish (ixtiyoriy)
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="🚀 *Genius AI Boti muvaffaqiyatli ishga tushdi va faol holatda!*",
                parse_mode="Markdown",
            )
        except Exception:
            pass

    # Eskirgan so'rovlarni (pending updates) o'tkazib yuborish
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot polling rejimida ish boshladi.")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot o'chirildi.")
