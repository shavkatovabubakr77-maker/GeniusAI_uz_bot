import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import DATABASE_PATH

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self) -> None:
        """Ma'lumotlar bazasi jadvallarini yaratish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT NOT NULL,
                    username TEXT,
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    commands_count INTEGER DEFAULT 0,
                    ai_requests_count INTEGER DEFAULT 0
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                )
            """)

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_user 
                ON chat_history(user_id, id DESC)
            """)

            await db.commit()

    async def get_or_create_user(
        self, user_id: int, full_name: str, username: Optional[str]
    ) -> Tuple[Dict, bool]:
        """Foydalanuvchini olish yoki yangisini yaratish"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            row = await cursor.fetchone()

            if row:
                # Ism yoki usernameni yangilab qo'yish va last_active yangilash
                await db.execute(
                    """
                    UPDATE users 
                    SET full_name = ?, username = ?, last_active = ?
                    WHERE user_id = ?
                    """,
                    (full_name, username, now, user_id),
                )
                await db.commit()
                return dict(row), False
            else:
                await db.execute(
                    """
                    INSERT INTO users (user_id, full_name, username, registered_at, last_active, commands_count, ai_requests_count)
                    VALUES (?, ?, ?, ?, ?, 0, 0)
                    """,
                    (user_id, full_name, username, now, now),
                )
                await db.commit()
                return {
                    "user_id": user_id,
                    "full_name": full_name,
                    "username": username,
                    "registered_at": now,
                    "last_active": now,
                    "commands_count": 0,
                    "ai_requests_count": 0,
                }, True

    async def increment_command_count(self, user_id: int) -> None:
        """Buyruqlar sonini bittaga oshirish"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE users 
                SET commands_count = commands_count + 1, last_active = ?
                WHERE user_id = ?
                """,
                (now, user_id),
            )
            await db.commit()

    async def increment_ai_request_count(self, user_id: int) -> None:
        """AI so'rovlar sonini bittaga oshirish"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE users 
                SET ai_requests_count = ai_requests_count + 1, last_active = ?
                WHERE user_id = ?
                """,
                (now, user_id),
            )
            await db.commit()

    async def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Foydalanuvchi profil statistikasini olish"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_total_stats(self) -> Dict:
        """Admin paneli uchun umumiy statistika"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                total_users = (await cursor.fetchone())[0]

            async with db.execute("SELECT SUM(commands_count), SUM(ai_requests_count) FROM users") as cursor:
                row = await cursor.fetchone()
                total_commands = row[0] or 0
                total_ai_requests = row[1] or 0

            return {
                "total_users": total_users,
                "total_commands": total_commands,
                "total_ai_requests": total_ai_requests,
            }

    async def get_all_user_ids(self) -> List[int]:
        """Barcha foydalanuvchilar IDlarini olish (e'lon yuborish uchun)"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id FROM users")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def add_chat_message(self, user_id: int, role: str, content: str) -> None:
        """Suhbat tarixiga yangi xabar qo'shish"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content),
            )
            await db.commit()

    async def get_chat_history(self, user_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """Oxirgi N ta xabarni olish (xronologik tartibda)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT role, content FROM chat_history 
                WHERE user_id = ? 
                ORDER BY id DESC LIMIT ?
                """,
                (user_id, limit),
            )
            rows = await cursor.fetchall()
            # Teskari tartibda (eski -> yangi)
            return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    async def clear_chat_history(self, user_id: int) -> None:
        """Foydalanuvchi suhbat tarixini tozalash"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM chat_history WHERE user_id = ?",
                (user_id,),
            )
            await db.commit()

db = Database()
