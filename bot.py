import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from datetime import datetime

from config import BOT_TOKEN, MODELS, CHECK_INTERVAL, CITIES, AUTHOR_TG
from database import Database
from parser import AvitoParser

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

db = Database()
parser = AvitoParser()

user_states = {}

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🚗 Lada Granta", callback_data="monitor_grant"),
        InlineKeyboardButton("🚐 Lada Largus", callback_data="monitor_largus"),
        InlineKeyboardButton("🇰🇷 Kia Rio", callback_data="monitor_rio"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        InlineKeyboardButton("❓ Помощь", callback_data="help"),
        InlineKeyboardButton("📞 Связь с автором", url=f"https://t.me/{AUTHOR_TG.replace('@', '')}")
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name)
    
    welcome_text = f"""
👋 Привет, {user.first_name}!

Я бот для мониторинга свежих объявлений на Авито.
Отслеживаю автомобили в городах: {', '.join(CITIES)}

🔍 <b>Что отслеживаю:</b>
• Lada Granta (до 700 000 ₽, пробег до 100 000 км)
• Lada Largus (до 800 000 ₽, пробег до 100 000 км)
• Kia Rio (до 1 200 000 ₽, пробег до 150 000 км)

📢 <b>По вопросам и предложениям:</b> {AUTHOR_TG}

Выбери модель для отслеживания 👇
    """
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    help_text = f"""
❓ <b>Как пользоваться ботом:</b>

1️⃣ Выберите модель автомобиля
2️⃣ Выберите город
3️⃣ Ждите свежие объявления

💰 <b>Перспективные цены:</b>
• Granta (2018+) < 600 000 ₽
• Largus (2017+) < 700 000 ₽
• Rio (2020+) < 1 000 000 ₽

📍 <b>Города:</b>
• Набережные Челны
• Нижнекамск
• Елабуга
• Менделеевск

⚡️ <b>Совет:</b> Перспективные варианты уходят за 2-3 часа!

📬 <b>Связь с разработчиком:</b> {AUTHOR_TG}
    """
    await message.answer(help_text, reply_markup=get_main_keyboard())

# ... (остальной код bot.py из предыдущего сообщения, добавить импорт AUTHOR_TG)