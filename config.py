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