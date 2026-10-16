# 🤖 Genius AI — O‘zbekcha Telegram AI Bot

**Genius AI** (`@GeniusAI_uz_bot`) — Python 3, `aiogram 3`, asinxron SQLite (`aiosqlite`) va zamonaviy Sun'iy Intellekt API (OpenAI / Gemini / Groq / DeepSeek) asosida yaratilgan, to'liq o'zbek tilida ishlovchi ko'p funksiyali Telegram AI bot.

---

## 🌟 Asosiy Imkoniyatlar

1. **🤖 AI bilan erkin suhbat:**
   - Har qanday savollarga to'liq o'zbek tilida tabiiy va aqlli javoblar.
   - Kontekstni eslab qolish (muloqot tarixi saqlanadi).
   - "🧹 Suhbatni tozalash" imkoniyati.
   - Uzun javoblarni Telegram chegarasiga (4096 belgi) moslab xavfsiz bo'lib yuborish.

2. **✍️ Matn yozish (Professional kopirayting):**
   - 📝 Insho va referatlar yozish
   - 📄 Rasmiy ariza va xatlar tayyorlash
   - 📢 Savdo va xizmatlar uchun reklama matnlari
   - 📱 Telegram kanallar uchun chiroyli postlar
   - 📖 Badiiy hikoyalar va tasvirlar
   - 🔍 Matnlarni tahrirlash va imlo xatolarini to‘g‘rilash

3. **🌐 Ko‘p tilli tarjima xizmati:**
   - O‘zbek, ingliz, rus, turk, nemis, arab, fransuz va ispan tillari orasida qulay va aniq tarjima.
   - Avval matn kiritiladi, so'ng qulay inline tugmalar orqali kerakli til tanlanadi.

4. **💻 Dasturlash yordamchisi (Senior Developer):**
   - Python, JavaScript, HTML/CSS, C++, SQL va boshqa dasturlash tillarida kod yozish.
   - Koddagi xatoliklarni topish va tushuntirish.
   - Chiroyli Markdown kod bloklari.

5. **📚 Bilimlar va savol-javob:**
   - Ilmiy, tarixiy, geografik, falsafiy va umumiy bilimlarga oid har qanday savolga ishonchli javob.

6. **👤 Foydalanuvchi profili va statistikasi:**
   - Foydalanuvchining shaxsiy ID, ro'yxatdan o'tgan sanasi, buyruqlari soni va AI so'rovlari hisobi.

7. **👑 Administrator paneli:**
   - Bot statistikasi: foydalanuvchilar soni, umumiy AI va buyruqlar hisobi.
   - Barcha foydalanuvchilarga xabar tarqatish (Broadcast) — tasdiqlash va tezkor hisobot tizimi bilan.
   - Faqat `.env` da belgilangan administratorlar kirishi mumkin.

---

## 📂 Loyiha Tuzilishi

```text
genius_ai_bot/
│
├── bot.py                  # Botni ishga tushirish asosiy fayli
├── config.py               # Sozlamalar va .env o'zgaruvchilarini yuklash
├── database.py             # SQLite (aiosqlite) asinxron ma'lumotlar bazasi
├── states.py               # FSM (Finite State Machine) holatlari
├── utils.py                # Uzun xabarlarni bo'lib yuborish va yordamchilar
│
├── handlers/               # Xabarlarni qabul qiluvchi handlerlar
│   ├── __init__.py
│   ├── start.py            # /start, /menu, /help va navigatsiya
│   ├── chat.py             # AI bilan suhbat va kontekst
│   ├── writing.py          # Matn yozish va tahrirlash
│   ├── translate.py        # Tarjima tizimi
│   ├── coding.py           # Dasturlash va savol-javob
│   ├── profile.py          # Shaxsiy profil va statistika
│   └── admin.py            # Admin boshqaruv paneli va broadcast
│
├── keyboards/              # Klaviaturashunoslik
│   ├── __init__.py
│   └── main_menu.py        # Barcha menyu, inline va reply tugmalar
│
├── services/               # Tashqi xizmatlar
│   ├── __init__.py
│   └── ai_service.py       # OpenAI va Gemini bilan integratsiya
│
├── requirements.txt        # Kerakli Python kutubxonalari
├── .env.example            # Konfiguratsiya namunasi
├── .gitignore              # Maxfiy va keraksiz fayllarni yashirish
└── README.md               # To'liq o'zbekcha qo'llanma
```

