from aiogram.fsm.state import State, StatesGroup

class ChatStates(StatesGroup):
    chatting = State()

class WritingStates(StatesGroup):
    waiting_for_topic = State()

class TranslateStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_language = State()

class CodingStates(StatesGroup):
    waiting_for_task = State()

class KnowledgeStates(StatesGroup):
    waiting_for_question = State()

class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()
    confirm_broadcast = State()
