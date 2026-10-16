from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# 1. Asosiy Menyu Klaviaturasi
def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="🤖 AI bilan suhbat"),
            KeyboardButton(text="✍️ Matn yozish"),
        ],
        [
            KeyboardButton(text="🌐 Tarjima qilish"),
            KeyboardButton(text="💻 Kod yozishda yordam"),
        ],
        [
            KeyboardButton(text="📚 Bilimlar va savol-javob"),
            KeyboardButton(text="👤 Mening profilim"),
        ],
        [
            KeyboardButton(text="ℹ️ Yordam"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Quyidagi bo'limlardan birini tanlang...",
    )

# 2. AI bilan suhbat rejimidagi klaviatura
def get_chat_mode_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="🧹 Suhbatni tozalash"),
            KeyboardButton(text="🔙 Asosiy menyu"),
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Savolingizni yozing...",
    )

# 3. Matn yozish bo'limi menyusi
def get_writing_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="📝 Insho va referat"),
            KeyboardButton(text="📄 Ariza va xat"),
        ],
        [
            KeyboardButton(text="📢 Reklama matni"),
            KeyboardButton(text="📱 Telegram post"),
        ],
        [
            KeyboardButton(text="📖 Hikoya va tavsif"),
            KeyboardButton(text="🔍 Imlo va tahrir"),
        ],
        [
            KeyboardButton(text="🔙 Asosiy menyu"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Matn turini tanlang...",
    )

# 4. Bekor qilish / Asosiy menyuga qaytish klaviaturasi
def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🔙 Asosiy menyu")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Matnni yuboring yoki bekor qiling...",
    )

# 5. Tarjima tillari inline klaviaturasi
def get_translation_languages_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data="tr_lang:O'zbek"),
            InlineKeyboardButton(text="🇬🇧 Ingliz tili", callback_data="tr_lang:Ingliz"),
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Rus tili", callback_data="tr_lang:Rus"),
            InlineKeyboardButton(text="🇹🇷 Turk tili", callback_data="tr_lang:Turk"),
        ],
        [
            InlineKeyboardButton(text="🇩🇪 Nemis tili", callback_data="tr_lang:Nemis"),
            InlineKeyboardButton(text="🇸🇦 Arab tili", callback_data="tr_lang:Arab"),
        ],
        [
            InlineKeyboardButton(text="🇫🇷 Fransuz tili", callback_data="tr_lang:Fransuz"),
            InlineKeyboardButton(text="🇪🇸 Ispan tili", callback_data="tr_lang:Ispan"),
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="tr_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 6. Admin paneli inline klaviaturasi
def get_admin_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📊 Umumiy statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="📢 Xabar tarqatish", callback_data="admin_broadcast"),
        ],
        [
            InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin_refresh"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 7. Xabar tarqatishni tasdiqlash klaviaturasi
def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="✅ Yuborish", callback_data="broadcast_confirm"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
