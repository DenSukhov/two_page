import logging
import os

# Настройка логирования
logging.basicConfig(
    filename='dashboard.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Начальный ID для смен
next_shift_id = 1000

# Конфигурация иконок для карты
ICON_CONFIG = {
    'islands#yellowIcon': {'normal': 'assets/marker-icon-yellow.png', 'selected': 'assets/marker-icon-2x-gold.png'},
    'islands#redIcon': {'normal': 'assets/marker-icon-red.png', 'selected': 'assets/marker-icon-2x-red.png'},
    'islands#grayIcon': {'normal': 'assets/marker-icon-gray.png', 'selected': 'assets/marker-icon-2x-gray.png'},
    'islands#blueIcon': {'normal': 'assets/marker-icon-blue.png', 'selected': 'assets/marker-icon-2x-blue.png'},
    'islands#violetEducationIcon': {'normal': 'assets/marker-icon-violet.png', 'selected': 'assets/marker-icon-2x-violet.png'},
    'islands#graySportIcon': {'normal': 'assets/marker-icon-gray-sport.png', 'selected': 'assets/marker-icon-2x-gray-sport.png'},
    'islands#blueSportIcon': {'normal': 'assets/marker-icon-blue-sport.png', 'selected': 'assets/marker-icon-2x-blue-sport.png'}
}

# Маппинг эмодзи для товаров
EMOJI_MAPPING = {
    "фров": "🥦",
    "фрукты": "🥦",
    "холод": "🧀",
    "сухой": "🍱",
    "заморозка": "❄️",
    "промка": "🛠️",
    "алкоголь": "🍾"
}