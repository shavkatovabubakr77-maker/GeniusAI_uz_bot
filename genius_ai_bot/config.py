import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini loyiha katalogidan yuklash
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Adminlar ID ro'yxati (masalan: 12345,67890)
admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
ADMIN_IDS = [
    int(admin_id.strip())
    for admin_id in admin_ids_raw.split(",")
    if admin_id.strip().isdigit()
]

# AI sozlamalari
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").strip().lower()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

# Ma'lumotlar bazasi
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "genius_ai.db")).strip()
if not os.path.isabs(DATABASE_PATH):
    DATABASE_PATH = str(BASE_DIR / DATABASE_PATH)
