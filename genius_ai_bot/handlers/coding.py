from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database import db
from services.ai_service import ai_service
from keyboards.main_menu import get_cancel_keyboard, get_main_menu_keyboard
from states import CodingStates, KnowledgeStates
from utils import send_chunked_message

router = Router()

# --- 1. Dasturlash yordamchisi ---
@router.message(F.text == "💻 Kod yozishda yordam")
async def start_coding_help(message: Message, state: FSMContext) -> None:
    """Kod yozish va dasturlash bo'yicha yordam rejimini boshlash"""
    await state.clear()
    if message.from_user:
        await db.increment_command_count(message.from_user.id)

    await state.set_state(CodingStates.waiting_for_task)

    text = (
        "💻 *Dasturlash yordamchisi bo‘limi*\n\n"
        "Men quyidagi masalalarda yordam bera olaman:\n"
        "• Python, JavaScript, HTML/CSS, C++, SQL va boshqa tillarda kod yozish\n"
        "• Koddagi xatoliklarni (bug / error) topish va to‘g‘rilash\n"
        "• Murakkab algoritmlar va kutubxonalarni tushuntirish\n"
        "• Kodni optimallashtirish (refactoring)\n\n"
        "Iltimos, kodingizni yoki vazifangizni yuboring:"
    )

    await message.answer(
        text=text,
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(),
    )

@router.message(CodingStates.waiting_for_task, F.text)
async def process_coding_task(message: Message, state: FSMContext, bot: Bot) -> None:
    """Dasturlash so'rovini qabul qilish va AI orqali yechim qaytarish"""
    task_text = message.text.strip()
    user_id = message.from_user.id

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    loading_msg = await message.answer("⏳ _Kod tahlil qilinmoqda va yechim tayyorlanmoqda..._", parse_mode="Markdown")

    try:
        solution = await ai_service.coding_assistance(task_text)

        if not solution.startswith("⚠️"):
            await db.increment_ai_request_count(user_id)

        await loading_msg.delete()
        await send_chunked_message(message, solution)

        await message.answer(
            "Yana dasturlash bo‘yicha savolingiz bormi? Yozib yuboring yoki asosiy menyuga qayting:",
            reply_markup=get_cancel_keyboard(),
        )

    except Exception as e:
        await loading_msg.delete()
        await message.answer(f"⚠️ Kodni tahlil qilishda xatolik: {str(e)[:150]}")


# --- 2. Bilimlar va savol-javob ---
@router.message(F.text == "📚 Bilimlar va savol-javob")
async def start_knowledge_qa(message: Message, state: FSMContext) -> None:
    """Umumiy bilimlar va savol-javob bo'limi"""
    await state.clear()
    if message.from_user:
        await db.increment_command_count(message.from_user.id)

    await state.set_state(KnowledgeStates.waiting_for_question)

    text = (
        "📚 *Bilimlar va savol-javob bo‘limi*\n\n"
        "Fan, texnologiya, tarix, adabiyot, matematika va dunyo yangiliklari haqida istalgan savolingizni berishingiz mumkin.\n\n"
        "Savolingizni yozib yuboring:"
    )

    await message.answer(
        text=text,
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(),
    )

@router.message(KnowledgeStates.waiting_for_question, F.text)
async def process_knowledge_question(message: Message, state: FSMContext, bot: Bot) -> None:
    """Savolga ilmiy javob tayyorlash"""
    question = message.text.strip()
    user_id = message.from_user.id

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    loading_msg = await message.answer("⏳ _Savolingiz o‘rganilmoqda..._", parse_mode="Markdown")

    try:
        answer = await ai_service.qa_knowledge(question)

        if not answer.startswith("⚠️"):
            await db.increment_ai_request_count(user_id)

        await loading_msg.delete()
        await send_chunked_message(message, answer)

        await message.answer(
            "Yana biror narsa haqida bilmoqchimisiz? Savolingizni yozing yoki menyuga qayting:",
            reply_markup=get_cancel_keyboard(),
        )

    except Exception as e:
        await loading_msg.delete()
        await message.answer(f"⚠️ Javob olishda xatolik yuz berdi: {str(e)[:150]}")
