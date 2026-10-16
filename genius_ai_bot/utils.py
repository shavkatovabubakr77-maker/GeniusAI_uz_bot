from aiogram.types import Message
import logging

logger = logging.getLogger(__name__)

async def send_chunked_message(message: Message, text: str, parse_mode: str = "Markdown") -> None:
    """
    Telegram xabar chegarasi (4096 belgi) bo'yicha matnni xavfsiz bo'lib yuborish.
    Markdown xatosi yuz berganda oddiy matn rejimiga o'tadi.
    """
    MAX_LENGTH = 3800
    if len(text) <= MAX_LENGTH:
        try:
            await message.answer(text, parse_mode=parse_mode)
        except Exception as e:
            logger.warning(f"Markdown parsing xatosi, oddiy matn ko'rinishida yuborilmoqda: {e}")
            await message.answer(text, parse_mode=None)
        return

    # Uzun matnni qismlarga ajratish
    chunks = []
    current_chunk = ""
    lines = text.split("\n")

    for line in lines:
        if len(current_chunk) + len(line) + 1 > MAX_LENGTH:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            # Agar bitta qatorning o'zi juda uzun bo'lsa
            while len(line) > MAX_LENGTH:
                chunks.append(line[:MAX_LENGTH])
                line = line[MAX_LENGTH:]
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line

    if current_chunk:
        chunks.append(current_chunk)

    for chunk in chunks:
        try:
            await message.answer(chunk, parse_mode=parse_mode)
        except Exception:
            await message.answer(chunk, parse_mode=None)
