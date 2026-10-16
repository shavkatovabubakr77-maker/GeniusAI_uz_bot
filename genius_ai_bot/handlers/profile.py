from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database import db
from keyboards.main_menu import get_main_menu_keyboard

router = Router()

@router.message(F.text == "👤 Mening profilim")
async def show_profile(message: Message, state: FSMContext) -> None:
    """Foydalanuvchi profili va statistikasini ko'rsatish"""
    await state.clear()
    user = message.from_user
    if not user:
        return

    await db.increment_command_count(user.id)
    profile = await db.get_user_profile(user.id)

    if not profile:
        profile, _ = await db.get_or_create_user(
            user_id=user.id,
            full_name=user.full_name,
            username=user.username,
        )

    full_name = profile.get("full_name", user.full_name)
    username = f"@{profile['username']}" if profile.get("username") else "Mavjud emas"
    registered_at = profile.get("registered_at", "Noma'lum")
    commands_count = profile.get("commands_count", 0)
    ai_requests_count = profile.get("ai_requests_count", 0)

    profile_text = (
        "👤 *Sizning profilingiz va statistikangiz*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 *Telegram ID:* `{user.id}`\n"
        f"👤 *Ism:* {full_name}\n"
        f"🔗 *Username:* {username}\n"
        f"📅 *Ro‘yxatdan o‘tgan sana:* `{registered_at}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔘 *Foydalanilgan buyruqlar:* {commands_count} ta\n"
        f"🤖 *AI so‘rovlari soni:* {ai_requests_count} ta\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Genius AI* xizmatidan faol foydalanayotganingiz uchun rahmat!"
    )

    await message.answer(
        text=profile_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard(),
    )
