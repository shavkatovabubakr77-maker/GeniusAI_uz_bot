import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import ADMIN_IDS
from database import db
from keyboards.main_menu import (
    get_admin_keyboard,
    get_broadcast_confirm_keyboard,
    get_main_menu_keyboard,
    get_cancel_keyboard,
)
from states import AdminStates

logger = logging.getLogger(__name__)
router = Router()

def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish"""
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    """Admin paneli bosh menyusi"""
    await state.clear()
    user_id = message.from_user.id if message.from_user else 0

    if not is_admin(user_id):
        await message.answer("⛔️ Kechirasiz, sizda administrator huquqi mavjud emas.")
        return

    stats = await db.get_total_stats()

    admin_text = (
        "👑 *Genius AI — Administrator Paneli*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Foydalanuvchilar soni:* `{stats['total_users']}` nafar\n"
        f"🔘 *Jami buyruqlar:* `{stats['total_commands']}` ta\n"
        f"🤖 *Jami AI so‘rovlari:* `{stats['total_ai_requests']}` ta\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Boshqaruv tugmalaridan birini tanlang:"
    )

    await message.answer(
        text=admin_text,
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard(),
    )

@router.callback_query(F.data.in_(["admin_stats", "admin_refresh"]))
async def cb_admin_stats(callback: CallbackQuery) -> None:
    """Statistikani yangilash"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    stats = await db.get_total_stats()

    admin_text = (
        "👑 *Genius AI — Yangilangan Statistika*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Foydalanuvchilar soni:* `{stats['total_users']}` nafar\n"
        f"🔘 *Jami buyruqlar:* `{stats['total_commands']}` ta\n"
        f"🤖 *Jami AI so‘rovlari:* `{stats['total_ai_requests']}` ta\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Ma'lumotlar bazadan yangilandi."
    )

    try:
        await callback.message.edit_text(
            text=admin_text,
            parse_mode="Markdown",
            reply_markup=get_admin_keyboard(),
        )
    except Exception:
        pass
    await callback.answer("Statistika yangilandi!")

@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """Xabar tarqatish jarayonini boshlash"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_broadcast_message)
    await callback.answer()

    await callback.message.answer(
        "📢 *Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:*\n\n"
        "Xabar matn, rasm yoki formatlangan ko‘rinishda bo‘lishi mumkin. "
        "Yoki bekor qilish uchun «🔙 Asosiy menyu» tugmasini bosing.",
        parse_mode="Markdown",
        reply_markup=get_cancel_keyboard(),
    )

@router.message(AdminStates.waiting_for_broadcast_message)
async def process_broadcast_message_input(message: Message, state: FSMContext) -> None:
    """Tarqatiladigan xabarni saqlash va tasdiqlash so'rash"""
    if not is_admin(message.from_user.id):
        return

    # Xabar ma'lumotlarini saqlash
    await state.update_data(
        broadcast_chat_id=message.chat.id,
        broadcast_message_id=message.message_id,
    )
    await state.set_state(AdminStates.confirm_broadcast)

    await message.reply(
        "❓ *Ushbu xabarni haqiqatdan ham barcha foydalanuvchilarga yubormoqchimisiz?*",
        parse_mode="Markdown",
        reply_markup=get_broadcast_confirm_keyboard(),
    )

@router.callback_query(AdminStates.confirm_broadcast, F.data == "broadcast_confirm")
async def execute_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Tasdiqlangandan so'ng xabarni barcha foydalanuvchilarga yuborish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    data = await state.get_data()
    from_chat_id = data.get("broadcast_chat_id")
    msg_id = data.get("broadcast_message_id")

    await state.clear()
    await callback.message.edit_text("⏳ Xabarlarni tarqatish boshlandi...")

    user_ids = await db.get_all_user_ids()
    total = len(user_ids)
    success = 0
    failed = 0

    status_msg = await callback.message.answer(f"🚀 Yuborilmoqda: 0/{total}")

    for index, user_id in enumerate(user_ids, start=1):
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=from_chat_id,
                message_id=msg_id,
            )
            success += 1
        except Exception as e:
            failed += 1
            logger.debug(f"Foydalanuvchiga yuborib bo'lmadi ({user_id}): {e}")

        # Telegram FloodLimit cheklovini oldini olish
        await asyncio.sleep(0.05)

        # Har 20 ta xabarda progressni yangilash
        if index % 20 == 0 or index == total:
            try:
                await status_msg.edit_text(f"🚀 Yuborilmoqda: {index}/{total}")
            except Exception:
                pass

    report = (
        "✅ *Xabar tarqatish yakunlandi!*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Jami foydalanuvchilar:* {total}\n"
        f"✅ *Yetkazildi:* {success}\n"
        f"❌ *Yetkazilmadi (bloklangan):* {failed}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    await status_msg.edit_text(report, parse_mode="Markdown")
    await callback.message.answer("Asosiy menyu:", reply_markup=get_main_menu_keyboard())

@router.callback_query(AdminStates.confirm_broadcast, F.data == "broadcast_cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """Xabar tarqatishni bekor qilish"""
    await state.clear()
    await callback.answer("E'lon bekor qilindi.")
    await callback.message.edit_text("❌ E'lon yuborish bekor qilindi.")
    await callback.message.answer("Asosiy menyu:", reply_markup=get_main_menu_keyboard())
