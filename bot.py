import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

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

Я бот для мониторинга Avito.
Отслеживаю авто в городах: {', '.join(CITIES)}

🔍 <b>Модели:</b>
• Lada Granta (до 700 000 ₽, пробег до 100 000 км)
• Lada Largus (до 800 000 ₽, пробег до 100 000 км)
• Kia Rio (до 1 200 000 ₽, пробег до 150 000 км)

📬 <b>Автор:</b> {AUTHOR_TG}
    """
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    help_text = f"""
❓ <b>Как пользоваться:</b>

1️⃣ Выберите модель
2️⃣ Выберите город
3️⃣ Ждите объявления

💰 <b>Перспективные цены:</b>
• Granta < 600 000 ₽
• Largus < 700 000 ₽
• Rio < 1 000 000 ₽

📍 <b>Города:</b>
• Набережные Челны
• Нижнекамск
• Елабуга
• Менделеевск

📬 <b>Автор:</b> {AUTHOR_TG}
    """
    await message.answer(help_text, reply_markup=get_main_keyboard())

@dp.callback_query_handler(lambda c: c.data.startswith('monitor_'))
async def process_monitor(callback_query: types.CallbackQuery):
    model = callback_query.data.replace('monitor_', '')
    user_states[callback_query.from_user.id] = {'action': 'monitoring', 'model': model}
    
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "Выберите город:",
        reply_markup=get_city_keyboard()
    )

def get_city_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    for city in CITIES:
        keyboard.insert(InlineKeyboardButton(city, callback_data=f"city_{city}"))
    keyboard.add(InlineKeyboardButton("✅ Все города", callback_data="city_all"))
    return keyboard

@dp.callback_query_handler(lambda c: c.data.startswith('city_'))
async def process_city(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    city = callback_query.data.replace('city_', '')
    
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        user_id,
        f"✅ Мониторинг запущен!\nБуду присылать новые объявления каждые 5 минут.",
        reply_markup=get_main_keyboard()
    )
    
    if user_id in user_states:
        user_states[user_id]['city'] = city
        user_states[user_id]['active'] = True

@dp.callback_query_handler(lambda c: c.data == 'stats')
async def show_stats(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "📊 Статистика будет доступна в следующей версии",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query_handler(lambda c: c.data == 'help')
async def show_help(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await cmd_help(callback_query.message)

async def monitoring_loop():
    while True:
        try:
            users = db.get_all_users()
            if not users:
                await asyncio.sleep(CHECK_INTERVAL)
                continue
            
            for model_name, model_config in MODELS.items():
                listings = await parser.check_new_listings(model_name, model_config)
                
                for listing in listings:
                    db.add_listing(listing)
                    
                    for user_id in users:
                        if not db.was_sent_to_user(user_id, listing['id']):
                            await send_new_listing(user_id, listing)
                            db.mark_as_sent(user_id, listing['id'])
                            await asyncio.sleep(0.5)
                
                await asyncio.sleep(2)
            
        except Exception as e:
            logging.error(f"Ошибка: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)

async def send_new_listing(user_id, listing):
    price_text = f"{listing['price']:,} ₽".replace(',', ' ')
    mileage_text = f"{listing['mileage']:,} км".replace(',', ' ') if listing['mileage'] else 'Н/Д'
    
    perspective = "⚡️ ПЕРСПЕКТИВНО!" if listing['price'] < 600000 else "📌 Вариант"
    
    message = f"""
🚗 <b>{listing['title']}</b>
{perspective}

💰 Цена: <b>{price_text}</b>
📊 Пробег: {mileage_text}
📅 Год: {listing['year'] or 'Н/Д'}
📍 Город: {listing['city']}

🔗 <a href="{listing['url']}">Ссылка на объявление</a>
    """
    
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔗 Открыть", url=listing['url'])
    )
    
    try:
        await bot.send_message(user_id, message, reply_markup=keyboard)
    except:
        pass

async def on_startup(dp):
    asyncio.create_task(monitoring_loop())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)