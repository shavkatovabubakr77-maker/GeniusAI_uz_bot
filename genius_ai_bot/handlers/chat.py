from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database import db
from services.ai_service import ai_service
from keyboards.main_menu import get_chat_mode_keyboard, get_main_menu_keyboard
from states import ChatStates
from utils import send_chunked_message

router = Router()

@router.message(F.text == "🤖 AI bilan suhbat")
async def start_chat_mode(message: Message, state: FSMContext) -> None:
    """AI bilan erkin suhbat rejimini faollashtirish"""
    if message.from_user:
        await db.increment_command_count(message.from_user.id)

    await state.set_state(ChatStates.chatting)

    intro_text = (
        "🤖 *AI bilan suhbat rejimi yoqildi!*\n\n"
        "Menga istalgan savolingizni yozishingiz mumkin. Men oldingi xabarlaringizni eslab qolaman.\n\n"
        "💡 *Maslahat:* Agar mavzuni butunlay o'zgartirmoqchi bo'lsangiz, "
        "«🧹 Suhbatni tozalash» tugmasini bosing."
    )

    await message.answer(
        text=intro_text,
        parse_mode="Markdown",
        reply_markup=get_chat_mode_keyboard(),
    )

@router.message(ChatStates.chatting, F.text == "🧹 Suhbatni tozalash")
async def clear_chat(message: Message) -> None:
    """Suhbat kontekstini tozalash"""
    if message.from_user:
        await db.clear_chat_history(message.from_user.id)
        await db.increment_command_count(message.from_user.id)

    await message.answer(
        "🧹 Suhbat xotirasi tozalandi! Endi yangi mavzuda savol berishingiz mumkin.",
        reply_markup=get_chat_mode_keyboard(),
    )

@router.message(ChatStates.chatting, F.text)
async def process_chat_message(message: Message, bot: Bot) -> None:
    """Suhbat xabarini qabul qilish va AI orqali javob berish"""
    user_text = message.text.strip()
    user_id = message.from_user.id

    # Agar maxsus buyruq bo'lsa
    if user_text.startswith("/"):
        return

    # Typing holatini ko'rsatish
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Kontekst tarixini olish
    history = await db.get_chat_history(user_id=user_id, limit=6)

    wait_msg = await message.answer("⏳ _Genius AI javob tayyorlamoqda..._", parse_mode="Markdown")

    try:
        reply_text = await ai_service.chat(user_message=user_text, history=history)

        # Tarixga qo'shish (faqat xatolik bo'lmasa)
        if not reply_text.startswith("⚠️"):
            await db.add_chat_message(user_id=user_id, role="user", content=user_text)
            await db.add_chat_message(user_id=user_id, role="assistant", content=reply_text)
            await db.increment_ai_request_count(user_id)

        await wait_msg.delete()
        await send_chunked_message(message, reply_text)

    except Exception as e:
        await wait_msg.delete()
        await message.answer(f"⚠️ Kutilmagan xatolik yuz berdi: {str(e)[:150]}")