---

## 🔑 Kerakli Kalitlar (API Keys)

Bot to'liq ishlashi uchun sizga quyidagilar kerak:

1. **Telegram Bot Token:**
   - Telegramda [@BotFather](https://t.me/BotFather) ga kiring.
   - `/newbot` buyrug'ini yuboring va ko'rsatmalarga amal qilib yangi bot yarating.
   - Berilgan tokenni nusxalab oling (masalan: `7123456789:AAH...`).

2. **Admin Telegram ID:**
   - O'zingizning Telegram ID raqamingizni bilish uchun [@userinfobot](https://t.me/userinfobot) ga kiring.
   - Berilgan raqamni (masalan `123456789`) saqlab oling.

3. **AI API Kaliti (Quyidagilardan biri):**
   - **OpenAI API:** [platform.openai.com](https://platform.openai.com) dan API kalit oling (`sk-...`). *(Tavsiya etiladi: `gpt-4o-mini` modeli tez va juda arzon)*
   - **Google Gemini API:** [aistudio.google.com](https://aistudio.google.com) dan bepul Gemini API kalit oling (`AIzaSy...`).
   - *Yoki boshqa OpenAI-mos platformalar (Groq, DeepSeek, OpenRouter) orqali `OPENAI_BASE_URL` dan foydalanishingiz mumkin.*

---

## 💻 Windows Tizimida O'rnatish va Ishga Tushirish

### 1-qadam: Loyiha papkasiga o'ting

PowerShell yoki Buyruqlar qatorini (CMD) oching:

```powershell
cd c:\Users\LG\Desktop\TG_BOT\genius_ai_bot
```

### 2-qadam: Python virtual muhitini (venv) yaratish

```powershell
python -m venv venv
```

### 3-qadam: Virtual muhitni faollashtirish

PowerShell'da:
```powershell
.\venv\Scripts\Activate.ps1
```
*(Agar PowerShell'da script ishga tushirish taqiqlangan bo'lsa, avval ushbu buyruqni bering: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

Yoki CMD da:
```cmd
venv\Scripts\activate.bat
```

### 4-qadam: Kutubxonalarni o'rnatish

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 5-qadam: `.env` konfiguratsiya faylini sozlash

Namuna fayldan `.env` nusxasini yarating:

```powershell
copy .env.example .env
```

Endi `.env` faylini Notepad yoki VS Code orqali oching va o'z kalitlaringizni kiriting:

```env
BOT_TOKEN=7123456789:AAH...sizning_bot_tokeningiz
ADMIN_IDS=123456789
AI_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...sizning_openai_kalitingiz
OPENAI_MODEL=gpt-4o-mini
```

> **Eslatma:** Agar siz Google Gemini ishlatmoqchi bo'lsangiz:
> `AI_PROVIDER=gemini`
> `GEMINI_API_KEY=AIzaSy...` deb o'zgartiring.

### 6-qadam: Botni ishga tushirish! 🚀

```powershell
python bot.py
```

Konsolda quyidagi yozuv paydo bo'ladi:
```text
Genius AI Telegram Boti ishga tushirilmoqda...
SQLite ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.
Bot polling rejimida ish boshladi.
```

Endi Telegramda o'z botingizga kiring va **/start** buyrug'ini yuboring! 🎉

---

## 🛡️ Xavfsizlik Qoidalari

- `.env` faylida haqiqiy maxfiy kalitlar saqlanadi. Hech qachon uni GitHub yoki begonalarga yubormang.
- `.gitignore` fayliga `.env` va `genius_ai.db` kiritilgan, shuning uchun git push qilinganda maxfiy ma'lumotlar oshkor bo'lmaydi.
- Bot xatoliklari foydalanuvchiga xavfsiz tarzda yetkaziladi, serverning ichki xatolari va maxfiy ma'lumotlari ko'rsatilmaydi.
