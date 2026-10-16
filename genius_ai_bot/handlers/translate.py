from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import db
from services.ai_service import ai_service
from keyboards.main_menu import get_cancel_keyboard, get_translation_languages_keyboard, get_main_menu_keyboard
from states import TranslateStates
from utils import send_chunked_message

router = Router()

@router.message(F.text == "🌐 Tarjima qilish")
async def start_translation(message: Message, state: FSMContext) -> None:
    """Tarjima rejimini boshlash va matn so'rash"""
    await state.clear()
    if message.from_user:
        await db.increment_command_count(message.from_user.id)

    await state.set_state(TranslateStates.waiting_for_text)

    await message.answer(
        "🌐 *Tarjima xizmati*\n\n"
        "Tarjima qilinishi kerak bo'lgan matnni yuboring:",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(),
    )

@router.message(TranslateStates.waiting_for_text, F.text)
async def receive_translation_text(message: Message, state: FSMContext) -> None:
    """Tarjima qilinadigan matnni qabul qilish va maqsad tilni tanlashni taklif qilish"""
    text_to_translate = message.text.strip()
    await state.update_data(text_to_translate=text_to_translate)
    await state.set_state(TranslateStates.waiting_for_language)

    preview = (text_to_translate[:150] + "...") if len(text_to_translate) > 150 else text_to_translate

    await message.answer(
        f"📝 *Matn qabul qilindi:*\n_«{preview}»_\n\n"
        "Qaysi tilga tarjima qilmoqchisiz? Quyidagi tillardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=get_translation_languages_keyboard(),
    )

@router.callback_query(TranslateStates.waiting_for_language, F.data.startswith("tr_lang:"))
async def process_translation_callback(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Til tanlanganda tarjimani amalga oshirish"""
    target_lang = callback.data.split(":")[1]
    data = await state.get_data()
    text_to_translate = data.get("text_to_translate")

    await callback.answer(f"{target_lang} tiliga tarjima qilinmoqda...")

    if not text_to_translate:
        await callback.message.edit_text("⚠️ Tarjima uchun matn topilmadi. Qaytadan urinib ko'ring.")
        await state.clear()
        return

    await bot.send_chat_action(chat_id=callback.message.chat.id, action="typing")
    loading_msg = await callback.message.answer(
        f"⏳ _{target_lang} tiliga tarjima tayyorlanmoqda..._",
        parse_mode="Markdown",
    )

    try:
        translated_text = await ai_service.translate(text=text_to_translate, target_language=target_lang)

        if not translated_text.startswith("⚠️"):
            await db.increment_ai_request_count(callback.from_user.id)

        await loading_msg.delete()
        
        result_header = f"🌐 *Tarjima natijasi ({target_lang} tilida):*\n\n"
        await send_chunked_message(callback.message, result_header + translated_text)

        await callback.message.answer(
            "Yana tarjima qilish uchun yangi matn yuborishingiz yoki asosiy menyuga qaytishingiz mumkin.",
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()

    except Exception as e:
        await loading_msg.delete()
        await callback.message.answer(f"⚠️ Tarjima jarayonida xatolik yuz berdi: {str(e)[:150]}")
        await state.clear()

@router.callback_query(TranslateStates.waiting_for_language, F.data == "tr_cancel")
async def cancel_translation_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Tarjimani bekor qilish"""
    await state.clear()
    await callback.answer("Tarjima bekor qilindi.")
    await callback.message.edit_text("❌ Tarjima bekor qilindi.")
    await callback.message.answer("Asosiy menyudasiz:", reply_markup=get_main_menu_keyboard())
