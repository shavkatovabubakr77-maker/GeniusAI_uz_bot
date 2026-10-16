import logging
import aiohttp
from typing import List, Dict, Optional
import config

logger = logging.getLogger(__name__)

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

SYSTEM_PROMPT = (
    "Siz 'Genius AI' nomli zamonaviy, aqlli, odobli va professional sun'iy intellekt yordamchisisiz. "
    "Siz foydalanuvchilarning savollariga aniq, ravon va imkon qadar O'zbek tilida javob berasiz. "
    "Agar foydalanuvchi boshqa tilda murojaat qilsa, uning tiliga moslashishingiz mumkin, "
    "lekin asosiy tilingiz o'zbek tili. Javoblarni chiroyli va qulay formatda taqdim eting."
)

class AIService:
    def __init__(self):
        self.provider = config.AI_PROVIDER
        self.openai_client = None

        if self.provider == "openai" and HAS_OPENAI and config.OPENAI_API_KEY:
            kwargs = {"api_key": config.OPENAI_API_KEY}
            if config.OPENAI_BASE_URL:
                kwargs["base_url"] = config.OPENAI_BASE_URL
            self.openai_client = AsyncOpenAI(**kwargs)

    def is_configured(self) -> bool:
        """API kalit mavjudligini tekshirish"""
        if self.provider == "openai":
            return bool(config.OPENAI_API_KEY)
        elif self.provider == "gemini":
            return bool(config.GEMINI_API_KEY)
        return False

    async def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        """OpenAI orqali so'rov yuborish"""
        if not self.openai_client:
            if not config.OPENAI_API_KEY:
                return (
                    "⚠️ OpenAI API kaliti o'rnatilmagan!\n\n"
                    "Iltimos, bot ma'muri `.env` faylida `OPENAI_API_KEY` ni ko'rsatishi kerak."
                )
            kwargs = {"api_key": config.OPENAI_API_KEY}
            if config.OPENAI_BASE_URL:
                kwargs["base_url"] = config.OPENAI_BASE_URL
            self.openai_client = AsyncOpenAI(**kwargs)

        try:
            response = await self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL or "gpt-4o-mini",
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API xatosi: {e}")
            err_str = str(e).lower()
            if "authentication" in err_str or "invalid api key" in err_str or "401" in err_str:
                return "⚠️ Xatolik: AI API kaliti yaroqsiz yoki muddati o'tgan. Iltimos, administratorga xabar bering."
            elif "rate limit" in err_str or "429" in err_str:
                return "⚠️ Xatolik: AI so'rovlar limiti oshib ketdi yoki balans tugagan. Birozdan so'ng qayta urinib ko'ring."
            elif "connection" in err_str or "timeout" in err_str:
                return "⚠️ Xatolik: AI serveri bilan aloqa o'rnatib bo'lmadi. Internet yoki serverda uzilish bor."
            return f"⚠️ AI xizmatida xatolik yuz berdi: {str(e)[:200]}"

    async def _call_gemini(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Google Gemini REST API orqali tezkor va xavfsiz so'rov yuborish"""
        if not config.GEMINI_API_KEY:
            return (
                "⚠️ Gemini API kaliti o'rnatilmagan!\n\n"
                "Iltimos, bot ma'muri `.env` faylida `GEMINI_API_KEY` ni ko'rsatishi kerak."
            )

        model_name = config.GEMINI_MODEL or "gemini-3.5-flash-lite"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={config.GEMINI_API_KEY}"

        # Kontekst va xabarlar
        contents = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "temperature": 0.7,
            }
        }

        try:
            timeout = aiohttp.ClientTimeout(total=45)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as resp:
                    data = await resp.json()

                    if resp.status != 200:
                        error_msg = data.get("error", {}).get("message", "Noma'lum xatolik")
                        logger.error(f"Gemini API xatosi ({resp.status}): {error_msg}")
                        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
                            return "⚠️ Xatolik: Gemini API kaliti yaroqsiz. Iltimos, qaytadan tekshiring."
                        elif "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                            return "⚠️ Xatolik: Gemini so'rovlar limiti tugadi. Biroz kuting."
                        return f"⚠️ Gemini xizmatida xatolik: {error_msg[:180]}"

                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()

                    return "⚠️ Javob mazmuni bo'sh qaytdi."

        except aiohttp.ClientConnectorError:
            return "⚠️ Xatolik: Google serveriga ulanib bo'lmadi. Internet aloqasini tekshiring."
        except asyncio.TimeoutError:
            return "⚠️ Xatolik: So'rov vaqti tugadi (Timeout). Server juda sekin javob qaytardi."
        except Exception as e:
            logger.error(f"Gemini chaqiruvida xatolik: {e}")
            return f"⚠️ Gemini xizmatida xatolik yuz berdi: {str(e)[:200]}"

    async def chat(self, user_message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """AI bilan muloqot qilish (kontekst bilan)"""
        if not self.is_configured():
            return (
                "⚠️ AI xizmati sozlanmagan!\n\n"
                "Botda AI API kaliti o'rnatilmagan. Bot administratori `.env` faylida "
                "`OPENAI_API_KEY` yoki `GEMINI_API_KEY` ni kiritishi lozim.\n"
                "Soxta javob berilmaydi."
            )

        if self.provider == "gemini":
            return await self._call_gemini(user_message, history=history)

        # Default: OpenAI yoki OpenAI mos API
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            for item in history:
                role = "assistant" if item["role"] == "assistant" else "user"
                messages.append({"role": role, "content": item["content"]})
        messages.append({"role": "user", "content": user_message})

        return await self._call_openai(messages)

    async def generate_text(self, text_type: str, user_prompt: str) -> str:
        """Matn yaratish (insho, ariza, reklama va h.k.)"""
        prompts = {
            "essay": f"Quyidagi mavzuda sifatli, mazmunli insho yoki referat yozib ber: '{user_prompt}'. Tuzilishi: Kirish, asosiy qism, xulosa.",
            "letter": f"Quyidagi mavzuda rasmiy yoki norasmiy ariza / xat yozib ber: '{user_prompt}'. Rasmiy me'yorlarga va imloga to'liq amal qil.",
            "ad": f"Quyidagi mahsulot/xizmat uchun jalb qiluvchi reklama matni (kopirayting) yozib ber: '{user_prompt}'. Emojilar va kuchli chaqiriq (Call to action) qo'sh.",
            "post": f"Telegram kanali uchun quyidagi mavzuda chiroyli formatlangan, qiziqarli post tayyorlab ber: '{user_prompt}'. Emojilar va xeshteglar qo'sh.",
            "story": f"Quyidagi g'oya yoki mavzu bo'yicha qiziqarli hikoya yoki badiiy tavsif yozib ber: '{user_prompt}'.",
            "proofread": f"Quyidagi matnni tahrir qil, imlo, tinish belgilari va stilistik xatolarini to'g'irla. Avval tuzatilgan toza matnni, so'ng qilingan o'zgarishlar izohini ko'rsat:\n\n{user_prompt}",
        }

        full_prompt = prompts.get(
            text_type,
            f"Quyidagi mavzuda professional matn yozib ber: '{user_prompt}'."
        )

        return await self.chat(full_prompt)

    async def translate(self, text: str, target_language: str) -> str:
        """Matnni ko'rsatilgan tilga tarjima qilish"""
        prompt = (
            f"Quyidagi matnni {target_language} tiliga aniq, tabiiy va ravon tarjima qil. "
            f"Faqat tarjimaning o'zini qaytar (ortiqcha kirish so'zlarsiz):\n\n{text}"
        )
        return await self.chat(prompt)

    async def coding_assistance(self, task: str) -> str:
        """Dasturlash bo'yicha yordam (kod yozish, tushuntirish, xatolarni tuzatish)"""
        prompt = (
            f"Siz tajribali Senior dasturchisiz. Quyidagi dasturlash topshirig'i yoki kodi bo'yicha yordam bering:\n\n"
            f"{task}\n\n"
            f"Talablar: Kodlarni chiroyli Markdown formatida (```til ...) keltiring, "
            f"xatolarni aniqlab tushuntiring va eng yaxshi amaliyotlarni (best practices) tavsiya qiling."
        )
        return await self.chat(prompt)

    async def qa_knowledge(self, question: str) -> str:
        """Ilmiy, umumiy va ensiklopedik savollarga javob"""
        prompt = (
            f"Quyidagi savolga ilmiy va ishonchli manbalarga tayangan holda batafsil va tushunarli javob bering:\n\n"
            f"Savol: {question}"
        )
        return await self.chat(prompt)

ai_service = AIService()
