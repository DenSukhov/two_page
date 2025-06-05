from config import logger
from callbacks.file_callbacks import register_file_callbacks
from callbacks.table_callbacks import register_table_callbacks
from callbacks.shift_callbacks import register_shift_callbacks
from callbacks.map_callbacks import register_map_callbacks

def register_callbacks(app):
    # Регистрация всех callback-функций
    logger.info("Начало регистрации callback'ов")
    register_file_callbacks(app)
    register_table_callbacks(app)
    register_shift_callbacks(app)
    register_map_callbacks(app)
    logger.info(f"Registered {len(app.callback_map)} callbacks")