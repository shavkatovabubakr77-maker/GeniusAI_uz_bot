from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database import db
from services.ai_service import ai_service
from keyboards.main_menu import get_writing_menu_keyboard, get_cancel_keyboard, get_main_menu_keyboard
from states import WritingStates
from utils import send_chunked_message

router = Router()

WRITING_TYPES = {
    "📝 Insho va referat": ("essay", "Iltimos, insho yoki referat mavzusini yozing (masalan: *«Amir Temurning sarkardalik mahorati»*):"),
    "📄 Ariza va xat": ("letter", "Iltimos, ariza yoki xat kimga va qanday maqsadda yozilayotganini tushuntiring:"),
    "📢 Reklama matni": ("ad", "Iltimos, reklama qilinadigan mahsulot yoki xizmat haqida ma'lumot bering:"),
    "📱 Telegram post": ("post", "Iltimos, kanal uchun tayyorlanadigan post mavzusi yoki qisqa mazmunini yozing:"),
    "📖 Hikoya va tavsif": ("story", "Iltimos, hikoyaning bosh mavzusi, qahramonlari yoki g'oyasini yozing:"),
    "🔍 Imlo va tahrir": ("proofread", "Iltimos, xatolari tuzatilishi va tahrir qilinishi kerak bo'lgan matnni yuboring:"),
}

@router.message(F.text == "✍️ Matn yozish")
async def show_writing_menu(message: Message, state: FSMContext) -> None:
    """Matn yozish bo'limi menyusini ko'rsatish"""
    await state.clear()
    if message.from_user:
        await db.increment_command_count(message.from_user.id)

    text = (
        "✍️ *Matn yozish bo‘limiga xush kelibsiz!*\n\n"
        "Genius AI sizga professional darajadagi turli xil matnlarni yaratishda ko‘maklashadi.\n"
        "Quyidagi yo‘nalishlardan birini tanlang:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_writing_menu_keyboard())

@router.message(F.text.in_(WRITING_TYPES.keys()))
async def choose_writing_type(message: Message, state: FSMContext) -> None:
    """Matn turini tanlash va mavzu so'rash"""
    type_info = WRITING_TYPES[message.text]
    text_type, prompt_text = type_info

    await state.set_state(WritingStates.waiting_for_topic)
    await state.update_data(text_type=text_type, type_title=message.text)

    await message.answer(
        f"{message.text}\n\n{prompt_text}",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(),
    )

@router.message(WritingStates.waiting_for_topic, F.text)
async def process_writing_topic(message: Message, state: FSMContext, bot: Bot) -> None:
    """Mavzu bo'yicha matn yaratish"""
    user_topic = message.text.strip()
    data = await state.get_data()
    text_type = data.get("text_type", "essay")
    type_title = data.get("type_title", "Matn")

    user_id = message.from_user.id

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    wait_msg = await message.answer(f"⏳ _{type_title} tayyorlanmoqda... Bir necha soniya kuting._", parse_mode="Markdown")

    try:
        result = await ai_service.generate_text(text_type=text_type, user_prompt=user_topic)

        if not result.startswith("⚠️"):
            await db.increment_ai_request_count(user_id)

        await wait_msg.delete()
        await send_chunked_message(message, result)

        await message.answer(
            "Yana boshqa matn yozishni xohlaysizmi?",
            reply_markup=get_writing_menu_keyboard(),
        )
        await state.clear()

    except Exception as e:
        await wait_msg.delete()
        await message.answer(f"⚠️ Xatolik yuz berdi: {str(e)[:150]}")
        await state.clear()
