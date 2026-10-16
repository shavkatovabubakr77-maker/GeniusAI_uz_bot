from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database import db
from keyboards.main_menu import get_main_menu_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """/start buyrug'i uchun handler"""
    await state.clear()

    user = message.from_user
    if user:
        await db.get_or_create_user(
            user_id=user.id,
            full_name=user.full_name,
            username=user.username,
        )
        await db.increment_command_count(user.id)

    welcome_text = (
        "Assalomu alaykum! 👋 Genius AI botiga xush kelibsiz!\n\n"
        "Men sizga savollarga javob berish, matn yozish, tarjima va dasturlashda "
        "yordam beraman. Quyidagi bo‘limlardan birini tanlang."
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu_keyboard(),
    )

@router.message(F.text == "🔙 Asosiy menyu")
@router.message(Command("menu"))
async def back_to_main_menu(message: Message, state: FSMContext) -> None:
    """Asosiy menyuga qaytish"""
    await state.clear()
    if message.from_user:
        await db.increment_command_count(message.from_user.id)

    await message.answer(
        "Siz asosiy menyudasiz. Kerakli bo‘limni tanlang:",
        reply_markup=get_main_menu_keyboard(),
    )

@router.message(F.text == "ℹ️ Yordam")
@router.message(Command("help"))
async def show_help(message: Message) -> None:
    """Botdan foydalanish bo'yicha yo'riqnoma"""
    if message.from_user:
        await db.increment_command_count(message.from_user.id)

    help_text = (
        "💡 *Genius AI botidan foydalanish bo‘yicha qo‘llanma*\n\n"
        "Quyidagi imkoniyatlardan foydalanishingiz mumkin:\n\n"
        "🤖 *AI bilan suhbat* — sun'iy intellekt bilan xohlagan mavzuda erkin muloqot qiling. Suhbat davomida oldingi fikrlaringiz yodda saqlanadi.\n"
        "✍️ *Matn yozish* — insho, referat, rasmiy ariza, xat, reklama matnlari va Telegram postlarini bir necha soniyada yarating.\n"
        "🌐 *Tarjima qilish* — matnlarni dunyoning mashhur tillariga yuqori aniqlikda tarjima qiling.\n"
        "💻 *Kod yozishda yordam* — dasturlash (Python, JS, HTML/CSS va h.k.) bo'yicha savollaringizga javob oling, xatolarni tuzating.\n"
        "📚 *Bilimlar va savol-javob* — fan, tarix, texnologiya va umumiy bilimlarga oid har qanday savolingizga ilmiy javob oling.\n"
        "👤 *Mening profilim* — botdan foydalanish statistikangizni ko‘ring.\n\n"
        "📌 *Foydali buyruqlar:*\n"
        "/start — Botni qayta ishga tushirish\n"
        "/menu — Asosiy menyuga qaytish\n"
        "/help — Ushbu yordam xabarini ochish"
    )

    await message.answer(
        text=help_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard(),
    )
