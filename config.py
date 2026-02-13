import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
AUTHOR_TG = os.getenv('AUTHOR_TELEGRAM', '@Aleksandr_Semeno')

# Города для поиска
CITIES = ['Набережные Челны', 'Нижнекамск', 'Елабуга', 'Менделеевск']

# Параметры поиска
MODELS = {
    'lada_granta': {
        'name': 'Lada Granta',
        'make': 21,
        'model': 4461,
        'max_price': 700000,
        'max_mileage': 100000,
        'years': [2018, 2019, 2020, 2021, 2022, 2023],
        'perspective_price': 600000
    },
    'lada_largus': {
        'name': 'Lada Largus',
        'make': 21,
        'model': 4518,
        'max_price': 800000,
        'max_mileage': 100000,
        'years': [2017, 2018, 2019, 2020, 2021, 2022],
        'perspective_price': 700000
    },
    'kia_rio': {
        'name': 'Kia Rio',
        'make': 34,
        'model': 6107,
        'max_price': 1200000,
        'max_mileage': 150000,
        'years': [2018, 2019, 2020, 2021, 2022, 2023],
        'perspective_price': 1000000
    }
}

CHECK_INTERVAL = 300  # 5 минут